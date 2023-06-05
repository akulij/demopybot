from aiogram.types import InlineKeyboardButton
from modules.db import DB


async def get_faqs(db: DB, user: None = None):
    faqs = await db.get_faq()

    return list(map(lambda f: InlineKeyboardButton(f.question, callback_data=f"faq_{f.id}"), faqs))

async def get_info_faqs(db: DB, user: None = None):
    faqs = await db.get_faq()

    return list(map(lambda f: InlineKeyboardButton(f.question, callback_data=f"info_{f.id}"), faqs))
