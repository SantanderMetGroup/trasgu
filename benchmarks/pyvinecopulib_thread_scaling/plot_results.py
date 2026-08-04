#!/usr/bin/env python3
"""Plot measured pyvinecopulib thread scaling and parallel efficiency."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
RESULTS_FILE = HERE / "results" / "thread_summary.csv"
OUTPUT_STEM = HERE / "figures" / "thread_scaling"
STYLE_FILE = REPOSITORY_ROOT / "styles" / "trasgu.mplstyle"

BLUE = "#0072B2"


def load_results(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load measured median timings from CSV."""
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"No benchmark rows found in {path}")
    threads = np.array([int(row["threads"]) for row in rows])
    times_ms = np.array([float(row["median_time_ms"]) for row in rows])
    if threads[0] != 1:
        raise ValueError("The first benchmark row must contain the one-thread baseline")
    return threads, times_ms


def main() -> None:
    plt.style.use(STYLE_FILE)
    threads, times_ms = load_results(RESULTS_FILE)
    speedup = times_ms[0] / times_ms
    efficiency = speedup / threads

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))

    axes[0].plot(threads, speedup, marker="o", color=BLUE)
    axes[0].set(
        xlabel="Allocated CPUs",
        ylabel=r"Speedup $S(p)=T(1)/T(p)$",
        title="(a) Scaling",
        xlim=(0, 50),
        xticks=np.arange(0, 49, 8),
    )

    axes[1].plot(threads, efficiency, marker="o", color=BLUE)
    axes[1].set(
        xlabel="Allocated CPUs",
        ylabel=r"Parallel efficiency $E(p)=S(p)/p$",
        title="(b) Parallel efficiency",
        xlim=(0, 50),
        ylim=(0, 1.05),
        xticks=np.arange(0, 49, 8),
    )

    fig.suptitle("Thread scaling for one eight-dimensional vine fit")
    fig.tight_layout()

    OUTPUT_STEM.parent.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf", "svg"):
        output = OUTPUT_STEM.with_suffix(f".{extension}")
        fig.savefig(output)
        print(output)
    plt.close(fig)


if __name__ == "__main__":
    main()
