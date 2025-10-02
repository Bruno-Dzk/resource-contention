import asyncio
import websockets

message_count = 0

async def handler(websocket, path):
    global message_count
    async for message in websocket:
        message_count += 1
        print(f"Received message {message_count}: {message}")

async def main():
    async with websockets.serve(handler, "localhost", 3000):
        print("WebSocket server listening on ws://localhost:3000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
