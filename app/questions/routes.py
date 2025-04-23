from aiohttp.web_app import Application

from app.questions.views import (
    AnswerAddView,
    AnswerDeleteView,
    AnswerGetView,
    AnswerUpdateView,
    QuestionAddView,
    QuestionDeleteView,
    QuestionGetView,
    QuestionUpdateView,
)


def setup_routes(app: Application):
    app.router.add_view("/add_question", QuestionAddView)
    app.router.add_view("/get_question", QuestionGetView)
    app.router.add_view("/delete_question", QuestionDeleteView)
    app.router.add_view("/update_question", QuestionUpdateView)
    app.router.add_view("/add_answer", AnswerAddView)
    app.router.add_view("/get_answers", AnswerGetView)
    app.router.add_view("/delete_answer", AnswerDeleteView)
    app.router.add_view("/update_answer", AnswerUpdateView)
