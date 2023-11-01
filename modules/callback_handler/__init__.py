import aiogram
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from modules.dbtg import DBTG
from modules.keyboards import ReplyKeyboard, InlineKeyboard
from modules.config import config as cfg


class CallbackHandler:
    def __init__(self, dispatcher: aiogram.Dispatcher, db_provider: DBTG):
        self.dp = dispatcher
        self.db = db_provider
        self.rk = ReplyKeyboard(self.db)
        self.ik = InlineKeyboard(self.db)
        
        @self.dp.callback_query_handler(lambda q: q.data.startswith("faq"))
        async def faq(query: CallbackQuery):
            user = await self.db.get_user(query.from_user)
            _, faqid = query.data.split("_")
            faqid = int(faqid)
            faq = await self.db.db.get_faq(faqid=faqid)
            faq = faq[0]

            await self.dp.bot.send_message(query.message.chat.id, faq.answer, "HTML")
        
        @self.dp.callback_query_handler(lambda q: q.data.startswith("info"))
        async def faqinfo(query: CallbackQuery):
            user = await self.db.get_user(query.from_user)
            _, faqid = query.data.split("_")
            faqid = int(faqid)

            await self.db.db.set_user_state(user, f"editfaq_content_{faqid}")
            await self.dp.bot.send_message(query.message.chat.id, "Введите ответ на вопрос", "HTML")

        
        @self.dp.callback_query_handler(lambda q: q.data.startswith("delete"))
        async def faqinfo(query: CallbackQuery):
            user = await self.db.get_user(query.from_user)
            _, faqid = query.data.split("_")
            faqid = int(faqid)

            await self.db.db.delete_faqs(faqid=faqid)
            await self.dp.bot.send_message(query.message.chat.id, "Вопрос удален", "HTML")

        
        @self.dp.callback_query_handler(lambda q: q == "bots_add_chat")
        async def faqinfo(query: CallbackQuery):
             await self.dp.bot.send_message(query.message.chat.id, "Отправьте файл с чатами", "HTML")
