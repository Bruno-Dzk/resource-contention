// Minimal includes — only what this translation unit actually needs.
#include <benchmark/benchmark.h>

#define FOOTPRINT_SIZE 16000000

unsigned lfsr;
#define MASK 0xd0000001u
#define rand (lfsr = (lfsr >> 1) ^ (-(int)(lfsr & 1u) & MASK))
#define r (rand % FOOTPRINT_SIZE)

static unsigned int data_chunk[FOOTPRINT_SIZE];
static double scalar = 3.0;
static unsigned int dump[10];

void random_access(benchmark::State& state) {
    for (auto _ : state) {
        lfsr = 0xACE1u;
        for (int i = 0; i < FOOTPRINT_SIZE / 100; i++) {
            dump[0] += data_chunk[r]++;
            dump[1] += data_chunk[r]++;
            dump[2] += data_chunk[r]++;
            dump[3] += data_chunk[r]++;
            dump[4] += data_chunk[r]++;
            dump[5] += data_chunk[r]++;
            dump[6] += data_chunk[r]++;
            dump[7] += data_chunk[r]++;
            dump[8] += data_chunk[r]++;
            dump[9] += data_chunk[r]++;
            benchmark::ClobberMemory();
        }
    }
}

BENCHMARK(random_access);

BENCHMARK_MAIN();
