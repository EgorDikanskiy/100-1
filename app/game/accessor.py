from datetime import datetime

from sqlalchemy import desc, select

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    Game,
    GameModel,
    GameRound,
    GameRoundModel,
    GameScore,
    GameScoreModel,
    RoundQuestion,
    RoundQuestionAnswer,
    RoundQuestionAnswerModel,
    RoundQuestionModel,
)
from app.questions.models import AnswerModel


class GameAccessor(BaseAccessor):
    async def create_game(
        self, chat_id: int, is_active: bool, created_at: datetime
    ) -> Game:
        async with self.app.database.session() as session:
            game = GameModel(
                chat_id=chat_id,
                is_active=is_active,
                created_at=created_at,
            )
            session.add(game)
            await session.commit()
            return game.to_data()

    async def get_game_by_chat_id(self, chat_id: int) -> Game | None:
        async with self.app.database.session() as session:
            q = select(GameModel).where(GameModel.chat_id == chat_id).order_by(desc(GameModel.id))
            result = await session.execute(q)
            game = result.scalars().first()
            if game:
                return game.to_data()
            return None

    async def update_game_is_active(
        self, game_id: int, new_status: bool
    ) -> Game | None:
        async with self.app.database.session() as session:
            q = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(q)
            game = result.scalars().first()
            if game:
                game.is_active = new_status
                await session.commit()
                return game.to_data()
            return None


class GameScoreAccessor(BaseAccessor):
    async def create_game_score(
        self, player_id: int, game_id: int
    ) -> GameScore:
        async with self.app.database.session() as session:
            q = select(GameScoreModel).where(
                GameScoreModel.player_id == player_id,
                GameScoreModel.game_id == game_id,
            )
            result = await session.execute(q)
            existing = result.scalars().first()
            if existing:
                raise ValueError(
                    f"GameScore for player_id={player_id} and"
                    f"game_id={game_id} already exists."
                )

            game_score = GameScoreModel(
                player_id=player_id,
                game_id=game_id,
                score=0,
                is_active=False,
            )
            session.add(game_score)
            await session.commit()
            return game_score.to_data()

    async def get_scores_by_game(self, game_id: int) -> list[GameScore]:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(GameScoreModel).where(GameScoreModel.game_id == game_id)
            )
            return [
                game_score.to_data() for game_score in result.scalars().all()
            ]

    async def update_score(
        self, player_id: int, new_score: int
    ) -> GameScore | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(GameScoreModel).where(
                    GameScoreModel.player_id == player_id
                )
            )
            game_score = result.scalars().first()
            if game_score:
                game_score.score = new_score
                await session.commit()
                return game_score.to_data()
            return None

    async def get_player_status(self, player_id: int, game_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(GameScoreModel.is_active).where(
                    GameScoreModel.player_id == player_id,
                    GameScoreModel.game_id == game_id,
                )
            )
            return result.scalars().first()

    async def update_player_status(
        self, player_id: int, game_id: int, new_status: bool
    ) -> GameScore | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(GameScoreModel).where(
                    GameScoreModel.player_id == player_id,
                    GameScoreModel.game_id == game_id,
                )
            )
            game_score = result.scalars().first()
            if game_score:
                game_score.is_active = new_status
                await session.commit()
                return game_score.to_data()
            return None


class GameRoundAccessor(BaseAccessor):
    async def create_game_round(
        self, game_id: int, created_at: datetime
    ) -> GameRound:
        async with self.app.database.session() as session:
            game_round = GameRoundModel(
                game_id=game_id,
                is_active=True,
                created_at=created_at,
            )
            session.add(game_round)
            await session.commit()
            return game_round.to_data()
        
    async def get_game_rounds_by_game_id(self, game_id: int) -> list[GameRound]:
        async with self.app.database.session() as session:
            q = select(GameRoundModel).where(GameRoundModel.game_id == game_id)
            result = await session.execute(q)
            models = result.scalars().all()
            return [m.to_data() for m in models]

    async def update_round(
        self, round_id: int, current_player_id: int, is_active: bool = True
    ) -> GameRound | None:
        async with self.app.database.session() as session:
            q = select(GameRoundModel).where(GameRoundModel.id == round_id)
            result = await session.execute(q)
            model = result.scalars().first()
            if model:
                model.current_player_id = current_player_id
                model.is_active = is_active
                await session.commit()
                return model.to_data()
            return None


class RoundQuestionAccessor(BaseAccessor):
    async def create_round_question(
        self, round_id: int, question_id: int, is_found: bool = False
    ) -> RoundQuestion:
        async with self.app.database.session() as session:
            rq = RoundQuestionModel(
                round_id=round_id,
                question_id=question_id,
                is_found=is_found,
            )
            session.add(rq)
            await session.commit()
            await session.refresh(rq)
            return rq.to_data()

    async def get_round_question_by_id(
        self, rq_id: int
    ) -> RoundQuestion | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(RoundQuestionModel).where(RoundQuestionModel.id == rq_id)
            )
            model = result.scalars().first()
            if model:
                question = model.to_data()
                question.answers = [
                    answer.to_data() for answer in model.answers
                ]
                return question
            return None

    async def check_round_question_status(self, round_question_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(RoundQuestionAnswerModel.is_found).where(
                    RoundQuestionAnswerModel.round_question_id
                    == round_question_id
                )
            )
            statuses = result.scalars().all()

            if any(status is False for status in statuses):
                return True
            rq_result = await session.execute(
                select(RoundQuestionModel).where(
                    RoundQuestionModel.id == round_question_id
                )
            )
            round_question_model = rq_result.scalars().first()
            if round_question_model:
                round_question_model.is_found = True
                await session.commit()
            return False


class RoundQuestionAnswerAccessor(BaseAccessor):
    async def create_round_question_answer(
        self, round_question_id: int, answer_id: int, is_found: bool = False
    ) -> RoundQuestionAnswer:
        async with self.app.database.session() as session:
            rqa = RoundQuestionAnswerModel(
                round_question_id=round_question_id,
                answer_id=answer_id,
                is_found=is_found,
            )
            session.add(rqa)
            await session.commit()
            await session.refresh(rqa)
            return rqa.to_data()

    async def get_answers_by_round_question(
        self, round_question_id: int
    ) -> list[RoundQuestionAnswer]:
        async with self.app.database.session() as session:
            q = select(RoundQuestionAnswerModel).where(
                RoundQuestionAnswerModel.round_question_id == round_question_id
            )
            result = await session.execute(q)
            models = result.scalars().all()
            return [m.to_data() for m in models]

    async def update_answer_status(
        self, round_question_answer_id: int, new_status: bool
    ) -> RoundQuestionAnswer | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(RoundQuestionAnswerModel).where(
                    RoundQuestionAnswerModel.id == round_question_answer_id
                )
            )
            rqa_model = result.scalars().first()
            if rqa_model:
                rqa_model.is_found = new_status
                await session.commit()
                await session.refresh(rqa_model)
                return rqa_model.to_data()
            return None

    async def check_user_answer_in_not_found(
        self, round_question_id: int, user_answer: str
    ) -> bool:
        async with self.app.database.session() as session:
            q = (
                select(RoundQuestionAnswerModel)
                .join(RoundQuestionAnswerModel.answer)
                .where(
                    RoundQuestionAnswerModel.round_question_id
                    == round_question_id,
                    not RoundQuestionAnswerModel.is_found,
                    AnswerModel.word.ilike(user_answer),
                )
            )
            result = await session.execute(q)
            rqa_model = result.scalars().first()
            if rqa_model is not None:
                rqa_model.is_found = True
                await session.commit()
                return True
            return False
