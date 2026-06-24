from .utils import extract
from .data_model import (
                         MinimalSource,
                         StudentSearchResults,
                         MinimalAnswer,
                         StudentSearchResultsAndAnswer,
                         MinimalSearchResults
                        )
from .config import (
                     SYSTEM_PROMPT,
                     OUTPUT_CODE_SET,
                     OUTPUT_DOC_SET,
                     OUTPUT_ANSWER_DATA_SET
                    )
from typing import Any
import json
from tqdm import tqdm


def get_data_set() -> tuple[
    list[MinimalSearchResults], list[MinimalSearchResults]
]:
    with open(OUTPUT_CODE_SET, 'r') as data:
        code = json.load(data)
    with open(OUTPUT_DOC_SET, 'r') as data:
        doc = json.load(data)
    data_code = StudentSearchResults.model_validate(code)
    data_doc = StudentSearchResults.model_validate(doc)
    return (data_code.search_results, data_doc.search_results)


def get_context(chunk: list[Any]) -> list[str]:
    blocks = []
    for i in range(1, 6):
        if not isinstance(chunk[i], MinimalSource):
            m_s = MinimalSource(
                file_path=chunk[i]["file_path"],
                first_character_index=chunk[i]["first_character_index"],
                last_character_index=chunk[i]["last_character_index"]
            )
            text = extract(m_s)
            block = f"[Source {i}: {chunk[i]['file_path']}]\n{text}"
        else:
            text = extract(chunk[i])
            block = f"[Source {i}: {chunk[i].file_path}]\n{text}"
        blocks.append(block)
    return blocks


def prompt_gen(question: str, chunk: list[Any]) -> list[dict[str, str]]:
    context = get_context(chunk)

    user_message = f"""Context:
                        {context}

                        Question: {question}

                        Answer the question based only on the context above."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]


def get_answer(tokenizer: Any, model: Any, chunk: list[Any]) -> str:
    messages = prompt_gen(chunk[0]["question"], chunk)
    text = tokenizer.apply_chat_template(messages, tokenize=False,
                                         add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")

    outputs = model.generate(**inputs, max_new_tokens=350, temperature=0.3,
                             do_sample=True)
    response: str = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )
    response = response.strip()
    if "</think>" in response:
        response = response.split("</think>")[-1]

    return response


def answer_data_set(tokenizer: Any, model: Any) -> None:
    data_set = get_data_set()
    list_MinimalAnswer: list[MinimalAnswer] = []
    formated_chunk: list[Any] = []
    for data_model in tqdm(
                          data_set[0],
                          desc="Aswering data_set...",
                          bar_format="{desc} {bar} {percentage:.0f}%"
                          ):
        formated_chunk = [{"question": data_model.question}]
        formated_chunk.extend(c for c in data_model.retrieved_sources)
        response = get_answer(tokenizer, model, formated_chunk)
        list_MinimalAnswer.append(MinimalAnswer(
            question_id=data_model.question_id,
            question=data_model.question,
            retrieved_sources=data_model.retrieved_sources,
            answer=response
        ))

    res_and_answer = StudentSearchResultsAndAnswer(
        search_results=list_MinimalAnswer
    )

    with open(OUTPUT_ANSWER_DATA_SET, 'w') as f:
        f.write(json.dumps(
            res_and_answer.model_dump(), ensure_ascii=False, indent=4
        ))
