from typing import Optional, AsyncIterator
import datetime

from sqlmodel import SQLModel, Field, select, delete
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from modules.config import Settings


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    nickname: str
    state: str = Field(default="start")
    is_admin: bool = Field(default=False)
    last_activity: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class FAQ(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str = Field(unique=True)
    answer: str
    category: str


class DB:
    def __init__(self, config: Settings):
        self.engine = create_async_engine(config.database_uri)

    async def get_user_byid(self, id: int) -> User | None:
        async with AsyncSession(self.engine) as session:
            user = await session.get(User, id)

        return user

    async def create_user(self, user: User):
        async with AsyncSession(self.engine) as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

    async def append_faq(self, faq: FAQ):
        async with AsyncSession(self.engine) as session:
            session.add(faq)
            await session.commit()
            await session.refresh(faq)

    async def get_faq(self, category = None, faqid: Optional[int] = None) -> list[FAQ]:
        async with AsyncSession(self.engine) as session:
            q = select(FAQ)
            if category:
                q = q.where(FAQ.category == category)
            if faqid:
                q = q.where(FAQ.id == faqid)
            e = await session.exec(q)
            faq = e.all()

        return faq

    async def delete_faqs(self, faqid: int | None = None):
        async with AsyncSession(self.engine) as session:
            q = delete(FAQ)
            if faqid != None:
                q = q.where(FAQ.id == faqid)
            await session.exec(q)
            await session.commit()

    async def delete_unused_faq(self):
        async with AsyncSession(self.engine) as session:
            q = delete(FAQ).where(FAQ.category != "main")
            await session.exec(q)
            await session.commit()

    async def set_user_state(self, user: User, state: str):
        user.state = state
        async with AsyncSession(self.engine) as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

    async def get_all_user_ids(self) -> list[int]:
        async with AsyncSession(self.engine) as session:
            q = select(User)
            e = await session.exec(q)
            users = e.all()

        return list(map(lambda u: u.id, users))
