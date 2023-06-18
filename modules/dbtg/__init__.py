from aiogram.types.user import User as AiogramUser

from modules.db import (
        DB,
        UserV1,
        )

class DBTG:
    def __init__(self, db_provider: DB):
        self.db = db_provider

    async def get_user(self, aiogram_user: AiogramUser) -> UserV1:
        au = aiogram_user
        user = await self.db.get_user_byid(au.id)
        if not user:
            user = UserV1(id=au.id, name=au.first_name, nickname=au.username)
            await self.db.create_user(user)
            await self.db.new_action(user, "register", actionjson={})

            return user

        return user

