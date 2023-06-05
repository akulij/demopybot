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

