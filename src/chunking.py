import ast
from .utils import get_index
from .data_model import MinimalSource


def cut_py(txt: str, start_i: int, end_i: int, file: str):
     list_MS = []
     last_i = 0
     first_i = start_i
     for i in range(start_i, end_i):
        if last_i - start_i > 2000:
            list_MS.extend(MinimalSource(file_path=file,
                                         first_character_index=i_line[0],
                                         last_character_index=i_line[1]))
                file
            ))
        elif txt[i] == "\n":
            last_i = i



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
                    print(l_txt)
                    l_m_s.extend(cut_py(txt, i_line[0], i_line[0], file))
    return l_m_s


# tree = ast.parse(s)
# for node in ast.walk(tree):
#     if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
#         print(f"Type: {type(node).__name__}")
#         print(f"Nom: {node.name}")
#         print(f"Ligne début: {node.lineno}")
#         print(f"Ligne fin: {node.end_lineno}")
#         print("---")