from dataclasses import dataclass
from datetime import datetime
from app.store.database.sqlalchemy_base import BaseModel

from sqlalchemy import Column, Integer, Boolean, DateTime


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

    def to_data(self) -> Game:
        return Game(
            id=self.id,
            chat_id=self.chat_id,
            is_active=self.is_active,
            created_at=self.created_at,
        )
