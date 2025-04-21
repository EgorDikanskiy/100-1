import json
from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message

class AnswerHandler(BaseCommandHandler):
    async def handle(self):
        upd = self.update.object.message
        user = await self.app.store.users.get_user_by_tg_id(upd.user_id)
        game = await self.app.store.game.get_game_by_chat_id(chat_id=upd.chat_id)
        active_round = await self.app.store.game_rounds.get_active_round_by_chat_id(chat_id=upd.chat_id)
        if game.is_active and active_round:
            if upd.user_id == active_round.current_player_id:
                answer = await self.app.store.answers.get_answer_by_word(upd.text)
                if answer:
                    await self.app.store.game_scores.update_score(user.id, answer.score)
                    await self.app.store.game_rounds.update_round(active_round.id, current_player_id=0)
                    await self.app.store.tg_api.send_message(Message(chat_id=self.chat_id, text="Это правильный ответ"))
                else:
                    await self.app.store.game_scores.update_player_status(user.id, game.id, False)
                    await self.app.store.game_rounds.update_round(active_round.id, current_player_id=0)
                    await self.app.store.game_scores.update_player_status(user.id, active_round.game_id, False)
                    await self.app.store.tg_api.send_message(Message(chat_id=self.chat_id, text="Это не верный ответ :("))
            else:
                print("Ты дебил")
            
            

        