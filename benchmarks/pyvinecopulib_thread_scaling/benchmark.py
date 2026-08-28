#!/usr/bin/env python3
"""Benchmark pyvinecopulib threads for one fixed vine structure."""

from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path

import numpy as np
import pyvinecopulib as pv


HERE = Path(__file__).resolve().parent
DATA_FILE = HERE.parent / "data" / "input8_300_clayton_high.txt"
RAW_RESULTS_FILE = HERE / "results" / "thread_timings.csv"
SUMMARY_FILE = HERE / "results" / "thread_summary.csv"

COLUMNS = slice(0, 8)
THREADS = [1, 2, 4, 8, 16, 20, 24, 28, 32, 36, 40, 44, 48]
REPETITIONS = 7
RANDOM_SEED = 42


def make_controls(num_threads: int) -> pv.FitControlsVinecop:
    """Create identical fitting controls for every measurement."""
    return pv.FitControlsVinecop(
        family_set=pv.one_par,
        parametric_method="mle",
        selection_criterion="aic",
        num_threads=num_threads,
        show_trace=False,
    )


def write_results(
    measurements: list[dict[str, float | int]],
    elapsed: dict[int, list[float]],
) -> None:
    """Write raw measurements and median timings to CSV."""
    RAW_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RAW_RESULTS_FILE.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["run", "threads", "elapsed_ms"],
        )
        writer.writeheader()
        writer.writerows(measurements)

    with SUMMARY_FILE.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["threads", "median_time_ms"],
        )
        writer.writeheader()
        for threads in THREADS:
            writer.writerow(
                {
                    "threads": threads,
                    "median_time_ms": f"{statistics.median(elapsed[threads]) * 1000:.6f}",
                }
            )


def main() -> None:
    if not THREADS or any(threads < 1 for threads in THREADS):
        raise ValueError("THREADS must contain integers greater than or equal to 1")
    if REPETITIONS < 1:
        raise ValueError("REPETITIONS must be greater than or equal to 1")

    data = np.loadtxt(DATA_FILE, dtype=float, ndmin=2)
    if COLUMNS is not None:
        data = data[:, COLUMNS]
    data = np.asfortranarray(data)

    if not np.isfinite(data).all() or np.any((data <= 0.0) | (data >= 1.0)):
        raise ValueError("The data must be finite and strictly inside (0, 1)")

    print(f"pyvinecopulib: {pv.__version__}")
    print(f"Data: {DATA_FILE}")
    print(f"Observations: {data.shape[0]}; variables: {data.shape[1]}")
    print("Selecting a fixed structure (this step is not timed)...")

    initial_model = pv.Vinecop.from_data(data, controls=make_controls(1))
    matrix = np.asfortranarray(initial_model.matrix, dtype=np.uint64)

    execution_order = THREADS * REPETITIONS
    random.Random(RANDOM_SEED).shuffle(execution_order)
    elapsed = {threads: [] for threads in THREADS}
    measurements: list[dict[str, float | int]] = []

    for run_number, threads in enumerate(execution_order, start=1):
        start = time.perf_counter()
        pv.Vinecop.from_data(data, matrix=matrix, controls=make_controls(threads))
        duration = time.perf_counter() - start
        elapsed[threads].append(duration)
        measurements.append(
            {
                "run": run_number,
                "threads": threads,
                "elapsed_ms": round(duration * 1000, 6),
            }
        )
        print(
            f"Measurement {run_number:>2}/{len(execution_order)}: "
            f"{threads:>2} threads, {duration * 1000:>9.3f} ms"
        )

    write_results(measurements, elapsed)
    baseline = statistics.median(elapsed[1])
    print("\nResults (medians):")
    print("| Threads | Time per fit | Speedup |")
    print("|------:|---------------:|--------:|")
    for threads in THREADS:
        median = statistics.median(elapsed[threads])
        print(f"| {threads} | {median * 1000:.1f} ms | {baseline / median:.2f}x |")
    print(f"\nRaw results: {RAW_RESULTS_FILE}")
    print(f"Summary: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
