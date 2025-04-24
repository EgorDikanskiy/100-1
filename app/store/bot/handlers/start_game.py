import asyncio
import random
from datetime import UTC, datetime

from app.store.tg_api.dataclasses import Message

from ..base import BaseCommandHandler
from ..constants import (
    join_game_keyboard,
    want_answer_keyboard,
    yes_no_keyboard,
)


class StartGameHandler(BaseCommandHandler):
    async def handle(self):
        game = await self.app.store.game.get_game_by_chat_id(
            chat_id=self.chat_id
        )

        if game and game.is_active:
            await self._handle_active_game(game)
        else:
            game = await self.app.store.game.create_game(
                chat_id=self.chat_id,
                is_active=True,
                created_at=datetime.now(UTC),
            )
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="🎮 Начинаем новую игру!\n\nНажмите кнопку ниже, чтобы присоединиться 👇",  # noqa: E501
                    reply_markup=join_game_keyboard,
                )
            )
            self._start_game_task = asyncio.create_task(
                self._start_game_after_delay(game)
            )

    async def _start_game_after_delay(self, game):
        await asyncio.sleep(10)
        if not game or not game.is_active:
            return

        game_scores = await self.app.store.game_scores.get_scores_by_game(
            game.id
        )
        if len(game_scores) < 1:
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="❌ Недостаточно игроков для начала игры. Нужно минимум 1 игрок.",  # noqa: E501
                )
            )
            await self.app.store.game.update_game_is_active(
                game.id, new_status=False
            )
            return

        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text="🎮 Игра началась!")
        )

        round = await self.app.store.game_rounds.create_game_round(  # noqa: A001
            game_id=game.id, created_at=datetime.now(UTC)
        )

        questions = await self.app.store.questions.get_all_questions()
        if not questions:
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="❌ Нет доступных вопросов для игры.",
                )
            )
            await self.app.store.game.update_game_is_active(
                game.id, new_status=False
            )
            return

        selected_questions = random.sample(questions, min(3, len(questions)))

        first_question = selected_questions[0]
        round_question = (
            await self.app.store.round_questions.create_round_question(
                round_id=round.id, question_id=first_question.id
            )
        )

        for answer in first_question.answers:
            await self.app.store.round_question_answers.create_round_question_answer(  # noqa: E501
                round_question_id=round_question.id,
                answer_id=answer.id,
                is_found=False,
            )

        await self.app.store.game_rounds.update_round(
            round_id=round.id, question_id=round_question.id
        )

        for question in selected_questions[1:]:
            round_question = (
                await self.app.store.round_questions.create_round_question(
                    round_id=round.id, question_id=question.id
                )
            )

            for answer in question.answers:
                await self.app.store.round_question_answers.create_round_question_answer(  # noqa: E501
                    round_question_id=round_question.id,
                    answer_id=answer.id,
                    is_found=False,
                )

        await self._start_next_question(round)

    async def _start_next_question(self, round, round_questions=None):
        if not round:
            return

        if round_questions is None:
            round_questions = (
                await self.app.store.round_questions.get_round_questions_by_id(
                    round.id
                )
            )
        unanswered_questions = [rq for rq in round_questions if not rq.is_found]

        if not unanswered_questions:
            await self._show_round_statistics(round.game_id)
            await self._ask_for_next_round(round.game_id)
            return

        next_question = unanswered_questions[0]
        question = await self.app.store.questions.get_question_by_id(
            next_question.question_id
        )

        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text=f"❓ Вопрос: {question.question}\n\nКто первый ответит? Жмякайте! 👇",  # noqa: E501
                reply_markup=want_answer_keyboard,
            )
        )

    async def _show_round_statistics(self, game_id):
        scores = await self.app.store.game_scores.get_scores_by_game(game_id)
        stats_text = "📊 Статистика раунда:\n\n"
        for score in scores:
            player = await self.app.store.users.get_user_by_id(score.player_id)
            stats_text += f"{player.first_name}: {score.score} очков\n"

        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text=stats_text)
        )

    async def _ask_for_next_round(self, game_id):
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text="🎮 Хотите сыграть ещё один раунд?",
                reply_markup=yes_no_keyboard,
            )
        )

    async def _handle_active_game(self, game):
        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text="🎮 Игра уже активна")
        )
        rounds = await self.app.store.game_rounds.get_game_rounds_by_game_id(
            game_id=game.id
        )
        if not any(r.is_active for r in rounds):
            await self._start_game_after_delay(game)
        else:
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="🎮 Есть активный раунд")
            )
            active_round = (
                await self.app.store.game_rounds.get_active_round_by_chat_id(
                    self.chat_id
                )
            )
            if active_round:
                await self._start_next_question(active_round.id)
