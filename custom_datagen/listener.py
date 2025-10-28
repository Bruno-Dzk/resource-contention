import asyncio
import websockets
import avro.schema
import avro.io
import io

DATAGEN_SCHEMA ='''
	{
	"type": "record",
	"name": "DataGenerationNotification",
	"namespace": "nl.esi.techflex.delivery",
	"fields": [
		{ "name": "id", "type": "string" },
		{ "name": "data", "type": {
			"type": "record",
			"name": "DataTransportType",
			"fields": [
			{ "name": "dataList", "type": { "type":"array", "items":"long" } }
			]
		}
		}
	]
	}
'''

schema = avro.schema.parse(DATAGEN_SCHEMA)

async def handler(websocket: websockets.ClientConnection):
    async for message in websocket:
        bytes_reader = io.BytesIO(message)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        notification = reader.read(decoder)
        print(notification["id"])

async def main():
    async with websockets.serve(handler, "localhost", 3000):
        print("WebSocket server listening on ws://localhost:3000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
