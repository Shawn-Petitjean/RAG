from pathlib import Path
from .chunking import py_chunk, md_chunk
from .data_model import MinimalSource


def files_dispatch(files: list[str]):
    py_files = [file for file in files if file.endswith(".py")]
    md_files = [file for file in files if file.endswith(".md")]
    py_m_s = [MinimalSource]
    md_m_s = [MinimalSource]
    m_s = (md_chunk("/home/shapetit/Documents/42/C_4/RAG/vllm-0.10.1/CODE_OF_CONDUCT.md"))


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
