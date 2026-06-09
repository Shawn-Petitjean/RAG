from .data_model import MinimalSource
from pathlib import Path
import json
from os import path, makedirs
from .config import OUTPUT_CODE, OUTPUT_DOCS, OUTPUT_FILE


def lst_line(txt: str, i: int) -> int:
    while txt[i] != "\n":
        i -= 1
    while txt[i] == "\n":
        i -= 1
    for j in range(i, 0, -1):
        if txt[j] == "\n" and i - j > 10:
            return j + 1


def get_index(line1: int, line2: int, path: str):
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
    return [i_start + 1, i_end -1]


def extract(m_s: MinimalSource) -> str:
    with open(m_s.file_path, mode='r') as data:
        txt = data.read()
        return txt[m_s.first_character_index - 1: m_s.last_character_index - 1]


def get_files(dir: str):
    dir_path = Path(dir)
    files = []
    for f in dir_path.iterdir():
        if not f.is_file():
            d = str(f)
            files.extend(get_files(d))
        elif str(f).endswith(".py") or str(f).endswith(".md"):
            files.append(str(f))
    return files


def save_file(py_chunk, md_chunk):
    if not path.exists(OUTPUT_FILE):
        makedirs(OUTPUT_FILE)
    
    def serialize(chunk):
        result = []
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
