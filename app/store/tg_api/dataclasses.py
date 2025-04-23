from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    chat_id: int
    text: str
    reply_markup: Any | None = None


@dataclass
class UpdateMessage:
    chat_id: int
    id: int
    type: str
    user_id: int | None = None
    text: str | None = None
    new_user_tg_id: int | None = None
    new_user_first_name: str | None = None


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject
