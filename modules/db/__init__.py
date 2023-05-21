from typing import Optional, AsyncIterator

from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from modules.config import Settings


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    nickname: str


class DB:
    def __init__(self, config: Settings):
        self.engine = create_async_engine(config.database_uri)

    async def get_user_byid(self, id: int) -> User | None:
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, id)

        return user
