import typing
from logging import getLogger

from app.store.tg_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("telegram_handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            original_text = update.object.message.text
            chat_id = update.object.message.from_id
            echo_message = Message(chat_id=chat_id, text=original_text)
            await self.app.store.tg_api.send_message(echo_message)
