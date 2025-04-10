from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from sqlalchemy import BigInteger, Column, String

from app.store.database.sqlalchemy_base import BaseModel


@dataclass
class Admin:
    id: int
    email: str
    password: str | None = None

    @staticmethod
    def hash_password(password: str):
        return sha256(password.encode()).hexdigest()

    def is_correct_password(self, password: str):
        return self.hash_password(password) == self.password

    @classmethod
    def admin_from_session(cls, session: dict | None) -> Admin | None:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])


class AdminModel(BaseModel):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    def to_data(self) -> Admin:
        return Admin(id=self.id, email=self.email, password=self.password)
