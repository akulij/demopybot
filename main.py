from modules.config import Settings
from aiogram import Bot, Dispatcher


class BotRunner:
    def __init__(self, config: Settings):
        self.config = config
        self.bot = Bot(config.bot_token)
        self.dp = Dispatcher(self.bot)

        self.init_modules()

    def init_modules(self):
        from modules import (
                dialogs,
                callback_handler,
                commands,
                userstat,
                )
        from modules.db import DB
        from modules.dbtg import DBTG
        db = DB(self.config)
        dbtg = DBTG(db)
        active = [
                commands.Commands(self.dp, dbtg),
                dialogs.DialogConfigurer(self.dp, dbtg),
                callback_handler.CallbackHandler(self.dp, dbtg),
                userstat.UserStat(self.dp, dbtg)
                ]


if __name__ == '__main__':
    from aiogram import executor
    from modules.config import config
    bot = BotRunner(config)
    executor.start_polling(bot.dp, skip_updates=True)
