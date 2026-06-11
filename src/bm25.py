import bm25s
from .data_model import MinimalAnswer
from .utils import extract
from .config import BM_FOLDER


def bm_tokeniser(list_MA):
    texts = [extract(c) for c in list_MA]

    corpus_tokens = bm25s.tokenize(texts)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)
    retriever.save(BM_FOLDER)


def bm25_init(list_code, list_docs):
    ...