from aiogram import asyncio

from modules.config import config
from modules.db import DB, TaskV1, UserV1
from main import BotRunner

async def send_message(task: TaskV1, runner: BotRunner, db: DB):
    userid = task.taskdesc["userid"]
    message = task.taskdesc["message"]

    await runner.bot.send_message(userid, message)

    await db.delete_task(task)
    await db.set_message_sended(userid, runner.config.botname, message)

async def notificate_user(task: TaskV1, runner: BotRunner, db: DB):
    users: list[int] = await db.get_inactive_users()
    message = task.taskdesc["message"]

    for userid in users:
        await runner.bot.send_message(userid, message)
        await db.set_message_sended(userid, runner.config.botname, message)

async def main(runner: BotRunner, db: DB):
    while True:
        await asyncio.sleep(0.1)
        task_pool: list[TaskV1] = await db.get_tasks()
        for task in task_pool:
            if task.type == "send_message":
                await send_message(task, runner, db)
            if task.type == "notification_post":
                await notificate_user(task, runner, db)


if __name__ == "__main__":
    runner = BotRunner(config)
    db = DB(config)
    asyncio.run(main(runner, db))
