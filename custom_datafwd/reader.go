package main

import (
	"fmt"
	"log"

	"github.com/linkedin/goavro/v2"
	"github.com/zeromq/goczmq"
)

const avroSchema = `
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
`

var lfsr int64 = 0xACE1

func deserializePayload(codec *goavro.Codec, payload []byte) error {
	// create a slice of interface{} with int64 values (goavro expects int64 for "long")

	native, _, err := codec.NativeFromBinary(payload)
	if err != nil {
		return err
	}
	fmt.Println(native)
	return nil
}

func main() {
	// create Avro codec
	codec, err := goavro.NewCodec(avroSchema)
	if err != nil {
		log.Fatalf("failed to create avro codec: %v", err)
	}

	// connect to websocket
	// conn, _, err := websocket.DefaultDialer.Dial(WS_URL, nil)
	// if err != nil {
	// 	log.Fatalf("websocket dial error: %v", err)
	// }
	// defer conn.Close()
	// log.Println("connected to", WS_URL)

	sub, err := goczmq.NewSub("tcp://writer:3500", "")
	if err != nil {
		log.Fatal(err)
	}
	defer sub.Destroy()

	fmt.Println("Subscriber connected created and bound")

	for true {
		fmt.Println("HERE")
		frames, err := sub.RecvMessage()
		if err != nil {
			log.Fatal(err)
		}
		message := string(frames[len(frames) - 1])
		fmt.Println("Received message: %s", message)
		
		if len(frames) == 0 {
			continue
		}
		// last frame is the application payload
		payload := frames[len(frames)-1]
		if err := deserializePayload(codec, payload); err != nil {
			log.Printf("deserialize: %v", err)
		}

	}
}
