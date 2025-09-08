#include <benchmark/benchmark.h>

#define STREAM_SIZE 16000000
#define PADDING_SIZE 400000

static double bw_data [STREAM_SIZE + 2 * PADDING_SIZE];
static double scalar = 3.0;

void smash(benchmark::State& state) {
    for (auto _ : state) {
        double *mid = bw_data + PADDING_SIZE;
        for (int i = 0; i < STREAM_SIZE / 2; i++) {
            bw_data[i]= scalar*mid[i];
        }
        for (int i = 0; i< STREAM_SIZE / 2; i++) {
            mid[i]= scalar*bw_data[i];
        }
    }
}

BENCHMARK(smash);

BENCHMARK_MAIN();
