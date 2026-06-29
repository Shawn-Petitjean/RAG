import bm25s
from typing import Any
from .data_model import MinimalSource
from .utils import extract, preprocess_with_path
from .config import (
                     BM_PY,
                     STOPWORDS,
                     K1,
                     B,
                     BM_MD,
                     BM_ALL,
                     PYTHON_KEYWORDS,
                     ENGLISH_STOPWORDS
                    )
from tqdm import tqdm


def bm_tokeniser(list_md: list[MinimalSource],
                 list_py: list[MinimalSource]) -> None:
    """Tokenize all of the data set and save the bm25 data for the searching.

    Args:
        list_MA: list of MinimalSource that contain all the chunk.

    Returns:
        None but save the data at BM_FOLDER.
    """

    stop_words = [ENGLISH_STOPWORDS, PYTHON_KEYWORDS, STOPWORDS]
    folder = [BM_MD, BM_PY, BM_ALL]
    all = list_md + list_py
    lst = [list_md, list_py, all]
    for i in range(0, 3):
        texts_md: list[str] = [
            preprocess_with_path(extract(c), c.file_path) for c in tqdm(
                lst[i],
                desc="process .md to give at bm25...",
                bar_format="{desc} {bar} {percentage:.0f}%",
                leave=False
                )
        ]
        corpus_tokens_md: Any = bm25s.tokenize(texts_md,
                                               stopwords=stop_words[i])
        retriever_md: Any = bm25s.BM25(k1=K1, b=B)
        retriever_md.index(corpus_tokens_md)
        retriever_md.save(folder[i])
