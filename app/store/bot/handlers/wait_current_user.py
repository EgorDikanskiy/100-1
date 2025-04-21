import json
from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message

class WaitCurrentUserHandler(BaseCommandHandler):
    async def handle(self):
        upd = self.update.object.message
        user = await self.app.store.users.get_user_by_tg_id(upd.user_id)
        active_round = await self.app.store.game_rounds.get_active_round_by_chat_id(upd.chat_id)
        round = await self.app.store.game_rounds.update_round(round_id=active_round.id, current_player_id=upd.user_id)
        current_player = await self.app.store.users.get_user_by_tg_id(tg_id=round.current_player_id)
        await self.app.store.game_scores.update_player_status(current_player.id, active_round.game_id, True)
        await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text=f"Отвечает {current_player.first_name}")
            )
        await self.app.store.tg_api.edit_message_reply_markup(upd.chat_id, upd.id)

        



        # game = await self.app.store.game.get_game_by_chat_id(chat_id=upd.chat_id)
        # if game.is_active:
        #     if upd.user_id == active_round.current_player_id:
        #         print("Всё ок")
        #     else:
        #         print("Ты дебил")
        #     print('nkdnljvnsljdjvlose')

        