OUTPUT_DOCS = "data/output/output_docs.json"
OUTPUT_CODE = "data/output/output_code.json"
OUTPUT_CHUNK = "data/output/output_chunk.json"
OUTPUT_DOC_SET = "data/output/output_doc_set.json"
OUTPUT_CODE_SET = "data/output/output_code_set.json"
OUTPUT_ANSWER = "data/output/answer.json"
OUTPUT_ANSWER_DATA_SET = "data/output/answer_data_set.json"

OUTPUT_FILE = "data/output"

VLLM_FILE = "vllm-0.10.1"

ANSWER_CODE = "data/public/AnsweredQuestions/dataset_code_public.json"
ANSWER_DOCS = "data/public/AnsweredQuestions/dataset_docs_public.json"
UNANSWER_DOCS = "data/public/UnansweredQuestions/dataset_docs_public.json"
UNANSWER_CODE = "data/public/UnansweredQuestions/dataset_code_public.json"

BM_FOLDER = "data/bm_data/"

MODEL_NAME = "Qwen/Qwen3-0.6B"

OVLAP = 50

SYSTEM_PROMPT = """You are a documentation assistant for the vLLM project.
Answer the user's question using ONLY the information in the provided sources.

Rules:
- Be self-contained: your answer must be understandable without seeing the
question.
- Be source-grounded: mention which source(s) you used.
- Be faithful: never invent information that is not in the sources.
- Be relevant: directly answer what was asked, no unrelated details.
- If the sources do not contain the answer, say so clearly instead of guessing.
"""
