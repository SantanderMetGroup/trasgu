#!/usr/bin/env python3
"""Rebuild the AIC table from the retained per-iteration results."""

import argparse
import csv
from pathlib import Path

import yaml

FIELDS = (
    "iteration",
    "vine_id",
    "aic_vine",
    "aic_dissmann",
    "aic_fixed_matrix_clayton",
    "aic_ground_truth",
)
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "results/aic_comparison.csv"


def read_iteration(input_root, iteration):
    run = input_root / f"iteration_{iteration}"
    with (run / "best_vine_fit.txt").open(newline="") as stream:
        vine_id, _, aic = next(csv.reader(stream))
    references = yaml.safe_load((run / "references.yaml").read_text())
    return dict(
        iteration=iteration,
        vine_id=vine_id,
        aic_vine=aic,
        **{key: references[key] for key in FIELDS[3:]},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_root",
        type=Path,
        help="Directory containing iteration_1, ..., iteration_100",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 100:
        parser.error("--iterations must be between 1 and 100")
    rows = [read_iteration(args.input_root, i) for i in range(1, args.iterations + 1)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(args.output)


if __name__ == "__main__":
    main()
