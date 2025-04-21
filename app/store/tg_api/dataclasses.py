from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Message:
    chat_id: int
    text: str
    reply_markup: Optional[Any] = None


@dataclass
class UpdateMessage:
    chat_id: int
    id: int
    type: str
    user_id: Optional[int] = None
    text: Optional[str] = None
    new_user_tg_id: Optional[int] = None
    new_user_first_name: Optional[str] = None


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject
