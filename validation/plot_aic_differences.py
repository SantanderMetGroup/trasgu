#!/usr/bin/env python3
"""Plot empirical AIC differences from a validation summary."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parent
STYLE_FILE = REPOSITORY_ROOT / "styles" / "trasgu.mplstyle"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="validation aic_comparison.csv")
    parser.add_argument(
        "--output",
        type=Path,
        help="output figure (default: aic_differences.png next to the input)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output or args.input.with_name("aic_differences.png")
    required = {"aic_vine", "aic_dissmann", "aic_fixed_matrix_clayton"}
    with args.input.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{args.input} is missing columns: {', '.join(sorted(missing))}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"{args.input} contains no validation rows")

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
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
