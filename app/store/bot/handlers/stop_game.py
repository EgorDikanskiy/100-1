from app.store.tg_api.dataclasses import Message

from ..base import BaseCommandHandler


class StopGameHandler(BaseCommandHandler):
    async def handle(self):
        game = await self.app.store.game.get_game_by_chat_id(
            chat_id=self.chat_id
        )
        if not game:
            return

        if game.is_active:
            await self.app.store.game.update_game_is_active(
                game_id=game.id, new_status=False
            )
            rounds = (
                await self.app.store.game_rounds.get_game_rounds_by_game_id(
                    game_id=game.id
                )
            )
            for el in rounds:
                await self.app.store.game_rounds.update_round(
                    round_id=el.id, is_active=False
                )
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="🏁 Игра закончилась")
            )
        else:
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="❌ Игра не активна")
            )
            await self.app.store.tg_api.edit_message_reply_markup(
                self.chat_id, self.update.object.message.id
            )
