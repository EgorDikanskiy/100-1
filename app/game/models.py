from dataclasses import dataclass
from datetime import datetime
from app.store.database.sqlalchemy_base import BaseModel

from sqlalchemy import Column, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship


@dataclass
class Game:
    id: int | None
    chat_id: int
    is_active: bool
    created_at: datetime


class GameModel(BaseModel):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    scores = relationship("GameScoreModel", back_populates="game", cascade="all, delete", lazy="selectin")

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

    __table_args__ = (UniqueConstraint("player_id", "game_id", name="uix_player_game"),)

    def to_data(self) -> GameScore:
        return GameScore(
            id=self.id,
            player_id=self.player_id,
            game_id=self.game_id,
            score=self.score,
            is_active=self.is_active
        )
