import aiogram
from aiogram.types import Message
from modules import dialogs
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
            if not user.is_admin:
                return
            faq = FAQ(question="", answer="", category="onedit")
            await self.db.db.append_faq(faq)
            await self.db.db.set_user_state(user, f"editfaq_title_{faq.id}")
            await message.answer("Введите вопрос")
        
        @self.dp.message_handler(commands=["edit"])
        async def edit(message: Message):
            user = await self.db.get_user(message.from_user)
            if not user.is_admin:
                return
            keyboard = InlineKeyboard(self.db)

            await message.answer(dialogs.config.edit_msg, "HTML", reply_markup=await keyboard.get("faq_info"))
        
        @self.dp.message_handler(commands=["delete"])
        async def delete(message: Message):
            user = await self.db.get_user(message.from_user)
            if not user.is_admin:
                return
            keyboard = InlineKeyboard(self.db)

            await self.db.db.delete_unused_faq()
            await message.answer(dialogs.config.delete_msg, "HTML", reply_markup=await keyboard.get("faq_delete"))
        
        @self.dp.message_handler(commands=["cancel"])
        async def cancel(message: Message):
            user = await self.db.get_user(message.from_user)

            await self.db.db.set_user_state(user, "main")
            await message.answer("Действие отменено", "HTML")

        @self.dp.message_handler(commands=["there"])
        async def there(message: Message):
            print(message.chat.id)
        
        @self.dp.message_handler(commands=["post"])
        async def post(message: Message):
            user = await self.db.get_user(message.from_user)
            if not user.is_admin:
                return

            await self.db.db.set_user_state(user, "post_image")
            await message.answer("Отправьте картинку для поста, или отправьте любой текст для поста без картинки", "HTML")
