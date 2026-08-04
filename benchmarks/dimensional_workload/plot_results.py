#!/usr/bin/env python3
"""Plot fitting workload by number of variables from recorded CSV results."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
RESULTS_FILE = HERE / "results" / "timings.csv"
OUTPUT_FILE = HERE / "figures" / "dimensional_workload.png"
STYLE_FILE = REPOSITORY_ROOT / "styles" / "trasgu.mplstyle"

BLUE = "#0072B2"
ORANGE = "#D55E00"


def compact_number(value: float, _position: int) -> str:
    """Format large tick values using compact decimal suffixes."""
    for divisor, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if value >= divisor:
            return f"{value / divisor:g}{suffix}"
    return f"{value:g}"


def load_results(path: Path) -> list[dict[str, str]]:
    """Load and validate the recorded benchmark summary."""
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"No benchmark rows found in {path}")
    return rows


def main() -> None:
    plt.style.use(STYLE_FILE)
    rows = load_results(RESULTS_FILE)

    variables = [int(row["variables"]) for row in rows]
    times = [float(row["estimated_total_minutes"]) for row in rows]
    matrices = [int(row["matrices"]) for row in rows]
    time_labels = [row["display_time"] for row in rows]

    fig, time_axis = plt.subplots(figsize=(10, 5.5))
    matrix_axis = time_axis.twinx()
    matrix_axis.grid(False)

    width = 0.36
    time_positions = [value - width / 2 for value in variables]
    matrix_positions = [value + width / 2 for value in variables]

    time_bars = time_axis.bar(
        time_positions,
        times,
        width=width,
        color=BLUE,
        label="Estimated fitting time",
    )
    matrix_bars = matrix_axis.bar(
        matrix_positions,
        matrices,
        width=width,
        color=ORANGE,
        label="Chimera matrices",
    )

    time_axis.set(
        xlabel="Number of variables",
        ylabel="Estimated fitting time (minutes)",
        xticks=variables,
        yscale="log",
    )
    matrix_axis.set_ylabel("Number of matrices")
    matrix_axis.set_yscale("log")
    matrix_axis.yaxis.set_major_formatter(FuncFormatter(compact_number))
    time_axis.tick_params(axis="y", colors=BLUE)
    matrix_axis.tick_params(axis="y", colors=ORANGE)

    for bar, label in zip(time_bars, time_labels):
        time_axis.annotate(
            label,
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(-3, 4),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color=BLUE,
        )
    for bar, value in zip(matrix_bars, matrices):
        matrix_axis.annotate(
            f"{value:,}",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(3, 4),
            textcoords="offset points",
            ha="left",
            fontsize=8,
            color=ORANGE,
        )

    handles = [time_bars, matrix_bars]
    time_axis.legend(handles, [item.get_label() for item in handles], loc="upper left")
    time_axis.set_title("Vine fitting workload by dimensionality")
    fig.tight_layout()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE)
    plt.close(fig)
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
