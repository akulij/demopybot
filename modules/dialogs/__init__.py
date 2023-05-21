import aiogram
from modules.db import DB


class DialogConfigurer:
    def __init__(self, dispatcher: aiogram.Dispatcher, db: DB):
        self.dispatcher = dispatcher
        self.db = db
