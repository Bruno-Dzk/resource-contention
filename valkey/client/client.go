package main

import (
	"context"
	"log"
	"math/rand"
	"net/http"
	"time"

	// "runtime/debug"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/valkey-io/valkey-go"
)

func getBuckets() []float64 {
	res := []float64{}
	for i := 10; i <= 1000; i += 10 {
		res = append(res, float64(i))
	}
	return res
}

var (
	client      valkey.Client
	reqDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "req_duration_micros",
			Help: "Latency of requests in microseconds.",
			// Buckets: []float64{100_000, 150_000, 200_000, 250_000, 300_000, 500_000, 800_000, 1_000_000},
			// Buckets: []float64{500, 1000, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000, 25000, 30000},
			Buckets: getBuckets(),
		},
		[]string{"test-id"},
	)
)

// var (
// 	client      valkey.Client
// 	reqDuration = promauto.NewSummaryVec(
// 		prometheus.SummaryOpts{
// 			Name: "req_duration_nanos",
// 			Help: "Latency of calls to valkey.Client in microseconds.",
// 			Objectives: map[float64]float64{
// 				0.5:  0.001, // 50th percentile with 0.1% tolerated error
// 			},
// 			MaxAge: time.Minute * 1, // Expire after 1 minute
// 		},
// 		[]string{"test-id"},
// 	)
// )

// const N = 2_000_000

// func handleRequest(w http.ResponseWriter, req *http.Request) {
// 	params := mux.Vars(req)
// 	testId := params["test-id"]

// 	arr := make([]float64, N)

// 	start := time.Now()

// 	for i := 0; i < N / 2; i++ {
// 		arr[i] = arr[i + N / 2] * 3.0
// 	}

// 	for i := N / 2; i < N; i++ {
// 		arr[i] = arr[i - N / 2] * 3.0
// 	}

// 	elapsed := time.Since(start).Microseconds()
// 	reqDuration.WithLabelValues(testId).Observe(float64(elapsed))

// 	w.Header().Set("Content_Type", "application/json")
// 	w.WriteHeader(http.StatusOK)

// 	res := struct{Duration int}{Duration: int(elapsed)}
// 	json.NewEncoder(w).Encode(res)
// }

const N_KEYS = 100_000

var keys = make([]string, N_KEYS)
var are_keys_initialized = false

var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func randSeq(n int) string {
    b := make([]rune, n)
    for i := range b {
        b[i] = letters[rand.Intn(len(letters))]
    }
    return string(b)
}

const VALUE_SIZE = 1600

func initKeys(w http.ResponseWriter, req *http.Request) {
	if are_keys_initialized {
		http.Error(w, "Keys already initialized", http.StatusConflict)
	}

	ctx := context.Background()

	for i := 0; i < N_KEYS; i++ {
		key := uuid.New().String()
		keys[i] = key
		
		value := randSeq(VALUE_SIZE)
		setCmd := client.B().Set().Key(key).Value(value).Build()

		err := client.Do(ctx, setCmd).Error()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}

		are_keys_initialized = true
		w.Header().Set("Content_Type", "application/json")
		w.WriteHeader(http.StatusOK)
	}
}

var clientChan = make(chan string)

func valkeyClient(ch chan string) {
	var err error
	client, err = valkey.NewClient(
		valkey.ClientOption{
			InitAddress: []string{"valkey-server-clone:6379"},
			ClusterOption: valkey.ClusterOption{
				ShardsRefreshInterval: 0,
			},
			DisableCache:         true,
			DisableAutoPipelining: true,
		},
	)
	if err != nil {
		panic(err)
	}

	ctx := context.Background()

	for key := range ch {
		getCmd := client.B().Get().Key(key).Build()

		start := time.Now()
		client.Do(ctx, getCmd).ToString()

		elapsed := time.Since(start).Microseconds()
		reqDuration.WithLabelValues("fixed").Observe(float64(elapsed))
	}
}

func handleRequest(w http.ResponseWriter, _ *http.Request) {
	
	key := keys[rand.Intn(N_KEYS)]
	clientChan <- key

	w.WriteHeader(http.StatusOK)
}

const NUM_CLIENTS = 5000

func init() {
	// debug.SetGCPercent(80)
	for i := 0; i < NUM_CLIENTS; i++ {
		go valkeyClient(clientChan)
	}
}

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/query/{test-id}", handleRequest).Methods("GET")
	r.HandleFunc("/init", initKeys).Methods("POST")
	r.Handle("/metrics", promhttp.Handler()).Methods("GET")
	log.Fatal(http.ListenAndServe("0.0.0.0:3003", r))
}
