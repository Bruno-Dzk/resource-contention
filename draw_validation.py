import json
import logging
import matplotlib.pyplot as plt
import math
import textwrap
import numpy as np

logger = logging.getLogger(__name__)


def get_validated():
    with open('results/validated.json', 'r') as f:
        return json.load(f)
    
def draw_validation_chart(data, i: int):
    n = len(data)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(25, 10))

    max_error = 0
    errors = []

    # Normalize axes to a flat list so we can iterate consistently
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for ax, validation_data in zip(axes, data):
        # Build labels and values
        labels = []
        values = []
        ax.set_title(f"{validation_data[0]['name']} + {validation_data[1]['name']}")
        ax.grid(True)
        ax.set_axisbelow(True)
        for datum in validation_data:
            error = datum['perf'] - datum['actual']
            max_error = max(max_error, abs(error))
            errors.append(abs(error))
            labels.extend([
                f"{datum['name']} prediction",
                f"{datum['name']} actual",
                f"{datum['name']} error"
            ])
            values.extend([
                datum['perf'],
                datum['actual'],
                error
            ])
        
        labels = [
            "\n".join(textwrap.wrap(lbl, width=12)) if lbl else lbl
            for lbl in labels
        ]
        x = range(len(labels))
        ax.bar(x, values)

        # rotate labels: use 45 degrees normally, 90 degrees if there are many labels
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        ax.set_xlabel("MemBW footprint (MB)")
        ax.set_ylabel("Performance (norm.)")

    # Hide any unused subplots (if rows*cols > n)
    for ax in axes[len(data):]:
        ax.axis('off')

    plt.tight_layout()
    # make a bit more room at the bottom for rotated labels
    plt.subplots_adjust(bottom=0.18)

    output_path = f"./validation{i}.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    logger.info(f"Max error {max_error}")
    avg_error = sum(errors) / len(errors)
    logger.info(f"Avg error {avg_error}")
    
def main():
    data = get_validated()
    j = 1
    for i in range(0, len(data), 9):
        draw_validation_chart(data[i:i + 9], j)
        j += 1

if __name__ == '__main__':
    main()