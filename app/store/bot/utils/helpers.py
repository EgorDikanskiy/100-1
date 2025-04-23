from datetime import UTC, datetime

from app.web.app import Application


async def create_round_with_question(
    app: "Application", game_id: int, chat_id: int
):
    new_round = await app.store.game_rounds.create_game_round(
        game_id=game_id, created_at=datetime.now(UTC)
    )

    question = await app.store.questions.get_random_question()
    round_question = await app.store.round_questions.create_round_question(
        round_id=new_round.id, question_id=question.id
    )
    await app.store.game_rounds.update_round(
        round_id=new_round.id, question_id=round_question.id
    )

    for answer in question.answers:
        await app.store.round_question_answers.create_round_question_answer(
            round_question_id=round_question.id, answer_id=answer.id
        )

    users = await app.store.users.get_all_users()
    for user in users:
        await app.store.game_scores.update_player_status(
            user.id, new_round.game_id, new_status=True
        )

    return question
