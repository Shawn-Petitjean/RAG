OUTPUT_DOCS = "data/output/output_docs.json"
OUTPUT_CODE = "data/output/output_code.json"
OUTPUT_CHUNK = "data/output/output_chunk.json"
OUTPUT_DOC_SET = "data/output/output_doc_set.json"
OUTPUT_CODE_SET = "data/output/output_code_set.json"
OUTPUT_ANSWER = "data/output/answer.json"
OUTPUT_ANSWER_DATA_SET = "data/output/answer_data_set.json"

OUTPUT_FILE = "data/output"

VLLM_FILE = "data/raw/vllm-0.10.1"

ANSWER_CODE = "data/public/AnsweredQuestions/dataset_code_public.json"
ANSWER_DOCS = "data/public/AnsweredQuestions/dataset_docs_public.json"
UNANSWER_DOCS = "data/public/UnansweredQuestions/dataset_docs_public.json"
UNANSWER_CODE = "data/public/UnansweredQuestions/dataset_code_public.json"

BM_FOLDER = "data/bm_data/"

MODEL_NAME = "Qwen/Qwen3-0.6B"

OVLAP = 30
K1 = 2.0
B = 0.7
MIN_CHUNK = 50

PYTHON_KEYWORDS = [
    'def', 'class', 'import', 'from', 'return', 'self', 'None', 'True',
    'False', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
    'finally', 'with', 'as', 'assert', 'break', 'continue', 'pass',
    'raise', 'yield', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global',
    'nonlocal', 'del'
]

ENGLISH_STOPWORDS = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "arent", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "cant",
    "cannot", "could", "couldnt", "did", "didnt", "do", "does", "doesnt",
    "doing", "dont", "down", "during", "each", "few", "for", "from",
    "further", "had", "hadnt", "has", "hasnt", "have", "havent", "having",
    "he", "hed", "hell", "hes", "her", "here", "heres", "hers", "herself",
    "him", "himself", "his", "how", "hows", "i", "id", "im", "ive", "if",
    "in", "into", "is", "isnt", "it", "its", "itself", "lets", "me", "more",
    "most", "mustnt", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shant", "she", "shed", "shell", "shes",
    "should", "shouldnt", "so", "some", "such", "than", "that", "thats",
    "the", "their", "theirs", "them", "themselves", "then", "there",
    "theres", "these", "they", "theyd", "theyll", "theyre", "theyve",
    "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasnt", "we", "wed", "well", "were", "weve", "werent",
    "what", "whats", "when", "whens", "where", "wheres", "which", "while",
    "who", "whos", "whom", "why", "whys", "with", "wont", "would",
    "wouldnt", "you", "youd", "youll", "youre", "youve", "your", "yours",
    "yourself", "yourselves"
]

STOPWORDS = ENGLISH_STOPWORDS + PYTHON_KEYWORDS


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
