import typing

from app.game.views import GameAddView, GameGetView, GamePatchView, GameScoreAddView, GameScoreListView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/add_game", GameAddView)
    app.router.add_view("/get_game", GameGetView)
    app.router.add_view("/update_game", GamePatchView)
    app.router.add_view("/add_game_score", GameScoreAddView)
    app.router.add_view("/game_scores", GameScoreListView)