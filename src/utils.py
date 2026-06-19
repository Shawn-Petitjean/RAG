from .data_model import MinimalSource
from pathlib import Path
import json
from os import path, makedirs
from typing import Any
from .config import (
                     OUTPUT_CODE,
                     OUTPUT_DOCS,
                     OUTPUT_FILE,
                    )


def lst_line(txt: str, i: int) -> int | None:
    while txt[i] != "\n":
        i -= 1
    while txt[i] == "\n":
        i -= 1
    for j in range(i, 0, -1):
        if txt[j] == "\n" and i - j > 10:
            return j + 1
    return None  # Sécurité si la condition du for n'est jamais respectée


def get_index(line1: int, line2: int, path: str) -> list[int]:
    with open(path, mode='r') as data:
        s = data.readlines()
    i_start = 0
    i_end = 0
    c_line = 0
    for line in s:
        c_line += 1
        if c_line > line2:
            break
        elif c_line < line1:
            i_start += len(line)
        i_end += len(line)
    return [i_start + 1, i_end - 1]


def extract(m_s: MinimalSource) -> str:
    with open(m_s.file_path, mode='r') as data:
        txt = data.read()
        return txt[m_s.first_character_index - 1: m_s.last_character_index - 1]


def get_files(dir: str) -> list[str]:
    dir_path = Path(dir)
    files: list[str] = []
    for f in dir_path.iterdir():
        if not f.is_file():
            d = str(f)
            files.extend(get_files(d))
        elif str(f).endswith(".py") or str(f).endswith(".md"):
            files.append(str(f))
    return files


def save_file(py_chunk: list[Any], md_chunk: list[Any]) -> None:
    if not path.exists(OUTPUT_FILE):
        makedirs(OUTPUT_FILE)

    def serialize(chunk: list[Any] | Any) -> list[Any]:
        result: list[Any] = []
        if isinstance(chunk, list):
            for item in chunk:
                if isinstance(item, list):
                    result.extend(serialize(item))
                elif hasattr(item, 'model_dump'):
                    result.append(item.model_dump())
                else:
                    result.append(item)
        return result

    with open(OUTPUT_CODE, 'w') as f:
        f.write(json.dumps(serialize(py_chunk), ensure_ascii=False, indent=4))
    with open(OUTPUT_DOCS, 'w') as d:
        d.write(json.dumps(serialize(md_chunk), ensure_ascii=False, indent=4))


def get_chunk() -> Any:
    with open(OUTPUT_DOCS, 'r') as doc_data:
        docs = json.load(doc_data)
    with open(OUTPUT_CODE, 'r') as cod_data:
        code = json.load(cod_data)
    docs.extend(code)
    return docs
