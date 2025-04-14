from dataclasses import dataclass
from app.store.database.sqlalchemy_base import BaseModel

from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, Integer


@dataclass
class User:
    id: int | None
    tg_id: int
    first_name: str

class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    tg_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)

    def to_data(self) -> User:
        return UserModel(
            id=self.id,
            tg_id=self.tg_id,
            first_name=self.first_name,
        )
