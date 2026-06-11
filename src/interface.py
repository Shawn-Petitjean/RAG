from .utils import get_files, save_file
from .config import VLLM_FILE
from .index import py_chunking, md_chunking
from .bm25 import bm_tokeniser


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
        

    def search():
        ...

    def search_data_set():
        ...

    def answer():
        ...

    def answer_data_set():
        ...

    def evaluate():
        ...
