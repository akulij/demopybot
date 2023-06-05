import aiogram
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from modules.dbtg import DBTG
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
        
        @self.dp.message_handler(commands=["start"])
        async def start(message: Message):
            user = await self.db.get_user(message.from_user)
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
                    await self.db.db.set_user_state(user, "editfaq_content_{faq.id}")
                    await message.answer("Введите ответ")
                elif editing_part == "content":
                    faq.answer = message.text
                    await self.db.db.append_faq(faq)
                    await self.db.db.set_user_state(user, "main")
                    await message.answer("Завершено!")
            else:
                if message.text in basic_dialog.keys():
                    if message.text == config.support:
                        await self.db.db.set_user_state(user, "message_support")
                    answer = basic_dialog[message.text]
                    if type(answer) == str:
                        await message.answer(answer)
                    elif type(answer) == dict:
                        keyboard = None
                        if "keyboard_inline" in answer.keys():
                            keyboard = await self.ik.get(answer["keyboard_inline"])
                        await message.answer(answer["text"], reply_markup=keyboard)
                    else:
                        raise NotImplemented

