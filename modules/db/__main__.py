from . import *

async def run():
    async with AsyncSession(engine) as session:
        print(await session.connection())


import asyncio
asyncio.run(run())
