from .utils import extract
from .data_model import (
                         MinimalSource,
                         StudentSearchResults,
                         MinimalAnswer,
                         StudentSearchResultsAndAnswer
                        )
from .config import SYSTEM_PROMPT, OUTPUT_CODE_SET, OUTPUT_DOC_SET
import json


def get_data_set():
    with open(OUTPUT_CODE_SET, 'r') as data:
        code = json.load(data)
    with open(OUTPUT_DOC_SET, 'r') as data:
        doc = json.load(data)
    data_code = StudentSearchResults.model_validate(code)
    data_doc = StudentSearchResults.model_validate(doc)
    return (data_code.search_results, data_doc.search_results)


def get_context(chunk):
    blocks = []
    for i in range(1, 6):
        m_s = MinimalSource(
            file_path=chunk[i]["file_path"],
            first_character_index=chunk[i]["first_character_index"],
            last_character_index=chunk[i]["last_character_index"]
        )
        text = extract(m_s)
        block = f"[Source {i}: {chunk[i]["file_path"]}]\n{text}"
        blocks.append(block)
    return blocks


def prompt_gen(question: str, chunk: list[dict]) -> list[dict]:
    context = get_context(chunk)

    user_message = f"""Context:
                        {context}

                        Question: {question}

                        Answer the question based only on the context above."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]


def get_answer(tokenizer, model, chunk):
    messages = prompt_gen(chunk[0]["question"], chunk)
    text = tokenizer.apply_chat_template(messages, tokenize=False,
                                         add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")

    outputs = model.generate(**inputs, max_new_tokens=350, temperature=0.3,
                             do_sample=True)
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:],
                                skip_special_tokens=True)
    response = response.strip()
    if "</think>" in response:
        response = response.split("</think>")[-1]
    
    return response


def answer_data_set(tokenizer, model):
    data_set = get_data_set()
    for data_model in data_set[0]:
        answer = get_answer(tokenizer, model)
