#!/usr/bin/env python3
"""Plot empirical AIC differences for the 100 repeated 300-sample fits."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ANALYSIS_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = ANALYSIS_DIR.parent
REPOSITORY_ROOT = ANALYSIS_DIR.parents[2]
STYLE_FILE = REPOSITORY_ROOT / "styles" / "trasgu.mplstyle"
INPUT_FILE = EXPERIMENT_DIR / "repeated_300" / "results" / "aic_comparison.csv"
OUTPUT_FILE = EXPERIMENT_DIR / "repeated_300" / "results" / "aic_differences.png"


def main() -> None:
    with INPUT_FILE.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"{INPUT_FILE} contains no validation rows")

    differences = {
        "Exhaustive search": np.array(
            [
                abs(float(row["aic_vine"]) - float(row["aic_fixed_matrix_clayton"]))
                for row in rows
            ]
        ),
        "Dissmann algorithm": np.array(
            [
                abs(float(row["aic_dissmann"]) - float(row["aic_fixed_matrix_clayton"]))
                for row in rows
            ]
        ),
    }

    plt.style.use(STYLE_FILE)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for (label, difference), marker in zip(differences.items(), ("o", "x")):
        x = np.sort(difference[np.isfinite(difference)])
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(
            x,
            y,
            linestyle="none",
            marker=marker,
            markerfacecolor="none",
            label=label,
        )

    ax.axvline(0, color="0.45", linestyle="--", linewidth=1)
    ax.set(
        xlabel="Absolute AIC difference from the fixed Clayton structure",
        ylabel="Cumulative proportion of simulations",
        title="AIC differences across simulated datasets",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE)
    plt.close(fig)
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
