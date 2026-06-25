import bm25s
from typing import Any
from .data_model import MinimalSource
from .utils import extract, preprocess_with_path
from .config import BM_FOLDER, STOPWORDS, K1, B
from tqdm import tqdm


def bm_tokeniser(list_MA: list[MinimalSource]) -> None:
    """Tokenize all of the data set and save the bm25 data for the searching.

    Args:
        list_MA: list of MinimalSource that contain all the chunk.

    Returns:
        None but save the data at BM_FOLDER.
    """
    texts: list[str] = [
        preprocess_with_path(extract(c), c.file_path) for c in tqdm(
            list_MA,
            desc="process text to give at bm25...",
            bar_format="{desc} {bar} {percentage:.0f}%",
            leave=False
            )
    ]

    corpus_tokens: Any = bm25s.tokenize(texts, stopwords=STOPWORDS)
    retriever: Any = bm25s.BM25(k1=K1, b=B)
    retriever.index(corpus_tokens)
    retriever.save(BM_FOLDER)
