package main

import (
	"context"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/valkey-io/valkey-go"
)

func getBuckets() []float64 {
	res := []float64{}
	for i := 0; i <= 10000; i += 100 {
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

const N_KEYS = 1000

var keys = make([]string, N_KEYS)

var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func randSeq(n int) string {
	b := make([]rune, n)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}

const DEFAULT_VALUE_SIZE = 400_000

func getDbSize(ctx context.Context) (int64, error) {
	cmd := client.B().Dbsize().Build()
	size, err := client.Do(ctx, cmd).AsInt64()
	if err != nil {
		return -1, err
	}
	return size, nil
}

func flushAll(ctx context.Context) error {
	cmd := client.B().Flushall().Build()
	return client.Do(ctx, cmd).Error()
}

func initKeys(w http.ResponseWriter, req *http.Request) {
	ctx := context.Background()
	dbSize, err := getDbSize(ctx)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if dbSize != 0 {
		err := flushAll(ctx)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	valueSize, err := strconv.Atoi(os.Getenv("VALUE_SIZE"))
	if err != nil {
		valueSize = DEFAULT_VALUE_SIZE
	}

	for i := 0; i < N_KEYS; i++ {
		key := uuid.New().String()
		keys[i] = key

		value := randSeq(valueSize)
		setCmd := client.B().Set().Key(key).Value(value).Build()

		err := client.Do(ctx, setCmd).Error()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	w.Header().Set("Content_Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

const KEYS_PER_REQUEST = 50

func handleRequest(w http.ResponseWriter, _ *http.Request) {
	ctx := context.Background()
	cmds := make(valkey.Commands, 0, KEYS_PER_REQUEST)
	for i := 0; i < KEYS_PER_REQUEST; i++ {
		key := keys[rand.Intn(N_KEYS)]
		cmds = append(cmds, client.B().Get().Key(key).Build())
		
	}

	start := time.Now()
	for _, resp := range client.DoMulti(ctx, cmds...) {
		if err := resp.Error(); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}
	elapsed := time.Since(start).Microseconds()
	reqDuration.WithLabelValues("fixed").Observe(float64(elapsed))

	w.WriteHeader(http.StatusOK)
}

func init() {
	clientUrl := os.Getenv("CLIENT_URL")
	if clientUrl == "" {
		panic("Client url not set")
	}

	var err error
	client, err = valkey.NewClient(
		valkey.ClientOption{
			InitAddress: []string{clientUrl},
			ClusterOption: valkey.ClusterOption{
				ShardsRefreshInterval: 0,
			},
			DisableCache:          true,
			DisableAutoPipelining: true,
		},
	)
	if err != nil {
		panic(err)
	}
}

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/query/{test-id}", handleRequest).Methods("GET")
	r.HandleFunc("/init", initKeys).Methods("POST")
	r.Handle("/metrics", promhttp.Handler()).Methods("GET")
	log.Fatal(http.ListenAndServe("0.0.0.0:3003", r))
}
