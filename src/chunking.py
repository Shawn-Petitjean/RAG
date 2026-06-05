import ast
from .utils import get_index, extract
from .data_model import MinimalSource


def lst_line(txt: str, i: int) -> int:
    while txt[i] != "\n":
        i -= 1
    while txt[i] == "\n":
        i -= 1
    for j in range(i, 0, -1):
        if txt[j] == "\n" and i - j > 10:
            return j + 1


def cut(txt: str, first_i: int, last_i: int, file: str):
    list_MS = []
    end_i = first_i
    start_i = first_i
    for i in range(first_i, last_i + 1):
        if end_i - start_i > 2000:
            end_i = lst_line(txt, end_i)
            list_MS.append(MinimalSource(file_path=file,
                                         first_character_index=start_i,
                                         last_character_index=end_i))
            start_i = lst_line(txt, end_i)
        if last_i - start_i < 2000:
            break
        if txt[i] == "\n":
            end_i = i
    list_MS.append(MinimalSource(file_path=file,
                                 first_character_index=start_i,
                                 last_character_index=last_i))
    return list_MS


def py_chunk(file: str):
    l_m_s = []
    with open(file, mode='r') as data:
        txt = data.read()
        tree = ast.parse(txt)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                i_line = get_index(node.lineno, node.end_lineno, file)
                if i_line[1] - i_line[0] <= 2000:
                    l_m_s.append(MinimalSource(file_path=file,
                                               first_character_index=i_line[0],
                                               last_character_index=i_line[1]))
                else:
                    l_m_s.append(cut(txt, i_line[0], i_line[1], file))
    return l_m_s


def md_chunk(file: str):
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
                    if i_line[1] - i_line[0] <= 2000:
                        l_m_s.append(MinimalSource(file_path=file,
                                                   first_character_index=i_line[0],
                                                   last_character_index=i_line[1]))
                        start = end - 2
                    else:
                        l_m_s.append(cut(txt, i_line[0], i_line[1], file))
                        start = end - 2
    i_line = get_index(start, end - 1, file)
    if i_line[1] - i_line[0] <= 2000:
        l_m_s.append(MinimalSource(file_path=file,
                                   first_character_index=i_line[0],
                                   last_character_index=i_line[1]))
    else:
        l_m_s.append(cut(txt, i_line[0], i_line[1], file))
    for m_s in l_m_s:
        print(extract(m_s))
        print("||||||||||||||||||||||||||||||||||||||||||||")
    return l_m_s

