from typing import Optional

import aiogram
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from modules.dbtg import DBTG
from modules.db import UserV1

from . import config
from .config import reply_keyboards, inline_keyboards


class ReplyKeyboard:
    def __init__(self, db_provider: DBTG):
        self.db = db_provider

    async def get(self, keyboard_name: str, user: Optional[UserV1] = None):
        assert keyboard_name in reply_keyboards.keys()

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for line in reply_keyboards[keyboard_name]:
            if type(line) == list:
                keyboard.add(*line)
            else:
                keyboard.add(line)

        return keyboard

class InlineKeyboard:
    def __init__(self, db_provider: DBTG):
        self.db = db_provider

    async def get(self, keyboard_name: str, user: Optional[UserV1] = None):
        print(f"KN: {keyboard_name}")
        assert keyboard_name in inline_keyboards.keys()

        keyboard = InlineKeyboardMarkup()
        kbd = inline_keyboards[keyboard_name]
        if callable(kbd):
            lines = await kbd(self.db.db, user)
        else:
            lines = kbd
        for line in lines:
            if type(line) == list:
                keyboard.add(*line)
            elif callable(line):
                keyboard.add()
            elif type(line) == dict:
                if line["type"] == "link":
                    btn = InlineKeyboardButton(line["title"], line["link"])
                    keyboard.add(btn)
            else:
                keyboard.add(line)

        return keyboard
