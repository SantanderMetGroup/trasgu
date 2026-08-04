#!/usr/bin/env python3
"""Rebuild the repeated-fit and sample-size AIC summary tables."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import yaml


ANALYSIS_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = ANALYSIS_DIR.parent
SAMPLE_SIZES = (100, 300, 600, 1000, 1500, 2000, 2500, 3000)
REPEATED_ITERATIONS = range(1, 101)
AIC_FIELDS = (
    "vine_id",
    "aic_vine",
    "aic_dissmann",
    "aic_fixed_matrix_clayton",
    "aic_ground_truth",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_root",
        type=Path,
        help="extracted Zenodo data root containing numeric sample-size directories",
    )
    return parser.parse_args()


def read_iteration(
    input_root: Path, sample_size: int, iteration: int
) -> dict[str, str]:
    run_dir = input_root / str(sample_size) / "simulations" / f"iteration_{iteration}"
    with (run_dir / "best_vine_fit.txt").open(encoding="utf-8", newline="") as stream:
        vine_id, _, aic_vine = next(csv.reader(stream))
    with (run_dir / "references.yaml").open(encoding="utf-8") as stream:
        references = yaml.safe_load(stream)

    return {
        "vine_id": vine_id,
        "aic_vine": aic_vine,
        "aic_dissmann": str(references["aic_dissmann"]),
        "aic_fixed_matrix_clayton": str(references["aic_fixed_matrix_clayton"]),
        "aic_ground_truth": str(references["aic_ground_truth"]),
    }


def write_csv(
    path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    repeated_rows = [
        read_iteration(args.input_root, 300, iteration)
        for iteration in REPEATED_ITERATIONS
    ]
    repeated_path = EXPERIMENT_DIR / "repeated_300" / "results" / "aic_comparison.csv"
    write_csv(repeated_path, AIC_FIELDS, repeated_rows)

    sample_size_rows = []
    for sample_size in SAMPLE_SIZES:
        row = {"sample_size": str(sample_size), "iteration": "1"}
        row.update(read_iteration(args.input_root, sample_size, 1))
        sample_size_rows.append(row)
    sample_size_path = (
        EXPERIMENT_DIR
        / "sample_size_scaling"
        / "results"
        / "sample_size_aic_comparison.csv"
    )
    write_csv(
        sample_size_path,
        ("sample_size", "iteration", *AIC_FIELDS),
        sample_size_rows,
    )

    print(repeated_path)
    print(sample_size_path)


if __name__ == "__main__":
    main()
