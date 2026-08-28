#!/usr/bin/env python3
"""Plot the ship-wake AIC CDF and the Dissmann reference value."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EXPERIMENT_DIR = Path(__file__).resolve().parent
INPUT_FILE = EXPERIMENT_DIR / "processed_aic_cdf.npz"
OUTPUT_STEM = EXPERIMENT_DIR / "results" / "large_aic_cdf"
LOCAL_STYLE_FILE = EXPERIMENT_DIR / "styles" / "trasgu.mplstyle"
REPOSITORY_STYLE_FILE = EXPERIMENT_DIR.parents[1] / "styles" / "trasgu.mplstyle"
STYLE_FILE = LOCAL_STYLE_FILE if LOCAL_STYLE_FILE.is_file() else REPOSITORY_STYLE_FILE
DISSMANN_AIC = -560.7392


def main() -> None:
    with np.load(INPUT_FILE, allow_pickle=False) as data:
        x = data["x"]
        cdf = data["cdf"]
        count = int(data["count"])

    OUTPUT_STEM.parent.mkdir(parents=True, exist_ok=True)
    plt.style.use(STYLE_FILE)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.step(x, cdf, where="post", linewidth=1.5)
    ax.axvline(
        DISSMANN_AIC,
        color="#D55E00",
        linestyle="--",
        linewidth=1.5,
    )
    ax.annotate(
        f"Dissmann AIC = {DISSMANN_AIC:.2f}",
        xy=(DISSMANN_AIC, 0.94),
        xycoords=("data", "axes fraction"),
        xytext=(6, 0),
        textcoords="offset points",
        color="#D55E00",
        ha="left",
        va="top",
    )
    ax.set_xlabel("AIC")
    ax.set_ylabel("Empirical cumulative probability")
    ax.set_ylim(-0.02, 1.02)
    fig.tight_layout()

    outputs = [OUTPUT_STEM.with_suffix(suffix) for suffix in (".pdf", ".png")]
    for output_file in outputs:
        fig.savefig(output_file)
    plt.close(fig)
    print(
        f"Saved to {', '.join(str(path) for path in outputs)} ({count:,} finite values)"
    )


if __name__ == "__main__":
    main()
