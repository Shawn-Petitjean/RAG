from .utils import get_files, save_file, extract, save_results
from .config import VLLM_FILE, BM_FOLDER
from .index import py_chunking, md_chunking
from .bm25 import bm_tokeniser
import bm25s
import os


class Cli(object):
    def __init__(self):
        ...

    def index(self, chunk_size: int):
        if chunk_size < 250 or chunk_size > 2000:
            raise ValueError("wrong max chunk size, please try between 250 and 2000")
        lst_files = get_files(VLLM_FILE)
        py_chunk = []
        md_chunk = []
        for file in lst_files:
            if file.endswith(".py"):
                py_chunk.extend(py_chunking(file, chunk_size))
            elif file.endswith(".md"):
                md_chunk.extend(md_chunking(file, chunk_size))
        save_file(py_chunk, md_chunk)
        md_chunk.extend(py_chunk)
        bm_tokeniser(md_chunk)
        

    def search(self, query: str, k=5):
        if not os.path.exists(BM_FOLDER):
            raise ValueError("Please use the commande index before")
        retriever = bm25s.BM25.load(BM_FOLDER, load_corpus=True)
        query_token = bm25s.tokenize([query])
        results, scores = retriever.retrieve(query_token, k=k)
        save_results(results[0])

    def search_data_set():
        ...

    def answer():
        ...

    def answer_data_set():
        ...

    def evaluate():
        ...
