import asyncio

import aiogram
from aiogram.types import InputFile, Message, user
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.text_decorations import html

from modules.dbtg import DBTG
from modules.db import DB
from modules.keyboards import ReplyKeyboard, InlineKeyboard
from modules.config import config as cfg

from . import config
from .config import basic_dialog


class DialogConfigurer:
    def __init__(self, dispatcher: aiogram.Dispatcher, db_provider: DBTG):
        self.dp = dispatcher
        self.db = db_provider
        self.rk = ReplyKeyboard(self.db)
        self.ik = InlineKeyboard(self.db)
        
        @self.dp.message_handler(content_types=["photo"])
        async def photo(message: Message):
            user = await self.db.get_user(message.from_user)
            if not (user.is_admin and user.state == "post_image"):
                await message.answer("Зачем вы отправили мне фотографию...")
                return
            photo = message.photo[-1]
            await photo.download(destination_file="post.png")
            await self.db.db.set_user_state(user, "post_text_img")
            await message.answer("Картинка установлена. Введите текст поста (поддерживается форматирование Телеграма)")
        
        @self.dp.message_handler(commands=["start"])
        async def start(message: Message):
            args = message.get_args() if message.get_args() else ""
            print(args)
            user = await self.db.get_user(message.from_user, start_args=str(args))
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for q in basic_dialog.keys():
                keyboard.add(q)
            keyboard = await self.rk.get("main")
            await message.answer(config.greeting, reply_markup=keyboard)

        @self.dp.message_handler()
        async def map(message: Message):
            user = await self.db.get_user(message.from_user)
            if user.state == "message_support":
                msg_text = message.html_text
                msg_text = f"Вопрос от: @{message.from_user.username}\n" + msg_text
                await self.dp.bot.send_message(cfg.support_chatid, msg_text, "HTML")
                await self.db.db.set_user_state(user, "main")
                await message.answer(config.sended_support)
            elif user.state.startswith("editfaq") and user.is_admin:
                _, editing_part, faqid = user.state.split("_")
                faqid = int(faqid)
                faq = await self.db.db.get_faq(faqid=faqid)
                faq = faq[0]
                if editing_part == "title":
                    faq.question = message.text
                    await self.db.db.append_faq(faq)
                    await self.db.db.set_user_state(user, f"editfaq_content_{faq.id}")
                    await message.answer("Введите ответ")
                elif editing_part == "content":
                    faq.answer = message.html_text
                    faq.category = "main"
                    await self.db.db.append_faq(faq)
                    await self.db.db.set_user_state(user, "main")
                    await message.answer("Завершено!")
            elif user.state == "post_image":
                await self.db.db.set_user_state(user, "post_text_noimg")
                await message.answer("Отлично, значит без фото.\nВведите текст для поста")
            elif user.state.startswith("post_text"):
                # imgtype == img or noimg
                _, _, imgtype = user.state.split("_")
                await self.db.db.set_user_state(user, "main")
                await message.answer("В процессе...")
                await notificate_users(message.html_text, imgtype, self.db.db, self.dp)
                await message.answer("Все пользователи уведомлены!")
            else:
                if message.text in basic_dialog.keys():
                    if message.text == config.support:
                        await self.db.db.set_user_state(user, "message_support")
                    answer = basic_dialog[message.text]
                    if type(answer) == str:
                        await message.answer(answer)
                    elif type(answer) == dict:
                        if "file" in answer.keys():
                            file = answer["file"]
                            await self.dp.bot.send_document(message.from_user.id, file, caption=answer["text"])
                            return
                        keyboard = None
                        if "keyboard_inline" in answer.keys():
                            keyboard = await self.ik.get(answer["keyboard_inline"])
                        await message.answer(answer["text"], reply_markup=keyboard)
                    else:
                        raise NotImplemented


async def notificate_users(html_text: str, imgtype: str, db_provider: DB, dp: aiogram.Dispatcher):
    users = await db_provider.get_all_user_ids()
    for userid in users:
        if imgtype == "img":
            await dp.bot.send_photo(userid, InputFile("post.png"), html_text, "HTML")
        else:
            await dp.bot.send_message(userid, html_text, "HTML")
        await asyncio.sleep(0)
