#!/usr/bin/env python3
"""Measure Chimera fits on one core; extrapolate the large collections."""

import argparse
import csv
import time
from pathlib import Path

import numpy as np
import pyvinecopulib as pv
import zarr


HERE = Path(__file__).resolve().parent
COUNTS = {4: 24, 5: 480, 6: 23040, 7: 2580480, 8: 660602880}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chimera", help="Path to a local Chimera Zarr store")
    parser.add_argument("--sample", type=int, default=1000, help="Fits for each of 6, 7 and 8 variables")
    parser.add_argument("--output", type=Path, default=HERE / "results" / "timings.csv")
    args = parser.parse_args()
    if args.sample < 1:
        parser.error("--sample must be positive")

    root = zarr.open_group(args.chimera, mode="r")
    controls = pv.FitControlsVinecop(
        family_set=pv.one_par, parametric_method="mle",
        selection_criterion="aic", num_threads=1, show_trace=False,
    )
    rows = []
    for variables, total in COUNTS.items():
        data = np.asfortranarray(np.loadtxt(HERE.parent / "data" / f"input{variables}_300_clayton_high.txt"))
        matrices = root[f"matrices{variables}"]
        if matrices.shape[0] != total:
            raise ValueError(f"Unexpected number of {variables}-variable matrices: {matrices.shape[0]}")
        count = total if variables <= 5 else min(args.sample, total)
        indices = range(total) if count == total else np.linspace(0, total - 1, count, dtype=int)
        elapsed = 0.0
        for index in indices:
            matrix = np.asfortranarray(matrices[int(index)], dtype=np.uint64)
            start = time.perf_counter()
            pv.Vinecop.from_data(data, matrix=matrix, controls=controls)
            elapsed += time.perf_counter() - start
        minutes = elapsed * total / count / 60
        rows.append((variables, len(data), total, f"{minutes:.6f}", count, "measured" if count == total else "extrapolated"))
        print(f"{variables} variables: {count}/{total} fits; {minutes:.2f} min ({rows[-1][-1]})", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("variables", "observations", "matrices", "estimated_total_minutes", "fits_timed", "method"))
        writer.writerows(rows)
    print(args.output)


if __name__ == "__main__":
    main()
