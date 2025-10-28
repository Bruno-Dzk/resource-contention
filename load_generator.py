from abc import ABC, abstractmethod
import logging
from datetime import datetime, timezone
import json
import asyncio
import websockets
from websockets.asyncio.client import connect

class LoadGenerator(ABC):

    @abstractmethod
    async def generate(self):
        pass

class MdsLoadGenerator(LoadGenerator):
    HOST = "ws://145.100.131.48:31001/delivery/control/api/"

    @staticmethod
    def _load_cmds_from_file(cmd_file):
        with open(cmd_file, 'r') as fd:
            commands = json.load(fd)
            d = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            return json.dumps({
                "header": {
                    "oid":"1.5.2.3.4.2.1003",
                    "tid": "e8e711bc-1d0c-418c-b6e4-d4119db1af30",
                    "timestampe": d
                },
                "commands": commands 
                })
        
    async def _send_cmds(self, ws: websockets.ClientConnection, cmds):
        await ws.send(cmds)
        result = await ws.recv()
        logging.debug(f"received {result}")

    async def generate(self, requests_file: str):
        logging.info(f"Connecting to websocket: {MdsLoadGenerator.HOST}")
        async with connect(MdsLoadGenerator.HOST) as ws:
            commands = self._load_cmds_from_file(requests_file)
            await self._send_cmds(ws, commands)
        logging.info("Websocket connection closed")

if __name__ == "__main__":
    logging.basicConfig()
    gen = MdsLoadGenerator()
    asyncio.run(gen.generate("load/requests.json"))

