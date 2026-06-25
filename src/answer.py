from .utils import extract
from .data_model import (
    MinimalSource,
    StudentSearchResults,
    MinimalAnswer,
    MinimalSearchResults,
    StudentSearchResultsAndAnswer,
)
from .config import (
    SYSTEM_PROMPT,
    OUTPUT_CODE_SET,
    OUTPUT_DOC_SET,
    OUTPUT_ANSWER_CODE_SET,
    OUTPUT_ANSWER_DOCS_SET
)
from typing import Any, cast
import json
import re
from tqdm import tqdm
from transformers import StoppingCriteria, StoppingCriteriaList


def get_data_set() -> tuple[list[MinimalSearchResults],
                            list[MinimalSearchResults]]:
    """Open the right files and return search results."""
    with open(OUTPUT_CODE_SET, "r") as data:
        code = json.load(data)
    with open(OUTPUT_DOC_SET, "r") as data:
        doc = json.load(data)
    data_code = StudentSearchResults.model_validate(code)
    data_doc = StudentSearchResults.model_validate(doc)
    return data_code.search_results, data_doc.search_results


def get_context(chunk: list[Any]) -> str:
    """Return a joined string of source context for the LLM."""
    blocks = []
    for idx in range(1, min(len(chunk), 6)):
        source = chunk[idx]
        if not isinstance(source, MinimalSource):
            source = MinimalSource(
                file_path=source["file_path"],
                first_character_index=source["first_character_index"],
                last_character_index=source["last_character_index"],
            )
        text = extract(source)
        blocks.append(f"[Source {idx}: {source.file_path}]\n{text}")
    return "\n\n".join(blocks)


def get_source_paths(chunk: list[Any]) -> list[str]:
    """Return unique source file paths from the retrieved chunk."""
    paths: list[str] = []
    seen = set()
    for source in chunk[1:]:
        file_path = None
        if isinstance(source, MinimalSource):
            file_path = source.file_path
        elif isinstance(source, dict) and "file_path" in source:
            file_path = source["file_path"]
        if file_path and file_path not in seen:
            seen.add(file_path)
            paths.append(file_path)
    return paths


def prompt_gen(question: str, chunk: list[Any]) -> list[dict[str, str]]:
    """Build the prompt for the LLM using the retrieved context."""
    context = get_context(chunk)
    user_message = (
        "Context:\n"
        f"{context}\n\n"
        f"Question: {question}\n\n"
        "Answer the question using ONLY the context above.\n"
        "Be self-contained, source-grounded, faithful, and relevant.\n"
        "If you cannot answer, respond exactly:\n"
        "ANSWER: Aucune réponse trouvée dans les sources.\n"
        "SOURCES: Aucune source trouvée.\n"
        "Otherwise, use exactly this format:\n"
        "ANSWER: <your answer>\n"
        "SOURCES: <file_path1>\n"
        "<file_path2>\n"
        "<<END>>\n"
        "Do not include analysis, reasoning, or any extra text.\n"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def parse_response(response: str) -> tuple[str, list[str]]:
    """Extract the answer and the source file paths from the LLM response."""
    response = response.strip()
    if "</think>" in response:
        response = response.split("</think>")[-1]
    if "<<END>>" in response:
        response = response.split("<<END>>")[0]
    lines = [ln for ln in response.splitlines() if ln.strip()
             and ln.strip().upper() != "END"]
    response = "\n".join(lines).strip()

    answer_text = ""
    source_lines: list[str] = []
    if "ANSWER:" in response:
        _, remainder = response.split("ANSWER:", 1)
        if "SOURCES:" in remainder:
            answer_text, source_block = remainder.split("SOURCES:", 1)
            answer_text = answer_text.strip()
            source_lines = source_block.splitlines()
        else:
            answer_text = remainder.strip()
    elif "SOURCES:" in response:
        answer_text, source_block = response.split("SOURCES:", 1)
        answer_text = answer_text.strip()
        source_lines = source_block.splitlines()
    else:
        answer_text = response.strip()

    sources: list[str] = []
    for line in source_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()
        if re.match(r"^\d+\.", line):
            line = re.sub(r"^\d+\.\s*", "", line)
        if line:
            sources.append(line)
    return answer_text, list(dict.fromkeys(sources))


class EndTokenStoppingCriteria(StoppingCriteria):
    def __init__(self, stop_ids: list[int]):
        self.stop_ids = stop_ids

    def __call__(self, input_ids: Any, scores: Any, **kwargs: Any) -> bool:
        if len(input_ids[0]) < len(self.stop_ids):
            return False
        sequence = cast(list[int], input_ids[0][-len(self.stop_ids):].tolist())
        return sequence == self.stop_ids


def get_answer(tokenizer: Any, model: Any, chunk: list[Any]) -> str:
    """Generate the structured answer from the model."""
    messages = prompt_gen(chunk[0]["question"], chunk)
    text = tokenizer.apply_chat_template(messages, tokenize=False,
                                         add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    stop_token = "<<END>>"
    stop_ids = tokenizer(stop_token, add_special_tokens=False)["input_ids"]
    stop_criteria = StoppingCriteriaList([EndTokenStoppingCriteria(stop_ids)])

    outputs = model.generate(
        **inputs,
        max_new_tokens=400,
        temperature=0.0,
        do_sample=False,
        top_p=1.0,
        stopping_criteria=stop_criteria,
        pad_token_id=tokenizer.eos_token_id,
    )
    response: str = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    answer_text, sources = parse_response(response)
    if not answer_text:
        answer_text = "Aucune réponse trouvée dans les sources."
    if not sources:
        sources = get_source_paths(chunk)
    if not sources:
        sources = ["Aucune source trouvée."]

    return f"ANSWER: {answer_text}\n\nSOURCES:\n" + "\n".join(sources)


def answer_data_set(tokenizer: Any, model: Any) -> None:
    """Generate the response for the whole dataset."""
    data_set = get_data_set()
    list_MinimalAnswer: list[MinimalAnswer] = []
    for data_model in tqdm(
        data_set[0],
        desc="Answering data_set for code question...",
        bar_format="{desc} {bar} {percentage:.0f}%",
    ):
        formatted_chunk_py: list[dict[str, str] |
                                 MinimalSource] = [{"question":
                                                    data_model.question}]
        formatted_chunk_py.extend(data_model.retrieved_sources)
        response = get_answer(tokenizer, model, formatted_chunk_py)
        list_MinimalAnswer.append(
            MinimalAnswer(
                question_id=data_model.question_id,
                question=data_model.question,
                retrieved_sources=data_model.retrieved_sources,
                answer=response,
            )
        )

    res_and_answer = StudentSearchResultsAndAnswer(
        search_results=list_MinimalAnswer,
    )
    with open(OUTPUT_ANSWER_CODE_SET, "w") as f:
        f.write(
            json.dumps(
                res_and_answer.model_dump(),
                ensure_ascii=False,
                indent=4,
            )
        )

    for data_model in tqdm(
        data_set[1],
        desc="Answering data_set for docs question...",
        bar_format="{desc} {bar} {percentage:.0f}%",
    ):
        formatted_chunk_md: list[dict[str, str] |
                                 MinimalSource] = [{"question":
                                                    data_model.question}]
        formatted_chunk_md.extend(data_model.retrieved_sources)
        response = get_answer(tokenizer, model, formatted_chunk_md)
        list_MinimalAnswer.append(
            MinimalAnswer(
                question_id=data_model.question_id,
                question=data_model.question,
                retrieved_sources=data_model.retrieved_sources,
                answer=response,
            )
        )

    res_and_answer = StudentSearchResultsAndAnswer(
        search_results=list_MinimalAnswer,
    )
    with open(OUTPUT_ANSWER_DOCS_SET, "w") as f:
        f.write(
            json.dumps(
                res_and_answer.model_dump(),
                ensure_ascii=False,
                indent=4,
            )
        )
