from datetime import UTC, datetime
import asyncio
import random

from app.store.tg_api.dataclasses import Message

from ..base import BaseCommandHandler
from ..constants import want_answer_keyboard, yes_no_keyboard


class NextRoundHandler(BaseCommandHandler):
    async def handle(self):
        callback_data = self.update.object.message.callback_data
        
        if callback_data == "yes_button":
            # Get the current game
            game = await self.app.store.game.get_game_by_chat_id(
                chat_id=self.chat_id
            )
            if not game or not game.is_active:
                return

            # Create a new round
            round = await self.app.store.game_rounds.create_game_round(
                game_id=game.id,
                created_at=datetime.now(UTC)
            )
            
            # Get all questions
            questions = await self.app.store.questions.get_all_questions()
            if not questions:
                await self.app.store.tg_api.send_message(
                    Message(
                        chat_id=self.chat_id,
                        text="Нет доступных вопросов для игры."
                    )
                )
                await self.app.store.game.update_game_is_active(game.id, False)
                return
                
            # Select 3 random questions
            selected_questions = random.sample(questions, min(3, len(questions)))
            
            # Create round questions and set the first question as current
            first_question = selected_questions[0]
            round_question = await self.app.store.round_questions.create_round_question(
                round_id=round.id,
                question_id=first_question.id
            )
            
            # Create round_question_answers for the first question
            for answer in first_question.answers:
                await self.app.store.round_question_answers.create_round_question_answer(
                    round_question_id=round_question.id,
                    answer_id=answer.id,
                    is_found=False
                )
            
            # Update round with the first question
            await self.app.store.game_rounds.update_round(
                round_id=round.id,
                question_id=round_question.id
            )
            
            # Create round questions for remaining questions
            for question in selected_questions[1:]:
                round_question = await self.app.store.round_questions.create_round_question(
                    round_id=round.id,
                    question_id=question.id
                )
                
                # Create round_question_answers for each answer
                for answer in question.answers:
                    await self.app.store.round_question_answers.create_round_question_answer(
                        round_question_id=round_question.id,
                        answer_id=answer.id,
                        is_found=False
                    )
            
            # Start the first question
            await self._start_next_question(round)
            
        elif callback_data == "no_button":
            # Get the current game
            game = await self.app.store.game.get_game_by_chat_id(
                chat_id=self.chat_id
            )
            if game and game.is_active:
                # Deactivate the game
                await self.app.store.game.update_game_is_active(game.id, False)
                await self.app.store.tg_api.send_message(
                    Message(
                        chat_id=self.chat_id,
                        text="Игра завершена! Спасибо за участие!"
                    )
                )
            else:
                await self.app.store.tg_api.send_message(
                    Message(
                        chat_id=self.chat_id,
                        text="Активной игры не найдено."
                    )
                )

    async def _start_next_question(self, round):
        if not round:
            return
            
        # Get all round questions that haven't been answered yet
        round_questions = await self.app.store.round_questions.get_round_questions_by_id(round_id=round.id)
        unanswered_questions = [rq for rq in round_questions if not rq.is_found]
        
        if not unanswered_questions:
            # All questions answered, show statistics and ask for next round
            await self._show_round_statistics(round.game_id)
            await self._ask_for_next_round(round.game_id)
            return
            
        # Get the next question
        next_question = unanswered_questions[0]
        question = await self.app.store.questions.get_question_by_id(next_question.question_id)
        
        # Update the round with the current question_id
        await self.app.store.game_rounds.update_round(
            round_id=round.id,
            question_id=next_question.id
        )
        
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text=f"Вопрос: {question.question}"
            )
        )
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text="Жмякайте!",
                reply_markup=want_answer_keyboard,
            )
        )

    async def _show_round_statistics(self, game_id):
        scores = await self.app.store.game_scores.get_scores_by_game(game_id)
        stats_text = "Статистика раунда:\n\n"
        for score in scores:
            player = await self.app.store.users.get_user_by_id(score.player_id)
            stats_text += f"{player.first_name}: {score.score} очков\n"
            
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text=stats_text
            )
        )

    async def _ask_for_next_round(self, game_id):
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text="Хотите сыграть ещё один раунд?",
                reply_markup=yes_no_keyboard
            )
        ) 