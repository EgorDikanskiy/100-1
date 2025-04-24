from app.store.bot.handlers.answer import AnswerHandler
from app.store.bot.handlers.answer_request import AnswerRequestHandler
from app.store.bot.handlers.next_round import NextRoundHandler
from app.store.bot.handlers.join_game import JoinGameHandler
from app.store.tg_api.dataclasses import Message, Update
from app.web.app import Application

from .handlers.rules import RulesHandler
from .handlers.start_game import StartGameHandler
from .handlers.stop_game import StopGameHandler


class CommandDispatcher:
    def __init__(self, app: "Application"):
        self.app = app
        self.handlers = {
            "/start_game": StartGameHandler,
            "/stop_game": StopGameHandler,
            "/start_game@StoKOdnomuBot": StartGameHandler,
            "/stop_game@StoKOdnomuBot": StopGameHandler,
            "/rules": RulesHandler,
            "/rules@StoKOdnomuBot": RulesHandler,
        }

    async def dispatch(self, update: Update):
        message = update.object.message
        msg_type = message.type

        if msg_type == "callback_query":
            callback_data = message.callback_data
            if callback_data == "join_game":
                handler = JoinGameHandler(app=self.app, update=update)
                await handler.handle()
            elif callback_data == "want_answer":
                handler = AnswerRequestHandler(app=self.app, update=update)
                await handler.handle()
            elif callback_data in ["yes_button", "no_button"]:
                handler = NextRoundHandler(app=self.app, update=update)
                await handler.handle()
            return

        if msg_type == "text":
            command = message.text
            handler_cls = self.handlers.get(command)
            if handler_cls:
                handler = handler_cls(app=self.app, update=update)
                await handler.handle()
            else:
                handler = AnswerHandler(app=self.app, update=update)
                await handler.handle()
