from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message

class StopGameHandler(BaseCommandHandler):
    async def handle(self):
        game = await self.app.store.game.get_game_by_chat_id(chat_id=self.chat_id)
        if not game:
            return

        if game.is_active:
            await self.app.store.game.update_game_is_active(
                game_id=game.id, new_status=False
            )
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="Игра закончилась")
            )
        else:
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="Игра не активна")
            )
