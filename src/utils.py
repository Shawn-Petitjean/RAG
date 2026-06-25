from .data_model import MinimalSource
from pathlib import Path
import json
import re
from os import path, makedirs
from typing import Any
from .config import (
                     OUTPUT_CODE,
                     OUTPUT_DOCS,
                     OUTPUT_FILE,
                    )


def get_index(line1: int, line2: int, path: str) -> list[int]:
    """Get the index of the line given.

    Args:
        line1: the num of the first line to find the index.
        line2: the num of the last line to find the index.
        path: path of the file we need to find the index.

    Returns:
        return a list with the two index of the line given
    """
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
    """Extract the txt of the minimal_source.

    Args:
        MinimalSource: Minimal source
        that contain path end index of start and end.

    Returns:
        return the extracted text
    """
    with open(m_s.file_path, mode='r') as data:
        txt = data.read()
        return txt[m_s.first_character_index - 1: m_s.last_character_index - 1]


def get_files(dir: str) -> list[str]:
    """ Recursive algo to find all the python an markdown inside a file.

    Args:
        dir: the directory where we need to find the py and md files

    Returns:
        return the path of py and md files found
    """
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
    """ Save the chunk find inside a json.

    Args:
        py_chunk: list of python chunk.
        md_chunk: list of markdown chunk

    Returns:
        return the path of py and md files found
    """
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
    """ open file and return all the chunk that been saved.

    Returns:
        return all the chunk
    """
    with open(OUTPUT_DOCS, 'r') as doc_data:
        docs = json.load(doc_data)
    with open(OUTPUT_CODE, 'r') as cod_data:
        code = json.load(cod_data)
    docs.extend(code)
    return docs


def preprocess_append(text: str) -> str:
    """Expand technical tokens by appending their split forms to the text.

    For each word containing snake_case or camelCase patterns, the original
    word is kept and its split version is appended alongside it. This allows
    BM25 to match both 'load_model_weights' and individual terms like
    'load', 'model', 'weights'.

    Args:
        text: Raw text to preprocess.

    Returns:
        Expanded text with split tokens appended after their original forms.

    Examples:
        >>> preprocess_append("call myFunction and load_weights")
        "call myFunction my Function and load_weights load weights"
    """
    words = text.split()
    new_words = []
    for w in words:
        new_words.append(w)
        has_under = "_" in w
        has_camel = re.search(r'([a-z0-9])([A-Z])', w) is not None
        if has_under or has_camel:
            split_w = w
            if has_camel:
                split_w = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', split_w)
            if has_under:
                split_w = split_w.replace("_", " ")
            new_words.append(split_w)
    return " ".join(new_words)


def preprocess_with_path(text: str, file_path: str) -> str:
    """Preprocess text and enrich it with tokenized file path components.

    Applies `preprocess_append` to the main text, then splits the file path
    on common separators (/, ., _, -) and expands any camelCase parts.
    The resulting path tokens are appended to the text so that BM25 can
    match queries containing directory names, file names, or extensions.

    Args:
        text: Raw chunk content to preprocess.
        file_path: Path of the source file (e.g. 'src/utils/myParser.py').

    Returns:
        Preprocessed text with path tokens appended.

    Examples:
        >>> preprocess_with_path("parse tokens", "src/utils/myParser.py")
        "parse tokens ... src utils my Parser py"
    """
    text_preprocessed = preprocess_append(text)
    path_parts = re.split(r'[/._\-]', file_path)
    path_words = []
    for part in path_parts:
        part_split = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', part)
        path_words.append(part_split)
    path_str = " ".join(path_words)
    return text_preprocessed + " " + path_str
