import asyncio
import csv

from sqlalchemy.exc import IntegrityError

from modules.db import DB
from modules.db import FAQ
from modules.config import config

db = DB(config)


async def migrate_faq(question: str, answer: str, category: str):
    faq = FAQ(question=question, answer=answer, category=category)
    await db.append_faq(faq)

async def migrate():
    await db.delete_faqs()
    with open("faq.csv", "r") as faqfile:
        faq = csv.reader(faqfile, delimiter=";")
    
        for row in faq:
            print(row)
            category, question, answer = row

            try:
                await migrate_faq(question, answer, category=category)
            except IntegrityError:
                print(f"Info: Question {question} exists (how if it were deleted?)")

    print(await db.get_faq())
    print(await db.get_faq("maim"))
    print(await db.get_faq("main"))

if __name__ == "__main__":
    asyncio.run(migrate())
