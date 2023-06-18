import datetime

import aiogram
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from modules.db import FAQ

from modules.dbtg import DBTG
from modules.keyboards import ReplyKeyboard, InlineKeyboard
from modules.config import config as cfg
from aiogram.dispatcher.middlewares import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, db_provider: DBTG):
        self.db = db_provider
        super(LoggingMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        print(f"New message: {message.text}")
        print(f"Data: {data}")
        user = await self.db.get_user(message.from_user)
        await self.db.db.new_action(user, "message", {"message": message.text})
        user.last_activity = datetime.datetime.utcnow()
        await self.db.db.create_user(user)

class UserStat:
    def __init__(self, dispatcher: aiogram.Dispatcher, db_provider: DBTG):
        self.dp = dispatcher
        self.db = db_provider

        self.dp.middleware.setup(LoggingMiddleware(self.db))
