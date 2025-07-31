from cugraph import Graph
from pathlib import Path
import multiprocessing as mp
from rdflib.util import guess_format
import lightning as L
import torch
from torch.utils.data import TensorDataset, DataLoader, Dataset
from torch.utils.dlpack import to_dlpack
from lightning.pytorch.tuner import Tuner
from .helper.functions import get_gpu_cluster, determine_optimal_chunksize, _generate_vocab
from .embedders.word2vec import SkipGram, CBOW
from .embedders.word2vec_loader import SkipGramDataModule, CBOWDataModule
from .reader.kg_reader import read_kg_file
from .corpus.walk_corpus import single_gpu_walk_corpus, multi_gpu_walk_corpus
import cudf
import dask_cudf
from loguru import logger

class GPU_RDF2Vec:
    def __init__(self, walk_strategy: str, walk_depth: int, walk_number: int, embedding_model: str,
                 epochs: int, batch_size: int, vector_size: int, window_size: int, min_count: int,
                 negative_samples: int, learning_rate: int, random_state: int, reproducible: bool,
                 multi_gpu: bool, generate_artifact: bool, cpu_count: int):
        """GPU‑accelerated implementation of the RDF2Vec pipeline.

        This class wraps every step that is necessary to obtain dense vector
        representations for entities in a (potentially very large) knowledge
        graph on the GPU:

        1. **Load the triples** into a cuGraph `Graph`, optionally persisting
        intermediate artefacts.
        2. **Generate random walks** (or, in the future, BFS walks) that serve as a
        textual corpus.
        3. **Train a Word2Vec model** (currently Skip‑gram, CBOW forthcoming) on
        this corpus with all heavy‐lifting—negative sampling, matrix ops, CUDA
        kernels—performed on the GPU and orchestrated through PyTorch Lightning.
        4. **Export the learned embeddings** back to cuDF for further downstream
        analytics or as Parquet artefacts.


        Args:
            walk_strategy (str): {"random", "bfs"}
                How to sample walks from the graph.
            walk_depth (int): 
                Maximum length of every walk.
            walk_number (int): 
                Number of walks to start **per start vertex** (Relevant for random walk)
            embedding_model (str): {"skipgram", "cbow"}
                Variant of Word2Vec to train
            epochs (int): 
                Training epochs for the Word2Vec model
            batch_size (int): 
                Mini-batch size used by the Pytorch DataLoader
            vector_size (int): 
                Dimensionality of the output embeddings
            window_size (int): 
                Context window size in tokens
            min_count (int): 
                Ignore tokens that appear fewer than this number of times when building the vocabulary
            negative_samples (int): 
                Number of negative samples in the negative-sampling loss
            learning_rate (int): 
                Learning rate for the optimiser
            random_state (int): 
                Seed for deterministic sampling operations
            reproducible (bool): 
                Turn on all Pytorch/ CUDA deterministic flags **at the cost of speed**
            multi_gpu (bool): 
                If true, Dask CUDA cluster for multi-gpu training
            generate_artifact (bool): 
                Persist word2idx and embedding matrices as Parquet artefacts under provided directory
            cpu_count (int): 
                Number of cpu workers that feed the GPU via the DataLoader

        Attributes
        ----------
        knowledge_graph : cugraph.Graph
            Directed graph that stores the integer‑encoded triples.
        word2vec_model : torch.nn.Module or None
            Trained model after `fit`; ``None`` before.
        word2idx : cudf.DataFrame or None
            Two‑column mapping *token* → *word*; available after
            `load_data`.
        generate_artifact : bool
            Copied from the constructor.
        cpu_count : int
            Copied from the constructor.

        Raises
        ------
        NotImplementedError
            If a not‑yet‑supported walk strategy, embedding model is specified.
        ValueError
            If an unsupported file format is passed to `load_data` or if
            `transform` is called prior to `fit`.

        Examples
        --------
        >>> rdf2vec = GPU_RDF2Vec(
        ...     walk_strategy="random",
        ...     walk_depth=4,
        ...     walk_number=10,
        ...     embedding_model="skipgram",
        ...     epochs=5,
        ...     batch_size=2**14,
        ...     vector_size=256,
        ...     window_size=5,
        ...     min_count=1,
        ...     negative_samples=5,
        ...     learning_rate=0.025,
        ...     random_state=42,
        ...     reproducible=True,
        ...     multi_gpu=False,
        ...     generate_artifact=False,
        ...     cpu_count=4,
        ... )
        >>> edges = rdf2vec.load_data("example.parquet")
        >>> rdf2vec.fit(edges)
        >>> emb_df = rdf2vec.transform()
        >>> emb_df.head()
        
        """
        # Initialize class variables
        # Walk strategy parameters
        self.walk_strategy = walk_strategy
        self.walk_depth = walk_depth
        self.walk_number = walk_number
        # Word2Vec parameters
        self.embedding_model = embedding_model
        self.epochs = epochs
        self.batch_size = batch_size
        self.vector_size = vector_size
        self.window_size = window_size
        self.negative_samples = negative_samples
        self.min_count = min_count
        self.random_state = random_state
        self.reproducible = reproducible
        self.multi_gpu = multi_gpu
        self.learning_rate = learning_rate
        # Initialize the GPU cluster if multi_gpu is True
        if multi_gpu:
            get_gpu_cluster()
        # Initialize the cugraph graph
        self.knowledge_graph = Graph(directed=True)
        self.generate_artifact = generate_artifact
        self.word2vec_model = None
        self.word2idx = None
        self.cpu_count = cpu_count

    def load_data(self, path: str) -> cudf.DataFrame:
        """
        Load a triple file, build the token vocabulary, and populate the internal
        cuGraph instance.

        The method chooses the most efficient cuDF reader based on the file
        extension (`.parquet`, `.csv`, `.txt`, `.nt`).  If the extension is not
        one of these, it attempts to infer any other RDF serialisation via
        `rdflib.util.guess_format` and falls back to a generic
        ``rdflib`` reader.  After reading, the triples are integer‑encoded, a
        ``word2idx`` mapping is created (and optionally persisted), and the
        resulting edge list is loaded into `self.knowledge_graph`.

        Parameters
        ----------
        path : str
            Path to the knowledge‑graph file.  Supported formats:

            * ``.parquet`` – three‑column Parquet file *(subject, predicate, object)*  
            * ``.csv`` – comma‑separated triples without header  
            * ``.txt`` – whitespace‑separated triples without header  
            * ``.nt`` – N‑Triples (parsed with cuDF CSV reader and cleaned)  
            * any other RDF serialisation recognised by
                `rdflib.util.guess_format`

        Returns
        -------
        cudf.DataFrame
            Three‑column cuDF DataFrame whose ``subject``, ``predicate``, and
            ``object`` are *int32* tokens.  The DataFrame is also stored as a
            directed edge list in `self.knowledge_graph`.

        Raises
        ------
        ValueError
            If the file extension is unsupported **and** `rdflib` cannot guess
            the RDF format.

        Notes
        -----
        * Builds a vocabulary with `_generate_vocab` and stores it in
            `self.word2idx`.
        * Persists ``word2idx`` as Parquet under *./vector/* when
            ``self.generate_artifact`` is ``True``.
        * Returns the int‑encoded edge list for downstream use (e.g.,
            a`fit`).
        
        """
        
        file_path = Path(path)
        file_ending = file_path.suffix
        if file_ending == ".parquet":
            if self.multi_gpu:
                kg_data = dask_cudf.read_parquet(path, columns=["subject", "predicate", "object"])
            else:
                kg_data = cudf.read_parquet(path, columns=["subject", "predicate", "object"])
        elif file_ending == ".csv":
            if self.multi_gpu:
                kg_data = dask_cudf.read_csv(path, names=["subject", "predicate", "object"], header=None)
            else:
                kg_data = cudf.read_csv(path, names=["subject", "predicate", "object"], header=None)
        elif file_ending == ".txt":
            if self.multi_gpu:
                kg_data = dask_cudf.read_csv(path, sep=" ", names=["subject", "predicate", "object"], header=None)
            else:
                kg_data = cudf.read_text(path, names=["subject", "predicate", "object"])
        # In order to read the .nt file we will use the csv reader extension and clean up the data
        elif file_ending == ".nt":
            if self.multi_gpu:
                kg_data = dask_cudf.read_csv(path, sep=" ", names=["subject", "predicate", "object", "dot"], header=None)
            else:
                kg_data = cudf.read_csv(path, sep=" ", names=["subject", "predicate", "object"], header=None)
            kg_data = kg_data.drop(["dot"], axis=1)
            kg_data["subject"] = kg_data["subject"].str.strip().str.replace("<", "").str.replace(">", "")
            kg_data["predicate"] = kg_data["predicate"].str.strip().str.replace("<", "").str.replace(">", "")
            kg_data["object"] = kg_data["object"].str.strip().str.replace("<", "").str.replace(">", "")
        else:
            # Use rdflib to provide a support for general purpose RDF formats and return the kg as a tuple
            if self.multi_gpu:
                raise ValueError(f"Multi-GPU support is not enabled for the file format: {file_ending}. Please consider one of the supported multi gpu formats: .parquet, .csv, .txt, .nt")
            kg_format = guess_format(path)
            if kg_format:
                kg_tuple = read_kg_file(path)
                kg_data = cudf.DataFrame(kg_tuple, columns=["subject", "object", "predicate"])
            else:
                raise ValueError(f"Unsupported file format: {file_ending}. Please consider either a valid RDF format or a .parquet, .csv, .txt file.")
        tokenization, word = _generate_vocab(kg_data, self.multi_gpu)
        if self.multi_gpu:
            word2idx = dask_cudf.concat([dask_cudf.Series(tokenization), dask_cudf.Series(word)], axis=1)
        else:
            word2idx = cudf.concat([cudf.Series(tokenization), cudf.Series(word)], axis=1)
        word2idx.columns = ["token", "word"]
        if self.generate_artifact:
            word2idx.to_parquet(f"vector/word2idx_{file_path.stem}.parquet", index=False)
        self.word2idx = word2idx
        kg_data["subject"] = kg_data.merge(word2idx, left_on="subject", right_on="word", how="left")["token"]
        kg_data["predicate"] = kg_data.merge(word2idx, left_on="predicate", right_on="word", how="left")["token"]
        kg_data["object"] = kg_data.merge(word2idx, left_on="object", right_on="word", how="left")["token"]
        kg_data = kg_data.astype("int32")
        # Load the edge list into the graph
        if self.multi_gpu:
            self.knowledge_graph.from_dask_cudf_edgelist(kg_data, source='subject', destination='object', edge_attr='predicate', renumber=False)
        else:
            self.knowledge_graph.from_cudf_edgelist(kg_data, source='subject', destination='object', edge_attr='predicate', renumber=False)
        return kg_data

    def fit(self, edge_df: cudf.DataFrame, walk_vertices: cudf.Series = None) -> None:
        """
        Train a Word2Vec model on random-walk sequences generated from the
        knowledge graph.

        The method performs three high-level steps:

        1. **Generate walks** – Uses the configured ``walk_strategy``
        to obtain (center, context) pairs that mimic natural-language contexts.
        2. **Build the training data set** – Converts the pairs to PyTorch
        tensors and wraps them in a performant `TensorDataset`/`DataLoader`.
        3. **Optimize the embedding model** – Instantiates the requested
        Word2Vec variant, then fits it with a
        PyTorch Lightning `Trainer`.

        Parameters
        ----------
        edge_df : cudf.DataFrame
            Int-encoded edge list with columns ``subject``, ``predicate``,
            ``object``—typically the output of `load_data`.
        walk_vertices : cudf.Series or None, default None
            Optional subset of starting vertices from which to launch random
            walks. If None, all vertices in ``self.knowledge_graph`` are used.

        Raises
        ------
        ValueError
            If an invalid ``walk_strategy`` is supplied.

       Notes
       -----
       - Walks are repeated ``self.walk_number`` times and have maximum depth ``self.walk_depth``.
       - Skip-gram training uses negative sampling with ``self.negative_samples`` negatives per positive pair.
       - The trained model is stored in ``self.word2vec_model`` and can subsequently be exported via ``transform``.
       
        Examples
        --------
        >>> edges = rdf2vec.load_data("example.parquet")
        >>> rdf2vec.fit(edges)
        """

        if self.multi_gpu:
            walk_instance = multi_gpu_walk_corpus(self.knowledge_graph)
        else:
            walk_instance = single_gpu_walk_corpus(self.knowledge_graph)
        if self.walk_strategy == "random":
            if walk_vertices is None:
                walk_vertices = self.knowledge_graph.nodes()
            walk_vertices = walk_vertices.repeat(self.walk_number)
            walk_corpus = walk_instance.random_walk(
                edge_df=edge_df,
                walk_vertices=walk_vertices,
                walk_depth=self.walk_depth,
                random_state=self.random_state,
                word2vec_model=self.embedding_model,
                min_count=self.min_count
            )
        elif self.walk_strategy == "bfs":
            if walk_vertices is None:
                walk_vertices = self.knowledge_graph.nodes()
            walk_corpus =  walk_instance.bfs_walk(
                edge_df=edge_df,
                walk_vertices=walk_vertices,
                walk_depth=self.walk_depth,
                random_state=self.random_state,
                word2vec_model=self.embedding_model,
                min_count=self.min_count
            )
        else:
            raise ValueError(f"Unsupported walk strategy: {self.walk_strategy}. Please choose either 'random' or 'bfs'.")
        
        
        if self.embedding_model == "skipgram":
            word2vec_model = SkipGram(
                vocab_size = self.word2idx.shape[0],
                embedding_dim=self.vector_size,
                neg_samples=self.negative_samples,
                learning_rate=self.learning_rate
            )
            center_tensor = torch.utils.dlpack.from_dlpack(walk_corpus['center'].to_dlpack()).contiguous()
            context_tensor = torch.utils.dlpack.from_dlpack(walk_corpus['context'].to_dlpack()).contiguous()
            datamodule = SkipGramDataModule(center_tensor=center_tensor, context_tensor=context_tensor, batch_size=self.batch_size if self.batch_size else round(len(context_tensor)/(self.cpu_count)))

        else:
            word2vec_model = CBOW(
                vocab_size = self.word2idx.shape[0],
                embedding_dim=self.vector_size,
                learning_rate=self.learning_rate,
            )
            center_tensor = torch.utils.dlpack.from_dlpack(walk_corpus['center'].to_dlpack()).contiguous()
            context_tensor = torch.utils.dlpack.from_dlpack(walk_corpus['context'].to_dlpack()).contiguous()
        
        # word2vec_model = torch.compile(word2vec_model) -> Stabalize model compilation for speedup
        if self.reproducible:
            logger.info("Setting up reproducible training, might increase training time.")
            L.seed_everything(self.random_state, workers=True)
        trainer = L.Trainer(max_epochs=self.epochs, log_every_n_steps=1, accelerator="gpu", precision=16, devices=1)
        tune_batch_size = True
        if tune_batch_size:
            tuner = Tuner(trainer)
            tuner.scale_batch_size(word2vec_model, mode="power", datamodule=datamodule, steps_per_trial=1, init_val=round(len(context_tensor)/(self.cpu_count*2)), max_trials=12)
        trainer.fit(word2vec_model, datamodule)

        self.word2vec_model = word2vec_model

    def transform(self) -> cudf.DataFrame:
        """
        Convert the learned Word2Vec parameters into a cuDF table of
        entity‑level embeddings.

        The method fetches the trained embedding matrix
        (shape ``[vocab_size, vector_size]``), converts it from the PyTorch
        tensor on the GPU into a cuDF DataFrame, and concatenates it with the
        ``word2idx`` mapping so every row contains

        * ``token`` – integer ID  
        * ``word`` – original IRI / literal  
        * ``embedding_0 … embedding_{vector_size‑1}`` – float32 components

        When `self.generate_artifact` is *True*, the resulting table is also
        written to *./vector/embeddings_<model‑hash>.parquet*.

        Returns
        -------
        cudf.DataFrame
            A ``(vocab_size × (vector_size + 2))`` DataFrame with the mapping
            and embeddings.

        Raises
        ------
        ValueError
            If called before `fit` (no trained model) **or**
            `load_data` (no ``word2idx`` vocabulary).

        Notes
        -----
        The method is a pure transformation; it never mutates the underlying
        Word2Vec parameters.  Use it to obtain fresh snapshots after each
        training run.

        """
        # Check if model is fitted and word2idx is available
        if self.word2vec_model is not None and self.word2idx is not None:
            model_embeddings = self.word2vec_model.in_embeddings.weight
            model_embeddings_df = cudf.from_dlpack(to_dlpack(model_embeddings.T)).T
            model_embeddings_df.columns = model_embeddings_df.columns.astype(str)
            model_embeddings_df = model_embeddings_df.add_prefix("embedding_")
            embedding_df = cudf.concat([self.word2idx, model_embeddings_df], axis=1)
            if self.generate_artifact:
                embedding_df.to_parquet(f"vector/embeddings_{self.word2vec_model}.parquet", index=False)
            return embedding_df
        else:
            raise ValueError("The transform method is not possible to call without a fitted model or a generated word2idx setup." \
            "Please call the 'fit' method first or the 'load_data' method to generate the word2idx setup.")


    def fit_transform(self, edge_df: cudf.DataFrame, walk_vertices: cudf.DataFrame) -> cudf.DataFrame:
        """
        Train the Word2Vec model **and** immediately return the resulting
        embeddings.

        This convenience wrapper simply calls `fit` followed by
        `transform`.  Use it when you do **not** need to inspect the
        model object itself and only care about the final entity vectors.

        Parameters
        ----------
        edge_df : cudf.DataFrame
            Int‑encoded triples that define the knowledge graph (typically the
            output of `load_data`).
        walk_vertices : cudf.Series or None, default ``None``
            Optional subset of start vertices for walk generation; see
            a`fit` for semantics.

        Returns
        -------
        cudf.DataFrame
            The concatenated ``word2idx``–embedding table produced by
            a`transform`.

        Notes
        -----
        - All exceptions raised by a`fit` or a`transform`
          propagate unchanged.
        - The trained model is still stored in
          `self.word2vec_model` for later re‑use.

        """
        self.fit(edge_df, walk_vertices)
        embedding_df = self.transform()
        return embedding_df
    