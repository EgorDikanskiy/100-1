import json

from app.store.bot.utils.helpers import create_round_with_question
from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message
from ..constants import *

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
                    answers = await self.app.store.round_question_answers.get_answers_by_round_question(round_question_id=active_round.question_id)
                    if answer.id in [ans.answer_id for ans in answers if ans.is_found]:
                        await self.app.store.tg_api.send_message(Message(chat_id=self.chat_id, text="Такой ответ уже был"))
                    else:
                        await self.app.store.game_scores.update_score(user.id, answer.score)
                        await self.app.store.game_rounds.update_round(active_round.id, current_player_id=0)
                        await self.app.store.round_question_answers.update_answer_status(round_question_id=active_round.question_id, answer_id=answer.id, new_status=True)
                        answers = await self.app.store.round_question_answers.get_answers_by_round_question(round_question_id=active_round.question_id)
                        await self.app.store.tg_api.send_message(Message(chat_id=self.chat_id, text="Это правильный ответ"))
                        if any(not ans.is_found for ans in answers):
                            await self.app.store.tg_api.send_message(
                                Message(
                                    chat_id=self.chat_id,
                                    text="Жмякайте!",
                                    reply_markup=want_answer_keyboard
                                )
                            )
                            print(answers)
                        else:
                            await self.app.store.round_questions.update_round_question_status(active_round.question_id, is_found=True)
                            await self.app.store.tg_api.send_message(
                                Message(
                                    chat_id=self.chat_id,
                                    text="Ответы к вопросу закончились"
                                )
                            )
                            await self.app.store.game_rounds.update_round(round_id=active_round.id, is_active=False)
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
                else:
                    await self.app.store.game_rounds.update_round(active_round.id, current_player_id=0)
                    await self.app.store.game_scores.update_player_status(user.id, active_round.game_id, False)
                    await self.app.store.tg_api.send_message(Message(chat_id=self.chat_id, text="Это не верный ответ :("))
                    game_scores = await self.app.store.game_scores.get_scores_by_game(game_id=game.id)
                    if any([score.is_active for score in game_scores]):
                        await self.app.store.tg_api.send_message(
                            Message(
                                chat_id=self.chat_id,
                                text="Жмякайте!",
                                reply_markup=want_answer_keyboard
                            )
                        )
                    else:
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

            else:
                print("Ты дебил")
            
            

        