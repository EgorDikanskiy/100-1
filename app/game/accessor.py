from datetime import datetime
from sqlalchemy import select
from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel, Game, GameScore, GameScoreModel

class GameAccessor(BaseAccessor):
    async def create_game(self, chat_id: int, is_active: bool, created_at: datetime) -> Game:
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
            q = select(GameModel).where(GameModel.chat_id == chat_id)
            result = await session.execute(q)
            game = result.scalars().first()
            if game:
                return game.to_data()
        
    async def update_game_is_active(self, chat_id: int, new_status: bool) -> Game | None:
        async with self.app.database.session() as session:
            q = select(GameModel).where(GameModel.chat_id == chat_id)
            result = await session.execute(q)
            game = result.scalars().first()
            if game:
                game.is_active = new_status
                await session.commit()
                return game.to_data()
            

class GameScoreAccessor(BaseAccessor):
    async def create_game_score(self, player_id: int, game_id: int) -> GameScore:
        async with self.app.database.session() as session:
            q = select(GameScoreModel).where(
                GameScoreModel.player_id == player_id,
                GameScoreModel.game_id == game_id,
            )
            result = await session.execute(q)
            existing = result.scalars().first()
            if existing:
                raise ValueError(f"GameScore for player_id={player_id} and game_id={game_id} already exists.")

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
            return [game_score.to_data() for game_score in result.scalars().all()]

    async def update_score(self, score_id: int, new_score: int) -> GameScore | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(GameScoreModel).where(GameScoreModel.id == score_id)
            )
            game_score = result.scalars().first()
            if game_score:
                game_score.score = new_score
                await session.commit()
                return game_score.to_data()