from .utils import get_files, save_file
from .config import (
                     VLLM_FILE,
                     BM_FOLDER,
                     OUTPUT_CHUNK,
                     MODEL_NAME,
                     OUTPUT_ANSWER,
                     OUTPUT_CODE_SET,
                     OUTPUT_DOC_SET
                    )
from .index import py_chunking, md_chunking
from .search import gather_data_set, process_data_set, save_search
from .bm25 import bm_tokeniser
from .answer import get_answer, answer_data_set
from transformers import AutoModelForCausalLM, AutoTokenizer
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
        query_token = bm25s.tokenize([query])
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
        # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        answer_data_set()

    def evaluate(self) -> None:
        ...
