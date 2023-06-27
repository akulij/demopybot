import aiogram
from aiogram.types import Message, ChatJoinRequest
from modules import dialogs
from modules.db import FAQ

from modules.dbtg import DBTG
from modules.keyboards import ReplyKeyboard, InlineKeyboard
from modules.config import config as cfg


class JoinRequest:
    def __init__(self, dispatcher: aiogram.Dispatcher, db_provider: DBTG):
        self.dp = dispatcher
        self.db = db_provider
        self.rk = ReplyKeyboard(self.db)
        self.ik = InlineKeyboard(self.db)
        
        @self.dp.chat_join_request_handler()
        async def joinapprove(chat_member: ChatJoinRequest):
            user = await self.db.get_user(chat_member.from_user, start_args="channel_source")
            await chat_member.approve()
            userid = chat_member.from_user.id

            link = "https://t.me/+Mph8PoMh34k3N2Uy"
            await self.dp.bot.send_message(userid, f"Ваша заявка на вступление принята!\nКанал: {link}\nНажмите на /start для получения краткой информации из канала")
