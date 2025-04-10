from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.store.database import BaseModel

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application") -> None:
        self.app = app

        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        self.session = sessionmaker(
            self.engine,
            expire_on_commit=False,
            future=True,
            class_=AsyncSession,
        )

        database_url = f"postgresql+asyncpg://{self.app.config.database.user}:{self.app.config.database.password}@{self.app.config.database.host}/{self.app.config.database.database}"
        self.engine = create_async_engine(database_url, echo=True, future=True)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.engine:
            await self.engine.dispose()
