from app.store.tg_api.dataclasses import Message

from ..base import BaseCommandHandler
from ..constants import want_answer_keyboard, yes_no_keyboard


class AnswerHandler(BaseCommandHandler):
    async def handle(self):
        upd = self.update.object.message
        user = await self.app.store.users.get_user_by_tg_id(upd.user_id)
        game = await self.app.store.game.get_game_by_chat_id(
            chat_id=upd.chat_id
        )
        active_round = (
            await self.app.store.game_rounds.get_active_round_by_chat_id(
                chat_id=upd.chat_id
            )
        )

        if game:  # noqa: SIM102
            if not game.is_active or not active_round:
                return

        if user.id != active_round.current_player_id:
            return

        await self._process_answer(upd.text, user, game, active_round)

    async def _process_answer(self, answer_text: str, user, game, active_round):
        cur_round_question = (
            await self.app.store.round_questions.get_round_question_by_id(
                active_round.question_id
            )
        )
        question = await self.app.store.questions.get_question_by_id(
            cur_round_question.question_id
        )
        answer = await self.app.store.answers.get_answer_by_word(
            answer_text, question.id
        )

        if answer:
            await self._handle_correct_answer(user, game, active_round, answer)
        else:
            await self._handle_wrong_answer(user, game, active_round)

    async def _handle_correct_answer(self, user, game, active_round, answer):
        f = self.app.store.round_question_answers.get_answers_by_round_question
        answers = await f(round_question_id=active_round.question_id)

        if answer.id in [ans.answer_id for ans in answers if ans.is_found]:
            await self._send_message("Такой ответ уже был, введите другой")
            return

        await self._process_new_correct_answer(
            user, game, active_round, answer, answers
        )

    async def _process_new_correct_answer(
        self, user, game, active_round, answer, answers
    ):
        await self.app.store.game_scores.update_score(
            user.id, game.id, answer.score
        )
        await self.app.store.game_rounds.update_round(
            active_round.id, current_player_id=0
        )

        round_question = (
            await self.app.store.round_questions.get_round_question_by_id(
                rq_id=active_round.question_id
            )
        )

        await self.app.store.round_question_answers.update_answer_status(
            round_question_id=round_question.id,
            answer_id=answer.id,
            new_status=True,
        )

        await self._send_message("Это правильный ответ")

        f = self.app.store.round_question_answers.get_answers_by_round_question
        updated_answers = await f(round_question_id=round_question.id)

        if all(ans.is_found for ans in updated_answers):
            game_scores = await self.app.store.game_scores.get_scores_by_game(
                game.id
            )
            for score in game_scores:
                await self.app.store.game_scores.update_player_status(
                    score.player_id, game.id, new_status=True
                )

            await self.app.store.round_questions.update_round_question_status(
                round_question_id=round_question.id, is_found=True
            )
            await self._send_message("Все ответы к вопросу отгаданы!")
            await self._finish_current_round_and_start_new(game, active_round)
        else:
            await self._send_want_answer_message()

    async def _handle_wrong_answer(self, user, game, active_round):
        await self.app.store.game_rounds.update_round(
            active_round.id, current_player_id=0
        )
        await self.app.store.game_scores.update_player_status(
            user.id, active_round.game_id, new_status=False
        )
        await self._send_message("Это не верный ответ :(")
        await self._send_message(f"{user.first_name} заблокирован")

        round_question = (
            await self.app.store.round_questions.get_round_question_by_id(
                rq_id=active_round.question_id
            )
        )
        f = self.app.store.round_question_answers.get_answers_by_round_question
        answers = await f(round_question_id=round_question.id)

        game_scores = await self.app.store.game_scores.get_scores_by_game(
            game.id
        )
        if all(not score.is_active for score in game_scores):
            await self._send_message(
                "Все участники заблокированы! Переходим к следующему вопросу."
            )

            for answer in answers:
                await (
                    self.app.store.round_question_answers.update_answer_status(
                        round_question_id=round_question.id,
                        answer_id=answer.answer_id,
                        new_status=True,
                    )
                )

            for score in game_scores:
                await self.app.store.game_scores.update_player_status(
                    score.player_id, game.id, new_status=True
                )

            await self.app.store.round_questions.update_round_question_status(
                round_question_id=round_question.id, is_found=True
            )
            await self._finish_current_round_and_start_new(game, active_round)
            return

        if all(ans.is_found for ans in answers):
            game_scores = await self.app.store.game_scores.get_scores_by_game(
                game.id
            )
            for score in game_scores:
                await self.app.store.game_scores.update_player_status(
                    score.player_id, game.id, new_status=True
                )

            await self.app.store.round_questions.update_round_question_status(
                round_question_id=round_question.id, is_found=True
            )
            await self._finish_current_round_and_start_new(game, active_round)
        else:
            await self._send_want_answer_message()

    async def _finish_current_round_and_start_new(self, game, active_round):
        round_question = (
            await self.app.store.round_questions.get_round_question_by_id(
                rq_id=active_round.question_id
            )
        )

        f = self.app.store.round_question_answers.get_answers_by_round_question
        answers = await f(round_question_id=round_question.id)

        if not all(ans.is_found for ans in answers):
            await self._send_message("Еще остались неотгаданные ответы")
            await self._send_want_answer_message()
            return

        round_questions = (
            await self.app.store.round_questions.get_round_questions_by_id(
                active_round.id
            )
        )
        unanswered_questions = [rq for rq in round_questions if not rq.is_found]

        if not unanswered_questions:
            await self._show_player_statistics(game.id)
            await self.app.store.game_rounds.update_round(
                round_id=active_round.id, is_active=False
            )
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="Хотите сыграть ещё один раунд?",
                    reply_markup=yes_no_keyboard,
                )
            )
        else:
            next_question = unanswered_questions[0]
            await self.app.store.questions.get_question_by_id(
                next_question.question_id
            )

            await self.app.store.game_rounds.update_round(
                round_id=active_round.id, question_id=next_question.id
            )

            await self._send_want_answer_message()

    async def _show_player_statistics(self, game_id: int):
        scores = await self.app.store.game_scores.get_scores_by_game(game_id)
        if not scores:
            return

        stats_message = "📊 Статистика игроков:\n\n"
        for score in scores:
            if score.score > 0:
                user = await self.app.store.users.get_user_by_id(
                    score.player_id
                )
                if user:
                    stats_message += f"{user.first_name}: {score.score} очков\n"

        await self._send_message(stats_message)

    async def _send_message(self, text: str):
        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text=text)
        )

    async def _send_want_answer_message(self):
        active_round = (
            await self.app.store.game_rounds.get_active_round_by_chat_id(
                self.chat_id
            )
        )
        round_question = (
            await self.app.store.round_questions.get_round_question_by_id(
                rq_id=active_round.question_id
            )
        )
        question = await self.app.store.questions.get_question_by_id(
            question_id=round_question.question_id
        )
        q_text = question.question
        text = f"❓ Вопрос: {q_text}\n\nКто первый ответит? Жмякайте! 👇"
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text=text,
                reply_markup=want_answer_keyboard,
            )
        )
