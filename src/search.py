from .config import (
    OUTPUT_CHUNK,
    ENGLISH_STOPWORDS,
    PYTHON_KEYWORDS,
    STOPWORDS,
)
from .data_model import (
    UnansweredQuestion,
    MinimalSearchResults,
    StudentSearchResults,
)
from .utils import get_chunk, preprocess_append
import json
import bm25s  # type: ignore[import-untyped]
from typing import Any
from tqdm import tqdm


def save_search(res: list[int], chunk_type: str = "all") -> list[Any]:
    """Save the result that was found.

    Args:
        res: List of chunk indices.
        chunk_type: One of "all", "doc", or "code".

    Returns:
        The list of retrieved source chunks.
    """
    chunk = get_chunk(chunk_type)
    res_chunk = []
    for i in range(len(res)):
        res_chunk.append(chunk[res[i]])

    with open(OUTPUT_CHUNK, 'w') as f:
        f.write(json.dumps(res_chunk, ensure_ascii=False, indent=4))

    return res_chunk


def gather_data_set(data_path: str) -> list[UnansweredQuestion]:
    """Open the file and format the unanswered questions.

    Args:
        data_path: Path to the dataset JSON.

    Returns:
        List of validated UnansweredQuestion objects.
    """
    with open(data_path, 'r') as data:
        questions = json.load(data)
    return [UnansweredQuestion.model_validate(question)
            for question in questions["rag_questions"]]


def process_data_set(
                     data_set: list[UnansweredQuestion],
                     retriever: Any,
                     k: int,
                     output_path: str,
                     chunk_type: str = "all"
                     ) -> None:
    """Run retrieval on a dataset and save student search results.

    Args:
        data_set: List of unanswered questions.
        retriever: BM25 retriever instance.
        k: Number of top chunks to retrieve.
        output_path: Path where results are saved.
        chunk_type: One of "all", "doc", or "code".
    """
    if chunk_type == "code":
        stopwords = PYTHON_KEYWORDS
        desc = "Searching for code questions with bm25"
    elif chunk_type == "doc":
        stopwords = ENGLISH_STOPWORDS
        desc = "Searching for doc questions with bm25"
    else:
        stopwords = STOPWORDS
        desc = "Searching for questions with bm25"

    search_res = []
    for data in tqdm(
                    data_set,
                    desc=desc,
                    bar_format="{desc} {bar} {percentage:.0f}%"
                    ):
        query_token = bm25s.tokenize(
            [preprocess_append(data.question)], stopwords=stopwords
        )
        results, scores = retriever.retrieve(query_token, k=k)
        if results is None or len(results) == 0:
            res_chunk = []
        else:
            res_chunk = save_search(results[0], chunk_type=chunk_type)
        search_res.append(
            MinimalSearchResults(
                question_id=data.question_id,
                question_str=data.question,
                retrieved_sources=res_chunk,
            )
        )

    data_stud_search_res = StudentSearchResults(
            search_results=search_res,
            k=k
        )
    with open(output_path, 'w') as f:
        f.write(data_stud_search_res.model_dump_json(indent=4))
