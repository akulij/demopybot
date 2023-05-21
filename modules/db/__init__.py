from typing import Optional, AsyncIterator

from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from modules.config import config


engine = create_async_engine(config.database_uri)

async def get_session() -> AsyncIterator[AsyncSession]:
   async with AsyncSession(engine) as session:
       yield session


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    nickname: str
