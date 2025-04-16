import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.game.accessor import (
            GameAccessor,
            GameRoundAccessor,
            GameScoreAccessor,
            RoundQuestionAccessor,
            RoundQuestionAnswerAccessor,
        )
        from app.questions.accessors import AnswerAccessor, QuestionAccessor
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.tg_api.accessor import TelegramApiAccessor
        from app.users.accessor import UserAccessor

        self.admins = AdminAccessor(app)
        self.tg_api = TelegramApiAccessor(app)
        self.bots_manager = BotManager(app)
        self.users = UserAccessor(app)
        self.game = GameAccessor(app)
        self.game_scores = GameScoreAccessor(app)
        self.game_rounds = GameRoundAccessor(app)
        self.round_questions = RoundQuestionAccessor(app)
        self.round_question_answers = RoundQuestionAnswerAccessor(app)
        self.questions = QuestionAccessor(app)
        self.answers = AnswerAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
