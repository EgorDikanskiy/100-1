from datetime import UTC, datetime
from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message
from ..utils.helpers import create_round_with_question
from ..constants import *

class StartGameHandler(BaseCommandHandler):
    async def handle(self):
        game = await self.app.store.game.get_game_by_chat_id(chat_id=self.chat_id)

        if game and game.is_active:
            await self._handle_active_game(game)
        else:
            game = await self.app.store.game.create_game(
                chat_id=self.chat_id, is_active=True, created_at=datetime.now(UTC)
            )
            users = await self.app.store.users.get_all_users()
            for user in users:
                await self.app.store.game_scores.create_game_score(user.id, game.id)
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="Игра началась")
            )
            question = await create_round_with_question(app=self.app, game_id=game.id, chat_id=self.chat_id)
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text=f"Вопрос: {question.question}")
            )
            await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text="Жмякайте!",
                reply_markup=want_answer_keyboard
            )
            )


    async def _handle_active_game(self, game):
        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text="Игра активна")
        )
        rounds = await self.app.store.game_rounds.get_game_rounds_by_game_id(game_id=game.id)
        if not any(r.is_active for r in rounds):
            round = await create_round_with_question(app=self.app, game_id=game.id, chat_id=self.chat_id)
        else:
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="Есть активный раунд")
            )
            round = await self.app.store.game_rounds.get_active_round_by_chat_id(self.chat_id)
        round_question = await self.app.store.round_questions.get_round_question_by_id(rq_id=round.question_id)
        question = await self.app.store.questions.get_question_by_id(question_id=round_question.question_id)
        await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text=f"Текущий вопрос: {question.question}")
            )
        if round.current_player_id:
            current_player = await self.app.store.users.get_user_by_tg_id(tg_id=round.current_player_id)
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text=f"Отвечает {current_player.first_name}")
            )
        else:
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="Жмякайте!",
                    reply_markup=want_answer_keyboard
                )
                )
        

        
        


            
