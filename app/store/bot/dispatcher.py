from app.store.tg_api.dataclasses import Update
from .handlers.start_game import StartGameHandler
from .handlers.stop_game import StopGameHandler

class CommandDispatcher:
    def __init__(self, app):
        self.app = app
        self.handlers = {
            '/start_game': StartGameHandler,
            '/stop_game': StopGameHandler,
        }

    async def dispatch(self, update: Update):
        message = update.object.message
        command = message.text

        handler_cls = self.handlers.get(command)
        if handler_cls:
            handler = handler_cls(app=self.app, update=update)
            await handler.handle()