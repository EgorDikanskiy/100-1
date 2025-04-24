from app.store.tg_api.dataclasses import Message
from ..base import BaseCommandHandler


class AnswerRequestHandler(BaseCommandHandler):
    async def handle(self):
        # Get the current game
        game = await self.app.store.game.get_game_by_chat_id(
            chat_id=self.chat_id
        )
        if not game or not game.is_active:
            return

        # Get the active round
        active_round = await self.app.store.game_rounds.get_active_round_by_chat_id(
            self.chat_id
        )
        if not active_round:
            return

        # Get the current player
        current_player = await self.app.store.users.get_user_by_tg_id(
            tg_id=self.update.object.message.user_id
        )
        if not current_player:
            return

        # Check if player is blocked
        player_status = await self.app.store.game_scores.get_player_status(
            player_id=current_player.id,
            game_id=game.id
        )
        if not player_status:
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text=f"❌ {current_player.first_name}, вы заблокированы!"
                )
            )
            return

        # Check if there's already a current player
        if active_round.current_player_id:
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="❌ Кто-то уже отвечает на этот вопрос!"
                )
            )
            return

        # Set the current player for this round
        await self.app.store.game_rounds.update_round(
            round_id=active_round.id,
            current_player_id=current_player.id
        )

        # Get the current question
        round_questions = await self.app.store.round_questions.get_round_questions_by_id(
            active_round.id
        )
        unanswered_questions = [rq for rq in round_questions if not rq.is_found]
        if not unanswered_questions:
            return

        current_question = unanswered_questions[0]
        question = await self.app.store.questions.get_question_by_id(
            current_question.question_id
        )

        # Notify that this player is answering
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text=f"🎤 Отвечает {current_player.first_name}!\n\n❓ Вопрос: {question.question}"
            )
        )

        # Remove the reply markup from the message
        await self.app.store.tg_api.edit_message_reply_markup(
            self.chat_id, self.update.object.message.id
        ) 