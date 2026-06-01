import ast
from utils import get_index
from data_model import MinimalSource


def lst_line(txt: str, i: int) -> int:
    while txt[i] != "\n":
        i -= 1
    while txt[i] == "\n":
        i -= 1
    for j in range(i, 0, -1):
        if txt[j] == "\n" and i - j > 20:
            return j + 1


def cut_py(txt: str, first_i: int, last_i: int, file: str):
    list_MS = []
    end_i = first_i
    start_i = first_i
    for i in range(first_i, last_i + 1):
        if end_i - start_i > 2000:
            end_i = lst_line(txt, end_i)
            list_MS.extend(MinimalSource(file_path=file,
                                            first_character_index=start_i,
                                            last_character_index=end_i))
            start_i = lst_line(txt, end_i)
        if last_i - start_i < 2000:
            break
        if txt[i] == "\n":
            end_i = i
    list_MS.extend(MinimalSource(file_path=file,
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
                    l_m_s.extend(MinimalSource(file_path=file,
                                            first_character_index=i_line[0],
                                            last_character_index=i_line[1]))
                else:
                    print(i_line)
                    l_m_s.extend(cut_py(txt, i_line[0], i_line[1], file))
    return l_m_s


# tree = ast.parse(s)
# for node in ast.walk(tree):
#     if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
#         print(f"Type: {type(node).__name__}")
#         print(f"Nom: {node.name}")
#         print(f"Ligne début: {node.lineno}")
#         print(f"Ligne fin: {node.end_lineno}")
#         print("---")