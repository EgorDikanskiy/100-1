from datetime import datetime
from sqlalchemy import select
from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel, Game

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