#!/usr/bin/env bash
set -euo pipefail

INCLUDES="-I../benchmark/include"
LIBS="-L../benchmark/build/src -lbenchmark -pthread -static-libstdc++ -static-libgcc"
BUILD_DIR="../build"
mkdir -p "$BUILD_DIR"

for src in altern_reporter.cc hybrid_reporter.cc rand_reporter.cc stream_reporter.cc; do
  base="${src%.cc}"
  out="${BUILD_DIR}/${base}.out"
  echo "Compiling $src -> $out"
  g++ -std=c++11 -O2 $INCLUDES "$src" $LIBS -o "$out"
done

echo "All done."