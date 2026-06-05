from .data_model import MinimalSource


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
    
