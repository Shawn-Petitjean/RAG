from .data_model import MinimalSource
from .config import OVLAP
from .utils import get_index
import ast


def cut(txt: str, first_i: int, last_i: int, file: str,
        m_char: int) -> list[MinimalSource]:
    """cut the text between first_i and last_i with respecting the m_char.

    Args:
        txt: text given where the index come frome.
        first_i: first index where the cut begin.
        last_i: last index where the cut ending.
        m_char: number of character max a chunk can be.

    Returns:
        list of MinimalSource that contain the chunk cut between the index.
    """
    list_MS = []
    end_i = first_i
    start_i = first_i
    for i in range(first_i, last_i + 1):
        if end_i - start_i == m_char:
            list_MS.append(MinimalSource(file_path=file,
                                         first_character_index=start_i,
                                         last_character_index=end_i))

            start_i = end_i - OVLAP
        elif last_i - start_i < m_char:
            break
        end_i += 1
    list_MS.append(MinimalSource(file_path=file,
                                 first_character_index=start_i,
                                 last_character_index=last_i))
    return list_MS


def py_chunking(file: str, m_char: int) -> list[MinimalSource]:
    """Chunking of a python file with the number of charactere max it can be.

    Args:
        file: path of the py file that gonna be chunk.
        m_char: limit of the char max in a chunk.

    Returns:
        list of MinimalSource that contain the chunk cut in all the file.
    """
    l_m_s = []
    with open(file, mode='r') as data:
        txt = data.read()
        tree = ast.parse(txt)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                end_line = (node.end_lineno if node.end_lineno
                            is not None else node.lineno)
                i_line = get_index(node.lineno, end_line, file)
                if i_line[1] - i_line[0] <= m_char:
                    l_m_s.append(MinimalSource(file_path=file,
                                               first_character_index=i_line[0],
                                               last_character_index=i_line[1]))
                else:
                    new = cut(txt, i_line[0], i_line[1], file, m_char)
                    for ch in new:
                        l_m_s.append(ch)
    return l_m_s


def md_chunking(file: str, m_char: int) -> list[MinimalSource]:
    """Chunking of a markdown file with the number of charactere max it can be.

    Args:
        file: path of the py file that gonna be chunk.
        m_char: limit of the char max in a chunk.

    Returns:
        list of MinimalSource that contain the chunk cut in all the file.
    """
    with open(file, mode='r', encoding='utf-8', errors='ignore') as data:
        content = data.read()

    chunks: list[MinimalSource] = []
    content_len = len(content)
    if content_len == 0:
        return chunks

    # Calculate overlap dynamically based on chunk size
    if m_char >= 2000:
        overlap = 800
    elif m_char >= 1500:
        overlap = 500
    elif m_char >= 1000:
        overlap = 200
    else:
        overlap = OVLAP

    start = 0
    while start < content_len:
        end = min(start + m_char, content_len)
        if end - start < min(100, m_char) and len(chunks) > 0:
            break
        chunks.append(MinimalSource(
            file_path=file,
            first_character_index=start + 1,
            last_character_index=end
        ))
        start += (m_char - overlap)
        if start >= content_len:
            break
    return chunks
