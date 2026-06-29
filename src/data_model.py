from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid


class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question_id: str
    question_str: str = Field(validation_alias="question")
    retrieved_sources: List[MinimalSource]

    @property
    def question(self) -> str:
        return self.question_str

    @question.setter
    def question(self, value: str) -> None:
        self.question_str = value


class MinimalAnswer(MinimalSearchResults):
    answer: str


class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    search_results: List[MinimalAnswer]
