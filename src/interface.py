from .utils import get_files, save_file, preprocess_append
from .config import (
    VLLM_FILE,
    BM_ALL,
    BM_MD,
    BM_PY,
    OUTPUT_CHUNK,
    OUTPUT_CODE_SET,
    OUTPUT_DOC_SET,
    STOPWORDS,
    UNANSWER_DOCS,
    UNANSWER_CODE,
)
from .index import py_chunking, md_chunking
from .search import gather_data_set, process_data_set, save_search
from .bm25 import bm_tokeniser
from .config import OUTPUT_ANSWER, MODEL_NAME
from .answer import get_answer, answer_data_set
from .evaluate import find_recall_metric
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any
import json
import bm25s  # type: ignore[import-untyped]
import os
from tqdm import tqdm


class Cli(object):
    def index(
        self,
        chunk_size: int | None = None,
        max_chunk_size: int | None = None,
    ) -> None:
        """Indexation and chunking of all the vllm file.

        Args:
            self: self.
            chunk_size: limit of the char max in a chunk.
            max_chunk_size: alternate CLI-compatible argument name.

        Returns:
            None but save the index and data of the bm25.
        """
        effective_chunk_size = chunk_size
        if effective_chunk_size is None:
            effective_chunk_size = max_chunk_size
        if effective_chunk_size is None:
            effective_chunk_size = 1000

        if effective_chunk_size < 250 or effective_chunk_size > 2000:
            raise ValueError(
                "wrong max chunk size,"
                + "please try between 250 and 2000"
            )
        lst_files = get_files(VLLM_FILE)
        py_chunk: list[Any] = []
        md_chunk: list[Any] = []
        for file in tqdm(
            lst_files,
            desc="chunking files...",
            bar_format="{desc} {bar} {percentage:.0f}%",
        ):
            if file.endswith(".py"):
                py_chunk.extend(py_chunking(file, effective_chunk_size))
            elif file.endswith(".md"):
                md_chunk.extend(md_chunking(file, effective_chunk_size))
        save_file(py_chunk, md_chunk)
        bm_tokeniser(md_chunk, py_chunk)

    def search(self, query: str, k: int = 5) -> None:
        """searching the right chunk for the query given.

        Args:
            self: self.
            query: question given.
            k: number of chunk for the query.

        Returns:
            None but save the chunk found with the query.
        """
        if k < 1 or k > 10:
            print("Please use k between 1 and 10.")
            return
        if not os.path.exists(BM_ALL):
            print("Please use the command index before")
            return
        retriever = bm25s.BM25.load(BM_ALL, load_corpus=True)
        query_token = bm25s.tokenize(
            [preprocess_append(query)], stopwords=STOPWORDS
        )
        results, scores = retriever.retrieve(query_token, k=k)
        # Avoid ambiguous truth-value checks for lists/NumPy arrays
        if results is None or (
            hasattr(results, "__len__") and len(results) == 0
        ) or (hasattr(results, "size") and getattr(results, "size") == 0):
            print("No results found for the query.")
            return
        question = [{"question": query}]
        res_chunk = save_search(results[0])
        question.extend(res_chunk)
        with open(OUTPUT_CHUNK, "w") as f:
            f.write(json.dumps(question, ensure_ascii=False, indent=4))

    def search_dataset(
        self,
        dataset_path: str,
        save_directory: str,
        k: int = 5,
    ) -> None:
        """searching the right chunk for a dataset.

        Args:
            self: self.
            dataset_path: path to the unanswered dataset JSON.
            save_directory: folder where search outputs are saved.
            k: number of chunk for the query.

        Returns:
            None but save the student search results to the given directory.
        """
        if k < 1 or k > 10:
            print("Please use k between 1 and 10.")
            return
        if not os.path.exists(dataset_path):
            print(f"Dataset path not found: {dataset_path}")
            return
        if not os.path.exists(BM_PY) or not os.path.exists(BM_MD):
            print("Please use the command index before")
            return

        dataset = gather_data_set(dataset_path)
        dataset_name = os.path.basename(dataset_path).lower()
        if "doc" in dataset_name:
            retriever = bm25s.BM25.load(BM_MD, load_corpus=True)
            chunk_type = "doc"
        elif "code" in dataset_name:
            retriever = bm25s.BM25.load(BM_PY, load_corpus=True)
            chunk_type = "code"
        else:
            retriever = bm25s.BM25.load(BM_ALL, load_corpus=True)
            chunk_type = "all"

        out_name = f"search_results_{chunk_type}_{dataset_name}.json"
        output_path = os.path.join(save_directory, out_name)
        process_data_set(dataset, retriever, k, output_path, chunk_type)

    search_data_set = search_dataset

    def answer(self, query: str, k: int = 5) -> None:
        """Take the query, retrieve relevant chunks, and answer with a llm.

        Args:
            self: self.
            query: question given.
            k: number of chunks to retrieve.

        Returns:
            None but print the answer and save it to OUTPUT_ANSWER.
        """
        if k < 1 or k > 10:
            print("Please use k between 1 and 10.")
            return
        self.search(query, k)
        try:
            with open(OUTPUT_CHUNK, "r") as data:
                chunk = json.load(data)
        except FileNotFoundError:
            print("Please use the command search before")
            return

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        result = get_answer(tokenizer, model, chunk)
        with open(OUTPUT_ANSWER, "w") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=4))
        print(result)

    def answer_data_set(self) -> None:
        """Take the query in data_set and chunk find in search and answer
        it with a llm.

        Args:
            self: self.

        Returns:
            None but save the answer with the chunk find and query.
        """
        if (
            not os.path.exists(OUTPUT_DOC_SET)
            or not os.path.exists(OUTPUT_CODE_SET)
        ):
            print("Please use the command search_dataset before")
            return
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        answer_data_set(tokenizer, model)

    def evaluate(self) -> None:
        with open(OUTPUT_DOC_SET, "r") as f:
            data = json.load(f)

        k = data["k"]
        order = list(range(1, k + 1))

        print("--- DOCS ---")
        doc_results = []
        for val in order:
            doc_results.append(
                find_recall_metric(
                    "data/public/AnsweredQuestions/dataset_docs_public.json",
                    OUTPUT_DOC_SET,
                    val,
                )
            )
        for i, result in enumerate(doc_results):
            print(f"k@{order[i]} ; {int(result * 100)}% ({result})")

        print("--- CODE ---")
        code_results = []
        for val in order:
            code_results.append(
                find_recall_metric(
                    "data/public/AnsweredQuestions/dataset_code_public.json",
                    OUTPUT_CODE_SET,
                    val,
                )
            )
        for i, result in enumerate(code_results):
            print(f"k@{order[i]} ; {int(result * 100)}% ({result})")

    def run_all(self, chunk_size: int) -> None:
        """Run indexing, retrieval on public datasets, and evaluation."""
        self.index(chunk_size)

        if not os.path.exists(BM_PY) or not os.path.exists(BM_MD):
            print("Please use the command index before running run_all.")
            return

        retriever_py = bm25s.BM25.load(BM_PY, load_corpus=True)
        code_dataset = gather_data_set(UNANSWER_CODE)
        process_data_set(
            code_dataset,
            retriever_py,
            10,
            OUTPUT_CODE_SET,
            chunk_type="code",
        )

        retriever_md = bm25s.BM25.load(BM_MD, load_corpus=True)
        doc_dataset = gather_data_set(UNANSWER_DOCS)
        process_data_set(
            doc_dataset,
            retriever_md,
            10,
            OUTPUT_DOC_SET,
            chunk_type="doc",
        )

        self.evaluate()
