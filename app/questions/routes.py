from aiohttp.web_app import Application

from app.questions.views import (
    AnswerAddView,
    AnswerGetView,
    QuestionAddView,
    QuestionGetView,
)


def setup_routes(app: Application):
    app.router.add_view("/add_question", QuestionAddView)
    app.router.add_view("/get_question", QuestionGetView)
    app.router.add_view("/add_answer", AnswerAddView)
    app.router.add_view("/get_answers", AnswerGetView)
