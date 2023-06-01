import asyncio
import csv

from sqlalchemy.exc import IntegrityError

from modules.db import DB
from modules.db import FAQ
from modules.config import config

db = DB(config)


async def migrate_faq(question: str, answer: str):
    faq = FAQ(question=question, answer=answer)
    await db.append_faq(faq)

async def migrate():
    await db.delete_faqs()
    with open("faq.csv", "r") as faqfile:
        faq = csv.reader(faqfile)
    
        for row in faq:
            question, answer = row

            try:
                await migrate_faq(question, answer)
            except IntegrityError:
                print(f"Info: Question {question} exists (how if it were deleted?)")

    print(await db.get_faq())

if __name__ == "__main__":
    asyncio.run(migrate())
