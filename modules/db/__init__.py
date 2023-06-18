from typing import Optional, AsyncIterator
import datetime

from sqlmodel import Column, SQLModel, Field, select, delete, JSON, table
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import BigInteger, desc

from modules.config import Settings


class UserV1(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, sa_column=Column(BigInteger(), primary_key=True))
    name: str
    nickname: Optional[str]
    state: str = Field(default="start")
    is_admin: bool = Field(default=False)
    last_activity: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class BotInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, sa_column=Column(BigInteger(), primary_key=True), nullable=False)
    name: str
    nickname: str = Field(unique=True)
    version: int

class BotOwner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, sa_column=Column(BigInteger(), primary_key=True))
    login: str
    password: str
    botname: str = Field(unique=True)

class ActionV1(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False, sa_column=Column(BigInteger(), primary_key=True, autoincrement=True, nullable=False))
    bot: str
    username: Optional[str]
    userid: int = Field(default=None, primary_key=True, sa_column=Column(BigInteger(), primary_key=True))
    actiontype: str
    actionjson: dict = Field(default={}, sa_column=Column(JSON))
    time: datetime.datetime

class TaskV1(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, sa_column=Column(BigInteger(), primary_key=True), nullable=False)
    botname: str
    type: str
    taskdesc: dict = Field(default={}, sa_column=Column(JSON))
    time: datetime.datetime

class FAQ(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    botname: Optional[str]
    question: str
    answer: str
    category: str


class DB:
    def __init__(self, config: Settings):
        self.engine = create_async_engine(config.database_uri)
        self.config = config

    async def new_action(self, user: UserV1, actiontype: str, actionjson: dict):
        action = ActionV1(
                bot=self.config.botname,
                username=user.nickname,
                userid=user.id or 0,
                actiontype=actiontype,
                actionjson=actionjson,
                time=datetime.datetime.utcnow()
                )
        async with AsyncSession(self.engine) as session:
            session.add(action)
            await session.commit()
            await session.refresh(action)

    async def get_user_byid(self, id: int) -> UserV1 | None:
        async with AsyncSession(self.engine) as session:
            user = await session.get(UserV1, id)

        return user

    async def create_user(self, user: UserV1):
        async with AsyncSession(self.engine) as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

    async def append_faq(self, faq: FAQ):
        faq.botname = self.config.botname
        async with AsyncSession(self.engine) as session:
            session.add(faq)
            await session.commit()
            await session.refresh(faq)

    async def get_faq(self, category = None, faqid: Optional[int] = None) -> list[FAQ]:
        async with AsyncSession(self.engine) as session:
            q = select(FAQ).where(FAQ.botname == self.config.botname)
            if category:
                q = q.where(FAQ.category == category)
            if faqid:
                q = q.where(FAQ.id == faqid)
            e = await session.exec(q)
            faq = e.all()

        return faq

    async def delete_faqs(self, faqid: int | None = None):
        async with AsyncSession(self.engine) as session:
            q = delete(FAQ).where(FAQ.botname==self.config.botname)
            if faqid != None:
                q = q.where(FAQ.id == faqid)
            await session.exec(q)
            await session.commit()

    async def delete_unused_faq(self):
        async with AsyncSession(self.engine) as session:
            q = delete(FAQ).where(FAQ.category != "main")
            await session.exec(q)
            await session.commit()

    async def set_user_state(self, user: UserV1, state: str):
        user.state = state
        async with AsyncSession(self.engine) as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

    async def get_all_user_ids(self) -> list[int]:
        async with AsyncSession(self.engine) as session:
            q = select(UserV1)
            e = await session.exec(q)
            users = e.all()

        return list(map(lambda u: u.id, users))

    async def add_owner(self, login: str, password: str, botname: str):
        bo = BotOwner(login=login, password=password, botname=botname)
        async with AsyncSession(self.engine) as session:
            session.add(bo)
            await session.commit()
            await session.refresh(bo)
        return bo

    async def get_botowner(self, botname: str) -> BotOwner | None:
        async with AsyncSession(self.engine) as session:
            q = select(BotOwner).where(BotOwner.botname == botname)
            e = await session.exec(q)
            bo = e.first()

        return bo

    async def get_user_previews(self, botname: str, limit: int = 50):
        previews: list[dict] = []
        async with AsyncSession(self.engine) as session:
            q = select(ActionV1.userid).where(ActionV1.bot == botname).group_by(ActionV1.userid)
            e = await session.exec(q)
            for userid in e:
                q = select(ActionV1).where(ActionV1.bot == botname).where(ActionV1.userid == userid).where(ActionV1.actiontype == "message").order_by(desc(ActionV1.time))
                e = await session.exec(q)
                action: ActionV1 = e.first()
                previews.append({
                    "author": action.username,
                    "message": action.actionjson["message"],
                    "userid": userid,
                    })

            print(previews, flush=True)
            return previews

    async def get_user_messages(self, userid: int, botname: str, limit: int = 50) -> list[ActionV1]:
        async with AsyncSession(self.engine) as session:
            q = select(ActionV1).where(ActionV1.userid == userid).where(ActionV1.bot == botname).where(ActionV1.actiontype == "message").order_by(desc(ActionV1.time))
            e = await session.exec(q)

        return e.all()

    async def create_task_message(self, userid: int, botname: str, message: str):
        desc = {
                "userid": userid,
                "message": message
                }
        t = TaskV1(botname=botname, time=datetime.datetime.utcnow(), taskdesc=desc, type="send_message")
        async with AsyncSession(self.engine) as session:
            session.add(t)
            await session.commit()
            await session.refresh(t)
    
    async def delete_task(self, task: TaskV1):
        async with AsyncSession(self.engine) as session:
            await session.delete(task)
            await session.commit()
    
    async def get_tasks(self) -> list[TaskV1]:
        async with AsyncSession(self.engine) as session:
            q = select(TaskV1).where(TaskV1.botname == self.config.botname)
            e = await session.exec(q)

        return e.all()

    async def set_message_sended(self, userid: int, botname: str, message: str):
        user = await self.get_user_byid(userid)
        a = ActionV1(bot=botname, username=user.name, userid=userid, actiontype="send_message", actionjson={"message": message})
        async with AsyncSession(self.engine) as session:
            pass

