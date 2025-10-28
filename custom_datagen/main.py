import asyncio
import random
import websockets
from websockets.asyncio.client import connect
from fastavro import writer, reader, parse_schema, schemaless_writer
from io import BytesIO
import time
import numpy as np

BLOCK_SIZE = 50_000

DATAGEN_SCHEMA = [
    {
    "type": "record",
    "name": "DataTransportType",
    "namespace": "nl.esi.techflex.delivery",
    "fields": [
      {
        "name": "dataList",
        "type": { "type": "array", "items": "long" }
      }
    ]
  },  
  {
    "type": "record",
    "name": "DataGenerationNotification",
    "namespace": "nl.esi.techflex.delivery",
    "fields": [
      { "name": "id", "type": "string" },
      { "name": "data", "type": "DataTransportType" }
    ]
  }
]

schema = parse_schema(DATAGEN_SCHEMA)

def generate_payload(id: int) -> bytes:
    data = np.random.randint(0, 1000, BLOCK_SIZE, dtype=np.int64).tolist()
    bytes_writer = BytesIO()
    schemaless_writer(bytes_writer, schema, {'id': f'req_{id}', 'data': {'dataList': data}})
    return bytes_writer.getvalue()

async def main():
  async with connect("ws://localhost:3000") as websocket:
    for i in range(100):
      t1 = time.time_ns()
      raw_bytes = generate_payload(i)
      print(f"Gen time: {(time.time_ns() - t1) / 1_000_000}")
      t2 = time.time_ns()
      await websocket.send(raw_bytes)
      print(f"Send time: {(time.time_ns() - t2) / 1_000_000}")
      time.sleep(0.001)


if __name__ == "__main__":
    asyncio.run(main())