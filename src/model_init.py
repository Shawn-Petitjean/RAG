from .data_model import UnansweredQuestion
import json


def init_question(file: str):
    l_u_q = []
    with open(file) as f:
        data = json.load(f)
        for dic in data:
            print(dic)
            print("|||||||||||||||||||||||||||||")