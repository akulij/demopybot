from typing import Optional, AsyncIterator
import datetime
from urllib.parse import uses_params

from sqlmodel import Column, SQLModel, Field, select, delete, JSON, table
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.engine.result import ScalarResult
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

    async def _update_instance(self, instance: SQLModel):
        async with AsyncSession(self.engine) as session:
            session.add(instance)
            await session.commit()
            await session.refresh(instance)

    async def _exec_query(self, q) -> ScalarResult:
        async with AsyncSession(self.engine) as session:
            e = await session.exec(q)

        return e

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
        user: UserV1 = await self.get_user_byid(userid)
        a = ActionV1(bot=botname,
                     username=user.name,
                     userid=userid,
                     actiontype="send_message",
                     actionjson={"message": message},
                     time=datetime.datetime.utcnow())
        async with AsyncSession(self.engine) as session:
            session.add(a)
            await session.commit()
            await session.refresh(a)

    async def check_password(self, botname: str, password: str):
        q = select(BotOwner).where(BotOwner.botname == botname)
        cred = (await self._exec_query(q)).first()
        if not cred: return False

        if cred.password == password: return True

        return False

    async def get_new_users_per_day(self, botname: str, days: int = 5):
        stat = []

        mindate = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        maxdate = datetime.datetime.utcnow()
        for _ in range(days):
            q = select(ActionV1).where(ActionV1.bot == botname).where(ActionV1.actiontype == "register").where((ActionV1.time > mindate) & (ActionV1.time <= maxdate))
            e = await self._exec_query(q)
            actions: list[ActionV1] = e.all()
            
            stat.append({
                    "day": mindate.day,
                    "users": list(map(lambda a: a.username, actions))
                })

            maxdate = mindate
            mindate -= datetime.timedelta(days=1)

        return stat

    async def get_new_users_total(self, botname: str, days: int = 5):
        stat = []

        mindate = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        for _ in range(days):
            q = select(ActionV1).where(ActionV1.bot == botname).where(ActionV1.actiontype == "register").where(ActionV1.time > mindate)
            e = await self._exec_query(q)
            actions: list[ActionV1] = e.all()
            
            stat.append({
                    "day": mindate.day,
                    "users": len(list(map(lambda a: a.username, actions)))
                })

            mindate -= datetime.timedelta(days=1)

        return stat

    async def get_active_users_per_day(self, botname: str, days: int = 5):
        stat = []

        mindate = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        maxdate = datetime.datetime.utcnow()
        for _ in range(days):
            q = select(ActionV1).where(ActionV1.bot == botname).where(ActionV1.actiontype == "message").where((ActionV1.time > mindate) & (ActionV1.time <= maxdate))
            e = await self._exec_query(q)
            actions: list[ActionV1] = e.all()
            print(actions, flush=True)
            print(f"{len(set(map(lambda a: a.username, actions)))=}")
            
            stat.append({
                    "day": mindate.day,
                    "users": len(set(map(lambda a: a.username, actions)))
                })

            maxdate = mindate
            mindate -= datetime.timedelta(days=1)

        return stat

    async def get_active_users_per_hours(self, botname: str):
        stat = []

        for delta in (1, 6, 12, 24):
            q = select(ActionV1).where(ActionV1.bot == botname).where(ActionV1.actiontype == "message").where(ActionV1.time > (datetime.datetime.utcnow() - datetime.timedelta(hours=delta)))
            e = await self._exec_query(q)
            actions: list[ActionV1] = e.all()
            print(actions, flush=True)
            
            stat.append({
                    "day": f"{delta}h",
                    "users": len(set(map(lambda a: a.username, actions)))
                })

        return stat

    async def get_inactive_users(self) -> list[int]:
        q = select(ActionV1.userid).where((ActionV1.actiontype == "message") | (ActionV1.actiontype == "send_message")).where(ActionV1.time < (datetime.datetime.utcnow() - datetime.timedelta(hours=24)))
        e = await self._exec_query(q)

        return list(set(e.all()))

