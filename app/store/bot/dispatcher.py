from app.store.bot.handlers.answer import AnswerHandler
from app.store.bot.handlers.wait_current_user import WaitCurrentUserHandler
from app.store.tg_api.dataclasses import Update
from app.web.app import Application
from .handlers.start_game import StartGameHandler
from .handlers.stop_game import StopGameHandler
from .handlers.rules import RulesHandler

class CommandDispatcher:
    def __init__(self, app: "Application"):
        self.app = app
        self.handlers = {
            '/start_game': StartGameHandler,
            '/stop_game': StopGameHandler,
            '/start_game@StoKOdnomuBot': StartGameHandler,
            '/stop_game@StoKOdnomuBot': StopGameHandler,
            '/rules': RulesHandler,
            '/rules@StoKOdnomuBot': RulesHandler,
        }

    async def dispatch(self, update: Update):
        message = update.object.message
        command = message.text
        msg_type = message.type

        handler_cls = self.handlers.get(command)
        if handler_cls:
            handler = handler_cls(app=self.app, update=update)
            await handler.handle()

        if msg_type == 'callback_query':
            handler = WaitCurrentUserHandler(app=self.app, update=update)
            await handler.handle()
            return
        
        if msg_type == 'text':
            handler = AnswerHandler(app=self.app, update=update)
            await handler.handle()