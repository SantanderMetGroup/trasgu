#!/usr/bin/env python3

import argparse
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, spearmanr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure Spearman and Kendall correlations for an input data file."
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input file containing one observation per row.",
    )
    return parser.parse_args()


def load_data(input_file: Path) -> np.ndarray:
    data = np.loadtxt(input_file)
    if data.ndim != 2:
        raise ValueError(
            f"Expected a 2D data matrix in {input_file}, got an array with "
            f"{data.ndim} dimension(s)."
        )
    return data


def main() -> None:
    args = parse_args()
    data = load_data(args.input_file)

    spearman = spearmanr(data).statistic

    kendall = np.eye(data.shape[1])
    for i in range(data.shape[1]):
        for j in range(i + 1, data.shape[1]):
            correlation = kendalltau(data[:, i], data[:, j]).statistic
            kendall[i, j] = correlation
            kendall[j, i] = correlation

    print("Spearman:")
    print(spearman)
    print("\nKendall:")
    print(kendall)


if __name__ == "__main__":
    main()
