import aiogram
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from modules.db import FAQ

from modules.dbtg import DBTG
from modules.keyboards import ReplyKeyboard, InlineKeyboard
from modules.config import config as cfg


class Commands:
    def __init__(self, dispatcher: aiogram.Dispatcher, db_provider: DBTG):
        self.dp = dispatcher
        self.db = db_provider
        self.rk = ReplyKeyboard(self.db)
        self.ik = InlineKeyboard(self.db)
        
        @self.dp.message_handler(commands=["admin"])
        async def admin(message: Message):
            print("!!!")
            user = await self.db.get_user(message.from_user)
            _, code = message.text.split()
            if code == "QkrdOO":
                user.is_admin = True

            await self.db.db.create_user(user)
            await message.answer("Вы стали админом")
        
        @self.dp.message_handler(commands=["create"])
        async def create(message: Message):
            user = await self.db.get_user(message.from_user)
            faq = FAQ(question="", answer="", category="onedit")
            await self.db.db.append_faq(faq)
            await self.db.db.set_user_state(user, f"editfaq_title_{faq.id}")
            await message.answer("Введите вопрос")
        
        @self.dp.message_handler(commands=["edit"])
        async def edit(message: Message):
            user = await self.db.get_user(message.from_user)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for q in basic_dialog.keys():
                keyboard.add(q)
            keyboard = await self.rk.get("main")
            await message.answer(config.greeting, reply_markup=keyboard)
