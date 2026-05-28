def get_index(line1: int, line2: int, path: str):

    with open(path, mode='r') as data:
        s = data.readlines()
        k = data.read()
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
