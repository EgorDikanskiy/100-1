from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from app.store.database.sqlalchemy_base import BaseModel


@dataclass
class Game:
    id: int | None
    chat_id: int
    is_active: bool
    created_at: datetime


class GameModel(BaseModel):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    scores = relationship(
        "GameScoreModel",
        back_populates="game",
        cascade="all, delete",
        lazy="selectin",
    )
    rounds = relationship(
        "GameRoundModel",
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_data(self) -> Game:
        return Game(
            id=self.id,
            chat_id=self.chat_id,
            is_active=self.is_active,
            created_at=self.created_at,
        )


@dataclass
class GameScore:
    id: int | None
    player_id: int
    score: int
    is_active: bool
    game_id: int


class GameScoreModel(BaseModel):
    __tablename__ = "game_scores"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    score = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    player = relationship("UserModel", lazy="selectin")
    game = relationship("GameModel", back_populates="scores", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("player_id", "game_id", name="uix_player_game"),
    )

    def to_data(self) -> GameScore:
        return GameScore(
            id=self.id,
            player_id=self.player_id,
            game_id=self.game_id,
            score=self.score,
            is_active=self.is_active,
        )


@dataclass
class GameRound:
    id: int | None
    game_id: int
    question_id: int
    current_player_id: int
    is_active: bool
    created_at: datetime


class GameRoundModel(BaseModel):
    __tablename__ = "game_rounds"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    question_id = Column(Integer, nullable=True)
    current_player_id = Column(BigInteger, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    game = relationship("GameModel", back_populates="rounds")
    round_questions = relationship(
        "RoundQuestionModel",
        back_populates="game_round",
        cascade="all, delete-orphan",
        lazy="selectin",
        primaryjoin="GameRoundModel.id == RoundQuestionModel.round_id",
    )

    def to_data(self) -> GameRound:
        return GameRound(
            id=self.id,
            game_id=self.game_id,
            question_id=self.question_id,
            current_player_id=self.current_player_id,
            is_active=self.is_active,
            created_at=self.created_at,
        )


@dataclass
class RoundQuestion:
    id: int | None
    round_id: int
    question_id: int
    is_found: bool
    answers: list["RoundQuestionAnswer"] | None = None


class RoundQuestionModel(BaseModel):
    __tablename__ = "round_questions"

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("game_rounds.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    is_found = Column(Boolean, default=False, nullable=False)

    game_round = relationship(
        "GameRoundModel", back_populates="round_questions", lazy="selectin"
    )
    question = relationship("QuestionModel", lazy="selectin")
    answers = relationship(
        "RoundQuestionAnswerModel",
        back_populates="round_question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_data(self) -> RoundQuestion:
        return RoundQuestion(
            id=self.id,
            round_id=self.round_id,
            question_id=self.question_id,
            is_found=self.is_found,
            answers=[],
        )


@dataclass
class RoundQuestionAnswer:
    id: int | None
    round_question_id: int
    answer_id: int
    is_found: bool


class RoundQuestionAnswerModel(BaseModel):
    __tablename__ = "round_question_answers"

    id = Column(Integer, primary_key=True)
    round_question_id = Column(
        Integer, ForeignKey("round_questions.id"), nullable=False
    )
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)
    is_found = Column(Boolean, default=False, nullable=False)

    round_question = relationship(
        "RoundQuestionModel", back_populates="answers", lazy="selectin"
    )
    answer = relationship("AnswerModel", lazy="selectin")

    def to_data(self) -> RoundQuestionAnswer:
        return RoundQuestionAnswer(
            id=self.id,
            round_question_id=self.round_question_id,
            answer_id=self.answer_id,
            is_found=self.is_found,
        )
