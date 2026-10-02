"""Validate all ESREL fits and summarize scientific comparisons."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import yaml

from model import N_MATRICES

# Trasgu stores AIC with six decimal places. Allow rounding and small numeric noise.
AIC_TOLERANCE = 1e-5


def load_fits(path, id_column, aic_column):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    ids = [int(row[id_column]) for row in rows]
    if len(ids) != N_MATRICES or set(ids) != set(range(N_MATRICES)):
        raise ValueError(f"{path}: expected each matrix ID 0..479 exactly once")
    values = np.empty(N_MATRICES)
    for matrix_id, row in zip(ids, rows):
        values[matrix_id] = float(row[aic_column])
    if not np.isfinite(values).all():
        raise ValueError(f"{path}: non-finite AIC")
    return values


def compare_fits(canonical, manual, mapping):
    aligned = manual[np.asarray(mapping)]
    delta = np.abs(canonical - aligned)
    if np.max(delta) > AIC_TOLERANCE:
        i = int(np.argmax(delta))
        raise ValueError(
            f"AIC mismatch for Chimera matrix {i}: {delta[i]:.9g} "
            f"exceeds tolerance {AIC_TOLERANCE}"
        )
    return float(np.max(delta))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--iterations", type=int, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.run / "assets" / "manifest.json").read_text())
    mapping = manifest["canonical_to_manual"]
    if sorted(mapping) != list(range(N_MATRICES)):
        raise ValueError("Invalid matrix mapping")
    rows = []
    for iteration in range(1, args.iterations + 1):
        directory = args.run / "simulations" / f"iteration_{iteration}"
        fitted = load_fits(
            directory / f"fit_iteration_{iteration}.csv", "vine_id", "aic"
        )
        manual = load_fits(
            directory / f"manual_fits_{iteration}.csv", "manual_vine_id", "manual_aic"
        )
        error = compare_fits(fitted, manual, mapping)
        references = yaml.safe_load(
            (directory / f"reference_fits_{iteration}.yaml").read_text()
        )
        ref_aics = {
            key: float(references[key])
            for key in ("aic_dissmann", "aic_fixed_matrix_clayton", "aic_ground_truth")
        }
        if not all(np.isfinite(list(ref_aics.values()))):
            raise ValueError(f"Non-finite reference AIC in iteration {iteration}")
        best_id, manual_id = int(np.argmin(fitted)), int(np.argmin(manual))
        rows.append(
            {
                "iteration": iteration,
                "vine_id": best_id,
                "aic_vine": fitted[best_id],
                "manual_vine_id": manual_id,
                "manual_aic": manual[manual_id],
                **ref_aics,
                "max_matrix_aic_error": error,
                "delta_aic_dissmann": fitted[best_id] - ref_aics["aic_dissmann"],
                "delta_aic_fixed_clayton": fitted[best_id]
                - ref_aics["aic_fixed_matrix_clayton"],
                "generating_matrix_selected": abs(
                    fitted[manifest["generating_matrix_id"]] - fitted[best_id]
                )
                <= AIC_TOLERANCE,
            }
        )
    out = args.run / "results"
    out.mkdir(exist_ok=True)
    with (out / "aic_comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    differences = np.array([r["delta_aic_dissmann"] for r in rows])
    summary = {
        "iterations": len(rows),
        "matrices_per_iteration": N_MATRICES,
        "matrix_comparisons": len(rows) * N_MATRICES,
        "aic_tolerance": AIC_TOLERANCE,
        "max_matrix_aic_error": max(r["max_matrix_aic_error"] for r in rows),
        "all_manual_comparisons_passed": True,
        "generating_matrix_id": manifest["generating_matrix_id"],
        "generating_matrix_selected_including_ties": sum(
            int(r["generating_matrix_selected"]) for r in rows
        ),
        "distinct_selected_matrices": len(set(r["vine_id"] for r in rows)),
        "exhaustive_better_than_dissmann": int(np.sum(differences < -AIC_TOLERANCE)),
        "exhaustive_tied_with_dissmann": int(
            np.sum(np.abs(differences) <= AIC_TOLERANCE)
        ),
        "exhaustive_worse_than_dissmann": int(np.sum(differences > AIC_TOLERANCE)),
        "delta_aic_dissmann_min_median_max": [
            float(np.min(differences)),
            float(np.median(differences)),
            float(np.max(differences)),
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
