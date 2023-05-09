import os
import json
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import aiohttp
from uuid import uuid4
import datetime

load_dotenv()
QIWI_TOKEN = os.getenv("QIWI_TOKEN") or "UNDEFINEDTOKEN"
QIWI_TOKEN = "eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6Im56amYzNS0wMCIsInVzZXJfaWQiOiI3OTI5MjAyMjI3MCIsInNlY3JldCI6IjBlMzFmMGMzMDZkMzQ0MzNiYThjOTIzYjg3MTQ3NWRkMTNiNmQ3ZDAzMTE2ZDY5YjljMzI2NDI5YjM1M2IyMzYifX0="

async def generate_bill(amount: float) -> tuple[str, str]:
    """
    amount: float - require amount of RUB
    returns: (bill_id: str(int), payment_url: str)
    """

    # if db.is_bill_exists(user_id): db.remove_bill(user_id)
    # bill_idx = db.create_bill()
    amount: str = str(round(amount, 2))
    bill_id = str(uuid4())
    info = await _get_bill_info(bill_id, amount)

    # bill = await p2p.bill(amount=amount, lifetime=30, comment="Пополнение OLX Parser")
    # bill_id = bill_data[]
    pay_url: str = info["payUrl"]
    return bill_id, pay_url

async def check_bill(bill_id: str):
    return (await _get_bill_info(bill_id))["status"]["value"] == "PAID"

async def generate_bill_keyboard(amount: float):
    bill_id, bill_url = await generate_bill(amount)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Оплатить", url=bill_url))
    keyboard.add(InlineKeyboardButton("🟢Проверить оплату", callback_data=f"check_bill_{bill_id}"))

    return keyboard

async def get_bill_amount(bill_id: str):
    return float((await _get_bill_info(bill_id))["amount"]["value"])

async def _get_bill_info(bill_id: str, amount: str | None = None):
    headers = {
            "Authorization": f"Bearer {QIWI_TOKEN}",
            "content-type": "application/json",
            "accept": "application/json"
            }
    time = datetime.datetime.utcnow()
    time += datetime.timedelta(minutes=30) + datetime.timedelta(hours=3)  # перевожу дельту во время и перевожу UTC в МСК
    expiration_datetime = time.strftime('%Y-%m-%dT%H:%M:00+03:00')
    print(type(expiration_datetime))
    print(expiration_datetime)
    data = {
                "amount": {   
                        "currency": "RUB",   
                        "value": amount 
                    },
                "comment": "Оплата",
                "expirationDateTime": expiration_datetime,
            }
    data = json.dumps(data)
    print(data)

    if amount:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.put(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}", data=data) as response:
                bill_data = await response.json()
    else:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}") as response:
                bill_data = await response.json()

    print(bill_data)

    return bill_data
