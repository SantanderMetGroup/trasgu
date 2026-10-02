#!/usr/bin/env python3
"""Check all retained Clayton inputs, compact results and the full case-99 table."""

import argparse
import csv
import hashlib
import math
from pathlib import Path

import numpy as np
import yaml


def verify(package):
    runs = package / "simulations"
    expected = {f"iteration_{i}" for i in range(1, 101)}
    if {p.name for p in runs.iterdir() if p.is_dir()} != expected:
        raise ValueError("Expected exactly iterations 1–100")
    with (package / "results/aic_comparison.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    if [int(row["iteration"]) for row in rows] != list(range(1, 101)):
        raise ValueError("Summary must contain iterations 1–100 in order")
    hashes = set()
    for row in rows:
        run = runs / f"iteration_{row['iteration']}"
        data_path = run / "vinecop_samples.txt"
        data = np.loadtxt(data_path, ndmin=2)
        if (
            data.shape != (300, 7)
            or not np.isfinite(data).all()
            or not ((data > 0) & (data < 1)).all()
        ):
            raise ValueError(f"Invalid observations: {data_path}")
        hashes.add(hashlib.sha256(data_path.read_bytes()).hexdigest())
        with (run / "best_vine_fit.txt").open() as stream:
            vine_id, npars, aic = next(csv.reader(stream))
        if int(vine_id) != int(row["vine_id"]) or not math.isclose(
            float(aic), float(row["aic_vine"]), abs_tol=1e-6
        ):
            raise ValueError(f"Summary mismatch: {run}")
        if not 0 <= int(vine_id) < 2580480 or int(npars) != 21:
            raise ValueError(f"Invalid best fit: {run}")
        references = yaml.safe_load((run / "references.yaml").read_text())
        for key in ("aic_dissmann", "aic_fixed_matrix_clayton", "aic_ground_truth"):
            if not math.isclose(float(references[key]), float(row[key]), abs_tol=1e-6):
                raise ValueError(f"Reference mismatch: {run}, {key}")
        for name in ("best_fit_detailed.txt", "trasgu.yaml", "trasgu_run.log"):
            if not (run / name).is_file():
                raise ValueError(f"Missing {name}: {run}")
    if len(hashes) != 100:
        raise ValueError("The 100 observation files must be distinct")
    full_path = package / "simulations/iteration_99/fit_iteration_99.csv"
    seen = np.zeros(2580480, dtype=bool)
    best = (math.inf, None)
    with full_path.open() as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            i, aic = int(row["vine_id"]), float(row["aic"])
            if not 0 <= i < len(seen) or seen[i] or not math.isfinite(aic):
                raise ValueError(f"Invalid or duplicate full-fit row: {row}")
            seen[i] = True
            if aic < best[0]:
                best = (aic, i)
    if not seen.all():
        raise ValueError("Case 99 does not cover all 2,580,480 matrices")
    row99 = rows[98]
    if best[1] != int(row99["vine_id"]) or not math.isclose(
        best[0], float(row99["aic_vine"]), abs_tol=1e-6
    ):
        raise ValueError("Full case-99 minimum differs from the compact summary")
    recovered = sum(int(r["vine_id"]) == 252000 for r in rows)
    distinct = len({int(r["vine_id"]) for r in rows})
    improved = sum(float(r["aic_vine"]) < float(r["aic_dissmann"]) for r in rows)
    print(
        "Verified 100 distinct 300x7 inputs and 100 compact results; complete case 99."
    )
    print(
        f"Generating matrix selected: {recovered}/100; distinct selected matrices: {distinct}; lower AIC than Dissmann: {improved}/100."
    )
    print(f"Case 99 minimum: vine {best[1]}, AIC {best[0]}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    verify(parser.parse_args().package)
