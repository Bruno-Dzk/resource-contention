import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

RESULTS_PATH = 'test_results'

def main():
    labels, dfs = get_data()

    n = len(dfs)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=(16,10),
        sharex=True,
        sharey=True,
    )

    if len(dfs) == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for ax, df, label in zip(axes, dfs, labels):
        # Normalize the series
        df['perf'] = df['perf'][0] / df['perf']
        ax.plot(df["footprint_mb"], df["perf"], marker="o", markersize=4)
        ax.set_title(label)
        ax.set_xlabel("MemBW footprint (MB)")
        ax.set_ylabel("Performance (norm.)")
        xticks = np.arange(0, 128, 16)
        ax.set_xticks(xticks)
        ax.set_xlim([0, 112])
        ax.grid(True)

    for ax in axes[n:]:
        fig.delaxes(ax)

    plt.tight_layout()
    output_path = f"{RESULTS_PATH}/sensitivity.png"
    plt.savefig(output_path, dpi=300)
    plt.close()


def get_data() -> tuple[list[str], list[pd.DataFrame]]:
    csv_files = [f"{RESULTS_PATH}/sensitivity/" + f for f in os.listdir(f"{RESULTS_PATH}/sensitivity") if f.endswith(".csv")]
    labels = [f.split("_")[2] for f in csv_files]
    dfs = [pd.read_csv(f, delimiter=" ") for f in csv_files]
    return labels, dfs


if __name__ == "__main__":
    main()
