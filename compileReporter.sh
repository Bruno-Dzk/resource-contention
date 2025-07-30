#!/bin/bash

set -oe pipefail

g++ reporter.cc -std=c++11 -O2 -Ibenchmark/include -Lbenchmark/build/src -lbenchmark -lpthread -static-libstdc++ -static-libgcc -o reporter
