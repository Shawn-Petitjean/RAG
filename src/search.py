from .config import UNANSWER_DOCS, UNANSWER_CODE, OUTPUT_DOC_SET, OUTPUT_CODE_SET
from .data_model import UnansweredQuestion, MinimalSearchResults, StudentSearchResults
from .utils import get_chunk
import json
import bm25s


def save_search(res: list[int]):
    chunk = get_chunk()
    res_chunk = []
    for i in range(0, len(res)):
        res_chunk.append(chunk[i])
    return res_chunk
    with open(OUTPUT_CHUNK, 'w') as f:
        f.write(json.dumps(res_chunk, ensure_ascii=False, indent=4))


def gather_data_set():
    with open(UNANSWER_DOCS, 'r') as data:
        docs = json.load(data)
    with open(UNANSWER_CODE, 'r') as data:
        codes = json.load(data)
    unanswer_code = [UnansweredQuestion.model_validate(code) for code in codes["rag_questions"]]
    unanswer_doc = [UnansweredQuestion.model_validate(doc) for doc in docs["rag_questions"]]
    return unanswer_code, unanswer_doc


def process_data_set(data_set: list, retriever, k):
    code_search_res = []
    doc_search_res = []
    for code in data_set[0]:
        query_token = bm25s.tokenize([code.question])
        results, scores = retriever.retrieve(query_token, k=k)
        res_chunk = save_search(results[0])
        code_search_res.append(MinimalSearchResults(
                question_id=code.question_id,
                question=code.question,
                retrieved_sources=res_chunk,
            ))
    code_stud_search_res = StudentSearchResults(
            search_results=code_search_res,
            k=k
        )
    for doc in data_set[1]:
        query_token = bm25s.tokenize([doc.question])
        results, scores = retriever.retrieve(query_token, k=k)
        res_chunk = save_search(results[0])
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



