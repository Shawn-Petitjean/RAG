<<<<<<< HEAD
from pydantic import BaseModel, Field
from typing import List


=======
>>>>>>> refs/remotes/origin/master
class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda:str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    answer: str


class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]
<<<<<<< HEAD

def test(li: str):
    truc = "ca a interet a fonctionner sa mere"
    calcule1 = 456
    calcule2 = 987677
    calcule2 = calcule2 / 4
    for c in truc:
        calcule1 += 1
        if c == 's':
            calcule2 += 5
    if c == 'w':
        calcule2 += 3
    text = "asaaaaaaaaaaaaaaaaaaaasssssss"
    text += "ihbuebfusblknsjf;nseipfusifbusef"
    text += "idoyawduyvauuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
    marche = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    marche1 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    marche2 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    marche3 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    marche4 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    for c in truc:
        calcule1 += 1
        if c == 's':
            calcule2 += 5
            truc = "ca a interet a fonctionner sa mere?????????"
    marche_fin = "asiybbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    marche2 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    marche3 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    marche4 = ("sssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",
    "ssssssssssssssssssssssssssssssssss")
    return int
=======
>>>>>>> refs/remotes/origin/master
