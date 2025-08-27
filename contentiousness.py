import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import csv

RESULTS_DIR = 'test_results'

def construct_sensitivity_lookup():
    res = []
    with open(f'{RESULTS_DIR}/reporter_sensitivity.csv', 'r') as f:
        reader = csv.reader(f, delimiter=" ")
        next(reader)
        for row in reader:
            # Average the stream and rand values
            perf = (float(row[1]) + float(row[2])) / 2
            # We perform reverse lookup, that is we find dial from performance
            dial = int(row[0])
            res.append((perf, dial))
    return res

def find_dial(sample_perf: float, lookup: list[tuple[float, int]]) -> int:
    min_diff = math.inf
    res = -1
    for perf, dial in lookup:
        diff = abs(sample_perf - perf)
        if diff < min_diff:
            res = dial
            min_diff = diff
    return res

def get_contentiousness():
    res = {}
    with open(f"{RESULTS_DIR}/contentiousness.csv", 'r') as f:
        reader = csv.reader(f, delimiter=" ")
        next(reader)
        for row in reader:
            res[row[0]] = float(row[1])
    return res

def save_contentiousness(scores: dict[float, int]):
    with open(f"{RESULTS_DIR}/contentiousness_scores.csv", "w") as f:
        for bench, score in scores.items():
            f.write(f"{bench} {score}\n")

def main():
    lookup = construct_sensitivity_lookup()
    cont = get_contentiousness()
    data = {}
    for bench, perf in cont.items():
        dial = find_dial(perf, lookup)
        data[bench] = dial

    print(data)
    save_contentiousness(data)

        # Extract keys and values
    labels = list(data.keys())
    values = list(data.values())

    values, labels = zip(*sorted(zip(values, labels)))

    labels = [
        l.replace('.', '_').split('_')[1]
        for l
        in labels
    ]

    # Create the column chart
    plt.figure(figsize=(20, 12))
    bars = plt.bar(labels, values)

    plt.tick_params(axis='x', length=0)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2, 
            height + 0.2, 
            f'{height}', 
            ha='center', va='bottom'
        )

    # Labels and title
    plt.xlabel('SPEC CPU 2017 workload')
    plt.ylabel('Approximate MemBW benchmark footprint (MB)')

    # Display the chart
    plt.tight_layout()
    output_path = f"{RESULTS_DIR}/contentiousness.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
