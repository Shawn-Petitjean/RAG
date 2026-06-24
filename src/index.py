from .data_model import MinimalSource
from .config import OVLAP


def py_chunking(file: str, m_char: int) -> list[MinimalSource]:
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


def md_chunking(file: str, m_char: int) -> list[MinimalSource]:
    return py_chunking(file, m_char)
