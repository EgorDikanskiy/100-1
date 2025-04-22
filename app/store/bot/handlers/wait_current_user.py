import json
from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message

class WaitCurrentUserHandler(BaseCommandHandler):
    async def handle(self):
        upd = self.update.object.message
        active_round = await self.app.store.game_rounds.get_active_round_by_chat_id(upd.chat_id)
        user = await self.app.store.users.get_user_by_tg_id(upd.user_id)
        player_score_active = await self.app.store.game_scores.get_player_status(player_id=user.id, game_id=active_round.game_id)
        if player_score_active:
            round = await self.app.store.game_rounds.update_round(round_id=active_round.id, current_player_id=upd.user_id)
            await self.app.store.tg_api.send_message(
                    Message(chat_id=self.chat_id, text=f"Отвечает {user.first_name}")
                )
            await self.app.store.tg_api.edit_message_reply_markup(upd.chat_id, upd.id)
        
        
        