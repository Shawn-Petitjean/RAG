import ast
from .utils import get_index, extract, lst_line
from .data_model import MinimalSource
from .config import OUTPUT_CODE, OUTPUT_DOCS, OVLAP



def cut(txt: str, first_i: int, last_i: int, file: str, m_char: int):
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


def py_chunking(file: str, m_char: int):
    l_m_s = []
    with open(file, mode='r') as data:
        txt = data.read()
        tree = ast.parse(txt)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                i_line = get_index(node.lineno, node.end_lineno, file)
                if i_line[1] - i_line[0] <= m_char:
                    l_m_s.append(MinimalSource(file_path=file,
                                               first_character_index=i_line[0],
                                               last_character_index=i_line[1]))
                else:
                    new = cut(txt, i_line[0], i_line[1], file, m_char)
                    for ch in new:
                        l_m_s.append(ch)
    return l_m_s


def md_chunking(file: str, m_char: int):
    l_m_s = []
    with open(file, mode='r') as data:
        txt = data.read()
        start = 0
        end = 0
        for line in txt.split("\n"):
            end += 1
            if line.startswith("#"):
                if start == 0:
                    start = end
                else:
                    i_line = get_index(start, end - 1, file)
                    if i_line[1] - i_line[0] <= m_char:
                        l_m_s.append(MinimalSource(file_path=file,
                                                   first_character_index=i_line[0],
                                                   last_character_index=i_line[1]))
                        start = end - 2
                    else:
                        new = cut(txt, i_line[0], i_line[1], file, m_char)
                        for ch in new:
                            l_m_s.append(ch)
                        start = end - 2
    i_line = get_index(start, end - 1, file)
    if i_line[1] - i_line[0] <= m_char:
        l_m_s.append(MinimalSource(file_path=file,
                                   first_character_index=i_line[0],
                                   last_character_index=i_line[1]))
    else:
        l_m_s.extend(cut(txt, i_line[0], i_line[1], file, m_char))
    return l_m_s


# def main():
#     s = py_chunking("/home/shapetit/Documents/42/C_4/RAG/vllm-0.10.1/setup.py", 1000)
#     print


# main()
