import typing

from app.game.views import GameAddView, GameGetView, GamePatchView, GameRoundAddView, GameRoundGetView, GameRoundUpdateView, GameScoreAddView, GameScoreListView, RoundQuestionAddView, RoundQuestionAnswerAddView, RoundQuestionAnswerGetView, RoundQuestionGetView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/add_game", GameAddView)
    app.router.add_view("/get_game", GameGetView)
    app.router.add_view("/update_game", GamePatchView)
    app.router.add_view("/add_game_score", GameScoreAddView)
    app.router.add_view("/game_scores", GameScoreListView)
    app.router.add_view("/add_game_rounds", GameRoundAddView)
    app.router.add_view("/get_game_rounds", GameRoundGetView)
    app.router.add_view("/update_game_rounds", GameRoundUpdateView)
    app.router.add_view("/round_questions.add", RoundQuestionAddView)
    app.router.add_view("/round_questions.get", RoundQuestionGetView)
    app.router.add_view("/round_question_answers.add", RoundQuestionAnswerAddView)
    app.router.add_view("/round_question_answers.get", RoundQuestionAnswerGetView)