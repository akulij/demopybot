from aiogram import asyncio

from modules.config import config
from modules.db import DB, TaskV1
from main import BotRunner


async def main(runner: BotRunner, db: DB):
    while True:
        task_pool: list[TaskV1] = await db.get_tasks()
        for task in task_pool:
            if task.type == "send_message":
                userid = task.taskdesc["userid"]
                message = task.taskdesc["message"]

                await runner.bot.send_message(userid, message)

                await db.delete_task(task)
                await db.set_message_sended(userid, runner.config.botname, message)


if __name__ == "__main__":
    runner = BotRunner(config)
    db = DB(config)
    asyncio.run(main(runner, db))
