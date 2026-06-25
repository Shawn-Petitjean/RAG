import bm25s  # type: ignore[import-untyped]
from typing import Any
from .data_model import MinimalSource
from .utils import extract, preprocess_with_path
from .config import BM_PY, STOPWORDS, K1, B, BM_MD, BM_ALL
from tqdm import tqdm


def bm_tokeniser(list_md: list[MinimalSource],
                 list_py: list[MinimalSource]) -> None:
    """Tokenize all of the data set and save the bm25 data for the searching.

    Args:
        list_MA: list of MinimalSource that contain all the chunk.

    Returns:
        None but save the data at BM_FOLDER.
    """
    texts_md: list[str] = [
        preprocess_with_path(extract(c), c.file_path) for c in tqdm(
            list_md,
            desc="process .md to give at bm25...",
            bar_format="{desc} {bar} {percentage:.0f}%",
            leave=False
            )
    ]
    corpus_tokens_md: Any = bm25s.tokenize(texts_md, stopwords=STOPWORDS)
    retriever_md: Any = bm25s.BM25(k1=K1, b=B)
    retriever_md.index(corpus_tokens_md)
    retriever_md.save(BM_MD)

    texts_py: list[str] = [
        preprocess_with_path(extract(c), c.file_path) for c in tqdm(
            list_py,
            desc="process py to give at bm25...",
            bar_format="{desc} {bar} {percentage:.0f}%",
            leave=False
            )
    ]
    corpus_tokens_py: Any = bm25s.tokenize(texts_py, stopwords=STOPWORDS)
    retriever_py: Any = bm25s.BM25(k1=K1, b=B)
    retriever_py.index(corpus_tokens_py)
    retriever_py.save(BM_PY)

    list_md.extend(list_py)
    all_texts: list[str] = [
        preprocess_with_path(extract(c), c.file_path) for c in tqdm(
            list_md,
            desc="process py and md to give at bm25...",
            bar_format="{desc} {bar} {percentage:.0f}%",
            leave=False
            )
    ]
    corpus_tokens_all: Any = bm25s.tokenize(all_texts, stopwords=STOPWORDS)
    retriever_all: Any = bm25s.BM25(k1=K1, b=B)
    retriever_all.index(corpus_tokens_all)
    retriever_all.save(BM_ALL)
