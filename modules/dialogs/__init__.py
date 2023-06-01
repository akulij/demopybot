import aiogram
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from modules.dbtg import DBTG

from . import config
from .config import basic_dialog


class DialogConfigurer:
    def __init__(self, dispatcher: aiogram.Dispatcher, db_provider: DBTG):
        self.dp = dispatcher
        self.db = db_provider
        
        @self.dp.message_handler(commands=["start"])
        async def start(message: Message):
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for q in basic_dialog.keys():
                keyboard.add(q)
            await message.answer(basic_dialog[config.menu], reply_markup=keyboard)

        # for question, answer in basic_dialog.items():
        #     h = lambda m: m.answer(answer)
        #     print(h)
        #     self.dp.message_handler(regexp=question)(h)
        @self.dp.message_handler()
        async def map(message: Message):
            if message.text in basic_dialog.keys():
                await message.answer(basic_dialog[message.text])
