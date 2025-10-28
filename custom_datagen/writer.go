package main

import (
	"fmt"
	"log"
	"time"
	"math/rand"

	"github.com/linkedin/goavro/v2"
	"github.com/zeromq/goczmq"
)

const (
	BLOCK_SIZE = 50_000
	MASK int64 = 0xd0000001
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

    // #define rand (lfsr = (lfsr >> 1) ^ (-(int)(lfsr & 1u) & MASK))
    // #define r (rand % rand_size)

func generatePayload(codec *goavro.Codec, id int) ([]byte, error) {
	// create a slice of interface{} with int64 values (goavro expects int64 for "long")
	dataList := make([]interface{}, BLOCK_SIZE)
	for i := 0; i < BLOCK_SIZE; i++ {
		// values between 0 and 999 inclusive, like np.random.randint(0,1000)
		dataList[i] = int64(rand.Int63n(1000))
	}

	// encode to Avro binary
	native := map[string]interface{}{
		"id": fmt.Sprintf("req_%d", id),
		"data": map[string]interface{}{
			"dataList": dataList,
		},
	}

	bin, err := codec.BinaryFromNative(nil, native)
	if err != nil {
		return nil, err
	}
	return bin, nil
}

// const ZMQ_URL = "tcp://dataforwardingservice:5501"
const ZMQ_URL = "tcp://*:3500"
const TOPIC = "t1"

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

	pub, err := goczmq.NewPub(ZMQ_URL)
	if err != nil {
		log.Fatal(err)
	}
	defer pub.Destroy()
	log.Println("connected to", ZMQ_URL)

	i := 0
	for true {
		fmt.Printf("Req %d\n", i)
		i++

		t1 := time.Now()
		rawBytes, err := generatePayload(codec, i)
		if err != nil {
			log.Fatalf("generatePayload error: %v", err)
		}
		genMs := float64(time.Since(t1).Nanoseconds()) / 1_000_000.0
		fmt.Printf("Gen time: %.3f ms\n", genMs)

		t2 := time.Now()
		// send as binary message
		if err = pub.SendMessage([][]byte{[]byte(TOPIC), rawBytes}); err != nil {
			log.Fatalf("send topic: %v", err)
		}
		sendMs := float64(time.Since(t2).Nanoseconds()) / 1_000_000.0
		fmt.Printf("Send time: %.3f ms\n", sendMs)

		// sleep 1 ms
		time.Sleep(100 * time.Millisecond)
	}
}
