from dataclasses import dataclass

from sqlalchemy import BigInteger, Column, Integer, String, BIGINT
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


@dataclass
class User:
    id: int | None
    tg_id: int
    first_name: str


class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    tg_id = Column(BIGINT, nullable=False)
    first_name = Column(String, nullable=False)

    game_scores = relationship("GameScoreModel", back_populates="player")

    def to_data(self) -> User:
        return UserModel(
            id=self.id,
            tg_id=self.tg_id,
            first_name=self.first_name,
        )
