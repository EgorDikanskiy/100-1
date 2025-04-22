from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.users.models import User, UserModel


class UserAccessor(BaseAccessor):
    async def create_user(self, tg_id: int, first_name: str) -> User:
        async with self.app.database.session() as session:
            user = UserModel(
                tg_id=tg_id,
                first_name=first_name,
            )
            session.add(user)
            await session.commit()
            return user.to_data()

    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        async with self.app.database.session() as session:
            q = select(UserModel).where(UserModel.tg_id == tg_id)
            result = await session.execute(q)
            user = result.scalars().first()
            if user:
                return user.to_data()
            return None
            
    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.app.database.session() as session:
            q = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(q)
            user = result.scalars().first()
            if user:
                return user.to_data()
            return None
        
    async def get_all_users(self) -> list[User]:
        async with self.app.database.session() as session:
            q = select(UserModel)
            result = await session.execute(q)
            users = result.scalars().all()
            return [user.to_data() for user in users]
