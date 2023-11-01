from aiogram.types import InlineKeyboardButton
from modules.db import DB


async def get_faqs(db: DB, user: None = None):
    faqs = await db.get_faq()

    return list(map(lambda f: InlineKeyboardButton(f.question, callback_data=f"faq_{f.id}"), faqs))

async def get_info_faqs(db: DB, user: None = None):
    faqs = await db.get_faq()

    return list(map(lambda f: InlineKeyboardButton(f.question, callback_data=f"info_{f.id}"), faqs))

async def get_delete_faqs(db: DB, user: None = None):
    faqs = await db.get_faq()

    return list(map(lambda f: InlineKeyboardButton(f.question, callback_data=f"delete_{f.id}"), faqs))

# async def get_bots_ikbd(db: DB, user: UserV1):
async def get_bots_ikbd(db: DB, user):
    return [
               InlineKeyboardButton("Добавление пабликов", callback_data="bots_add_chat"),
               InlineKeyboardButton("Изменить никнейм", callback_data="bots_change_nickname"),
               InlineKeyboardButton("Изменить название акаунта", callback_data="bots_change_username"),
               InlineKeyboardButton("Изменить аватар", callback_data="bots_change_avatar"),
               InlineKeyboardButton("Изменить описание", callback_data="bots_change_description"),
           ]
