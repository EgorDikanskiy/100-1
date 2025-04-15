import typing

from app.game.views import GameAddView, GameGetView, GamePatchView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/add_game", GameAddView)
    app.router.add_view("/get_game", GameGetView)
    app.router.add_view("/update_game", GamePatchView)