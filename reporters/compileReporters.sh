#!/usr/bin/env bash
set -euo pipefail

INCLUDES="-I../benchmark/include"
LIBS="-L../benchmark/build/src -lbenchmark -pthread -static-libstdc++ -static-libgcc"

for src in reporter.cc sledge_reporter.cc rand_reporter.cc stream_reporter.cc; do
  out="${src%.cc}"
  echo "Compiling $src -> $out"
  g++ -std=c++11 -O2 $INCLUDES "$src" $LIBS -o "$out"
done

echo "All done."