#!/usr/bin/env python3
"""Plot a previously processed AIC CDF and the Dissmann reference value."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
INPUT_FILE = HERE.parent / "processed_aic_cdf.npz"
OUTPUT_FILE = HERE / "large_aic_cdf.png"
STYLE_FILE = REPOSITORY_ROOT / "styles" / "trasgu.mplstyle"
DISSMANN_AIC = -560.74


def main() -> None:
    plt.style.use(STYLE_FILE)
    with np.load(INPUT_FILE, allow_pickle=False) as data:
        x = data["x"]
        cdf = data["cdf"]
        count = int(data["count"])

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.step(x, cdf, where="post")
    ax.axvline(
        DISSMANN_AIC,
        color="tab:red",
        linestyle="--",
        linewidth=1.5,
    )
    ax.annotate(
        f"Dissmann AIC = {DISSMANN_AIC:.2f}",
        xy=(DISSMANN_AIC, 0.95),
        xycoords=("data", "axes fraction"),
        xytext=(6, 0),
        textcoords="offset points",
        rotation=0,
        color="tab:red",
        ha="left",
        va="top",
    )
    ax.set(xlabel="AIC", ylabel="Cumulative probability", title="Distribution of fitted AIC values")
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE)
    plt.close(fig)
    print(f"Saved to {OUTPUT_FILE} ({count:,} finite values)")


if __name__ == "__main__":
    main()
