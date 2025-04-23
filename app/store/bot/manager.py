import typing
from logging import getLogger

from .dispatcher import CommandDispatcher

if typing.TYPE_CHECKING:
    from app.store.tg_api.dataclasses import Update
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("telegram_handler")
        self.dispatcher = CommandDispatcher(app)

    async def handle_updates(self, updates: list["Update"]):
        for update in updates:
            type_update = update.object.message.type

            if type_update == "add_member":
                await self._handle_new_member(update)
            elif type_update == "text" or type_update == "callback_query":
                await self.dispatcher.dispatch(update)

    async def _handle_new_member(self, update: "Update"):
        tg_id = update.object.message.new_user_tg_id
        first_name = update.object.message.new_user_first_name

        if not await self.app.store.users.get_user_by_tg_id(tg_id):
            await self.app.store.users.create_user(
                tg_id=tg_id, first_name=first_name
            )
