import asyncio
from websockets.asyncio.client import connect

async def main():
    async with connect("ws://145.100.131.48:31001/delivery/control/api/") as ws:
        await ws.send("Hello world")

if __name__ == "__main__":
    asyncio.run(main())