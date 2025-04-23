from aiohttp.web_app import Application

from app.users.views import UserAddView, UserGetView

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    app.router.add_view("/add_user", UserAddView)
    app.router.add_view("/get_user", UserGetView)
