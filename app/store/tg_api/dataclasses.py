from dataclasses import dataclass


@dataclass
class Message:
    chat_id: int
    text: str


@dataclass
class UpdateMessage:
    from_id: int
    text: str
    id: int


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject
