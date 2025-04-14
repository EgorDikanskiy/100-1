import typing

from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        await super().connect(app)
        admin = await self.get_by_email(email=self.app.config.admin.email)
        if not admin:
            await self.create_admin(
                email=self.app.config.admin.email,
                password=self.app.config.admin.password,
            )

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as session:
            q = select(AdminModel).where(AdminModel.email == email)
            result = await session.execute(q)
            admin = result.scalars().first()
            if admin:
                return admin.to_data()
            return {}

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            admin = AdminModel(
                email=email, password=Admin.hash_password(password)
            )
            session.add(admin)
            await session.commit()
            return admin.to_data()
