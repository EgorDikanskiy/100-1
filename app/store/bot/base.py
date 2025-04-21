from abc import ABC, abstractmethod
from app.store.tg_api.dataclasses import Update
from app.web.app import Application

class BaseCommandHandler(ABC):
    def __init__(self, app: "Application", update: Update):
        self.app = app
        self.update = update
        self.chat_id = update.object.message.chat_id

    @abstractmethod
    async def handle(self):
        pass