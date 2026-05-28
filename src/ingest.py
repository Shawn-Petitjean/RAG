from pathlib import Path
<<<<<<< HEAD
from .chunking import py_chunk
from .data_model import MinimalSource


def files_dispatch(files: list[str]):
    py_files = [file for file in files if file.endswith(".py")]
    md_files = [file for file in files if file.endswith(".md")]
    py_m_s = [MinimalSource]
    md_m_s = [MinimalSource]
    m_s = (py_chunk("/home/shapetit/Documents/42/C_4/RAG/src/data_model.py"))
    # for file in py_files:
    #     py_m_s.extend(py_chunk(file))


def get_files(dir: str) -> list[str | None]:
=======


def get_files(dir: str):
>>>>>>> refs/remotes/origin/master
    dir_path = Path(dir)
    files = []
    for f in dir_path.iterdir():
        if not f.is_file():
            d = str(f)
            files.extend(get_files(d))
        elif str(f).endswith(".py") or str(f).endswith(".md"):
            files.append(str(f))
    return files
