from .config import (
                     UNANSWER_DOCS,
                     UNANSWER_CODE,
                     OUTPUT_DOC_SET,
                     OUTPUT_CODE_SET,
                     OUTPUT_CHUNK,
                     ENGLISH_STOPWORDS,
                     PYTHON_KEYWORDS
                    )
from .data_model import (
                         UnansweredQuestion,
                         MinimalSearchResults,
                         StudentSearchResults
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


def gather_data_set() -> tuple[list[UnansweredQuestion],
                               list[UnansweredQuestion]]:
    """Open the files and format them

    Returns:
        list of the data_class with the good format.
    """
    with open(UNANSWER_DOCS, 'r') as data:
        docs = json.load(data)
    with open(UNANSWER_CODE, 'r') as data:
        codes = json.load(data)
    unanswer_code = [UnansweredQuestion.model_validate(code)
                     for code in codes["rag_questions"]]
    unanswer_doc = [UnansweredQuestion.model_validate(doc)
                    for doc in docs["rag_questions"]]
    return unanswer_code, unanswer_doc


def process_data_set(data_set: tuple[list[UnansweredQuestion],
                     list[UnansweredQuestion]],
                     retriever_md: Any, retriever_py: Any, k: int) -> None:
    """Take the question and chunk, and give them to
       bm25 for finding the good chunk.

    Args:
        data_set: tuple that contain all of chunk and question.

    Returns:
        Save a json with the StudentSearchResults
        that contain question and chunk associated.
    """
    code_search_res = []
    doc_search_res = []
    for code in tqdm(
                    data_set[0],
                    desc="Searching for code question with bm25",
                    bar_format="{desc} {bar} {percentage:.0f}%"
                    ):
        query_token = bm25s.tokenize(
            [preprocess_append(code.question)], stopwords=PYTHON_KEYWORDS
        )
        results, scores = retriever_py.retrieve(query_token, k=k)
        res_chunk = save_search(results[0], chunk_type="code")
        code_search_res.append(MinimalSearchResults(
                question_id=code.question_id,
                question=code.question,
                retrieved_sources=res_chunk,
            ))
    code_stud_search_res = StudentSearchResults(
            search_results=code_search_res,
            k=k
        )
    for doc in tqdm(
                    data_set[1],
                    desc="Searching for doc question with bm25",
                    bar_format="{desc} {bar} {percentage:.0f}%"
                    ):
        query_token = bm25s.tokenize(
            [preprocess_append(doc.question)], stopwords=ENGLISH_STOPWORDS
        )
        results, scores = retriever_md.retrieve(query_token, k=k)
        res_chunk = save_search(results[0], chunk_type="doc")
        doc_search_res.append(MinimalSearchResults(
                question_id=doc.question_id,
                question=doc.question,
                retrieved_sources=res_chunk,
            ))
    doc_stud_search_res = StudentSearchResults(
        search_results=doc_search_res,
        k=k
        )
    with open(OUTPUT_CODE_SET, 'w') as f:
        f.write(code_stud_search_res.model_dump_json(indent=4))
    with open(OUTPUT_DOC_SET, 'w') as f:
        f.write(doc_stud_search_res.model_dump_json(indent=4))
