import bm25s
from typing import Any
from .data_model import MinimalSource
from .utils import extract
from .config import BM_FOLDER


def bm_tokeniser(list_MA: list[MinimalSource]) -> None:
    texts: list[str] = [extract(c) for c in list_MA]

    corpus_tokens: Any = bm25s.tokenize(texts)
    retriever: Any = bm25s.BM25()
    retriever.index(corpus_tokens)
    retriever.save(BM_FOLDER)
