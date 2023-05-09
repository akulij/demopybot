from sqlalchemy.ext.asyncio import create_async_engine

from modules.config import config

engine = create_async_engine(config.database_uri)

from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    nickname: str
