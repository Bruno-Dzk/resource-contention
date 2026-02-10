#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <float.h>
#include <sched.h>
#include <set>
#include <iostream>
#include <benchmark/benchmark.h>

#define FOOTPRINT_SIZE 16000000
#define STREAM_SIZE (FOOTPRINT_SIZE / 2)
#define RAND_SIZE (FOOTPRINT_SIZE / 2)
#define PADDING_SIZE 400000

unsigned lfsr;
#define MASK 0xd0000001u
#define rand (lfsr = (lfsr >> 1) ^ (-(int)(lfsr & 1u) & MASK))
#define r (rand % RAND_SIZE)

static double bw_data [STREAM_SIZE + 2 * PADDING_SIZE];
static unsigned int data_chunk [RAND_SIZE];
static double scalar = 3.0;
static unsigned int dump[10];

void streaming_access(benchmark::State& state) {
    //std::cout << "STREAM thread: " << state.thread_index() << " executed on CPU: " << sched_getcpu() << std::endl;
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

void random_access(benchmark::State& state) {
    //std::cout << "RAND thread: " << state.thread_index() << " executed on CPU: " << sched_getcpu() << std::endl;
    for (auto _ : state) {
        lfsr = 0xACE1u;
        for (int i = 0; i < RAND_SIZE / 100; i++) {
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

BENCHMARK(streaming_access);
BENCHMARK(random_access);

BENCHMARK_MAIN();
