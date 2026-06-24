from .utils import get_files, save_file, preprocess_append
from .config import (
                     VLLM_FILE,
                     BM_FOLDER,
                     OUTPUT_CHUNK,
                     MODEL_NAME,
                     OUTPUT_ANSWER,
                     OUTPUT_CODE_SET,
                     OUTPUT_DOC_SET,
                     STOPWORDS
                    )
from .index import py_chunking, md_chunking
from .search import gather_data_set, process_data_set, save_search
from .bm25 import bm_tokeniser
from .answer import get_answer, answer_data_set
from .evaluate import find_recall_metric
# from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any
import json
import bm25s
import os


class Cli(object):
    def __init__(self) -> None:
        ...

    def index(self, chunk_size: int) -> None:
        if chunk_size < 250 or chunk_size > 2000:
            raise ValueError("wrong max chunk size," +
                             "please try between 250 and 2000")
        lst_files = get_files(VLLM_FILE)
        py_chunk: list[Any] = []
        md_chunk: list[Any] = []
        for file in lst_files:
            if file.endswith(".py"):
                py_chunk.extend(py_chunking(file, chunk_size))
            elif file.endswith(".md"):
                md_chunk.extend(md_chunking(file, chunk_size))
        save_file(py_chunk, md_chunk)
        md_chunk.extend(py_chunk)
        bm_tokeniser(md_chunk)

    def search(self, query: str, k: int = 5) -> None:
        if not os.path.exists(BM_FOLDER):
            raise ValueError("Please use the commande index before")
        retriever = bm25s.BM25.load(BM_FOLDER, load_corpus=True)
        query_token = bm25s.tokenize(
            [preprocess_append(query)], stopwords=STOPWORDS
        )
        results, scores = retriever.retrieve(query_token, k=k)
        question = [{"question": query}]
        res_chunk = save_search(results[0])
        question.extend(res_chunk)
        with open(OUTPUT_CHUNK, 'w') as f:
            f.write(json.dumps(question, ensure_ascii=False, indent=4))

    def search_data_set(self, k: int = 5) -> None:
        if not os.path.exists(BM_FOLDER):
            raise ValueError("Please use the commande index before")
        retriever = bm25s.BM25.load(BM_FOLDER, load_corpus=True)
        data_set = gather_data_set()
        process_data_set(data_set, retriever, k)

    def answer(self) -> None:
        try:
            with open(OUTPUT_CHUNK, 'r') as data:
                chunk = json.load(data)
                if len(chunk) != 6:
                    print("Please use the commande search before")
                    return
        except FileExistsError:
            print("Please use the commande search before")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        result = get_answer(tokenizer, model, chunk)
        output = {"answer": result}
        with open(OUTPUT_ANSWER, 'w') as f:
            f.write(json.dumps(output, ensure_ascii=False, indent=4))

    def answer_data_set(self) -> None:
        if (not os.path.exists(OUTPUT_DOC_SET) or
           not os.path.exists(OUTPUT_CODE_SET)):
            raise ValueError("Please use the commande search_data_set before")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        answer_data_set(tokenizer, model)

    def evaluate(self) -> None:
        order = [1, 3, 5, 10]
        print("--- DOCS ---")
        doc_results = []
        for val in order:
            doc_results.append(find_recall_metric(
                "data/public/AnsweredQuestions/dataset_docs_public.json",
                "data/output/output_doc_set.json", val
            ))
        for i, result in enumerate(doc_results):
            print(f"k@{order[i]} ; {int(result * 100)}% ({result})")

        print("--- CODE ---")
        code_results = []
        for val in order:
            code_results.append(find_recall_metric(
                "data/public/AnsweredQuestions/dataset_code_public.json",
                "data/output/output_code_set.json", val
            ))
        for i, result in enumerate(code_results):
            print(f"k@{order[i]} ; {int(result * 100)}% ({result})")

    def prerun(self, chunk_size: int) -> None:
        self.index(chunk_size)
        self.search_data_set(k=10)
        self.evaluate()
