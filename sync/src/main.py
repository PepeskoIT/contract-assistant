import asyncio

from sync import runner


async def main():
    while True:
        await runner()
        await asyncio.sleep(3600)

asyncio.run(main())
