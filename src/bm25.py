import bm25s
from typing import Any
from .data_model import MinimalSource
from .utils import extract, preprocess_with_path
from .config import BM_FOLDER, STOPWORDS, K1, B


def bm_tokeniser(list_MA: list[MinimalSource]) -> None:
    texts: list[str] = [
        preprocess_with_path(extract(c), c.file_path) for c in list_MA
    ]

    corpus_tokens: Any = bm25s.tokenize(texts, stopwords=STOPWORDS)
    retriever: Any = bm25s.BM25(k1=K1, b=B)
    retriever.index(corpus_tokens)
    retriever.save(BM_FOLDER)
