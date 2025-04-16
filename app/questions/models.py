from dataclasses import dataclass

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


@dataclass
class Answer:
    id: int | None
    question_id: int
    word: str
    score: int


@dataclass
class Question:
    id: int | None
    question: str
    answers: [list[Answer]] | None = None


class QuestionModel(BaseModel):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answers = relationship(
        "AnswerModel",
        back_populates="question",
        cascade="all, delete",
        lazy="selectin",
    )

    def to_data(self) -> Question:
        return Question(id=self.id, question=self.question, answers=[])


class AnswerModel(BaseModel):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    word = Column(String, nullable=False)
    score = Column(Integer, nullable=False)

    question = relationship(
        "QuestionModel", back_populates="answers", lazy="selectin"
    )

    def to_data(self) -> Answer:
        return Answer(
            id=self.id,
            question_id=self.question_id,
            word=self.word,
            score=self.score,
        )
