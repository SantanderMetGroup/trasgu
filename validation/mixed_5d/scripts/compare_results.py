"""Validate every Trasgu AIC against sequential fitting of original matrices."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import yaml

from validation._shared.comparison import (
    AIC_TOLERANCE,
    N_MATRICES,
    compare_fits,
    load_fits,
)


def compare_iteration(directory, iteration, mapping):
    fitted = load_fits(directory / f"fit_iteration_{iteration}.csv", "vine_id", "aic")
    manual = load_fits(
        directory / f"manual_fits_{iteration}.csv", "manual_vine_id", "manual_aic"
    )
    maximum_error = compare_fits(fitted, manual, mapping)
    aligned = manual[np.asarray(mapping)]
    best = int(np.argmin(fitted))
    manual_best = int(np.argmin(aligned))
    # Each selected structure must be optimal within tolerance in the other fit.
    winners_agree = bool(
        fitted[manual_best] - fitted[best] <= AIC_TOLERANCE
        and aligned[best] - aligned[manual_best] <= AIC_TOLERANCE
    )
    if not winners_agree:
        raise ValueError(
            f"Iteration {iteration}: selected structures disagree beyond tolerance"
        )
    return {
        "iteration": iteration,
        "trasgu_vine_id": best,
        "manual_vine_id": int(mapping[manual_best]),
        "manual_best_chimera_id": manual_best,
        "aic_trasgu": float(fitted[best]),
        "aic_manual": float(aligned[manual_best]),
        "best_aic_difference": float(fitted[best] - aligned[manual_best]),
        "max_matrix_aic_error": maximum_error,
        "mean_matrix_aic_error": float(np.mean(np.abs(fitted - aligned))),
        "same_selected_structure": best == manual_best,
        "best_fit_agrees_within_tolerance": winners_agree,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--iterations", type=int, required=True)
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be positive")
    manifest = json.loads((args.run / "assets/manifest.json").read_text())
    mapping = manifest["canonical_to_manual"]
    if sorted(mapping) != list(range(N_MATRICES)):
        raise ValueError("Invalid matrix mapping")
    rows = []
    table_rows = []
    for iteration in range(1, args.iterations + 1):
        directory = args.run / "simulations" / f"iteration_{iteration}"
        metadata = json.loads((directory / "simulation.json").read_text())
        data_hash = hashlib.sha256(
            (directory / "vinecop_samples.txt").read_bytes()
        ).hexdigest()
        if metadata["iteration"] != iteration or metadata["data_sha256"] != data_hash:
            raise ValueError(
                f"Iteration {iteration}: input does not match simulation metadata"
            )
        row = compare_iteration(directory, iteration, mapping)
        rows.append(row)
        references = yaml.safe_load(
            (directory / f"reference_fits_{iteration}.yaml").read_text()
        )
        ref = {
            key: float(references[key])
            for key in ("aic_dissmann", "aic_fixed_matrix_clayton", "aic_ground_truth")
        }
        if not np.isfinite(list(ref.values())).all():
            raise ValueError(f"Iteration {iteration}: non-finite reference AIC")
        fitted = load_fits(
            directory / f"fit_iteration_{iteration}.csv", "vine_id", "aic"
        )
        table_rows.append(
            {
                "iteration": iteration,
                "vine_id": row["trasgu_vine_id"],
                "aic_vine": row["aic_trasgu"],
                "manual_vine_id": row["manual_vine_id"],
                "manual_aic": row["aic_manual"],
                **ref,
                "max_matrix_aic_error": row["max_matrix_aic_error"],
                "delta_aic_dissmann": row["aic_trasgu"] - ref["aic_dissmann"],
                "delta_aic_fixed_clayton": row["aic_trasgu"]
                - ref["aic_fixed_matrix_clayton"],
                "generating_matrix_selected": bool(
                    abs(fitted[manifest["generating_matrix_id"]] - row["aic_trasgu"])
                    <= AIC_TOLERANCE
                ),
            }
        )
    summary = {
        "iterations": len(rows),
        "matrices_per_iteration": N_MATRICES,
        "matrix_comparisons": len(rows) * N_MATRICES,
        "aic_tolerance": AIC_TOLERANCE,
        "max_matrix_aic_error": max(r["max_matrix_aic_error"] for r in rows),
        "max_best_aic_error": max(abs(r["best_aic_difference"]) for r in rows),
        "all_matrix_comparisons_passed": True,
        "all_input_checksums_passed": True,
        "identical_selected_structures": sum(
            r["same_selected_structure"] for r in rows
        ),
        "best_fits_agree_including_ties": sum(
            r["best_fit_agrees_within_tolerance"] for r in rows
        ),
    }
    differences = np.array([r["delta_aic_dissmann"] for r in table_rows])
    summary.update(
        {
            "generating_matrix_id": manifest["generating_matrix_id"],
            "generating_matrix_selected_including_ties": sum(
                r["generating_matrix_selected"] for r in table_rows
            ),
            "distinct_selected_matrices": len({r["vine_id"] for r in table_rows}),
            "exhaustive_better_than_dissmann": int(
                np.sum(differences < -AIC_TOLERANCE)
            ),
            "exhaustive_tied_with_dissmann": int(
                np.sum(np.abs(differences) <= AIC_TOLERANCE)
            ),
            "exhaustive_worse_than_dissmann": int(np.sum(differences > AIC_TOLERANCE)),
            "delta_aic_dissmann_min_median_max": [
                float(np.min(differences)),
                float(np.median(differences)),
                float(np.max(differences)),
            ],
            "fixed_reference": "Mixed Clayton/Gaussian generating vine with refitted parameters; ESREL-compatible column names",
        }
    )
    output = args.run / "results"
    output.mkdir(exist_ok=True)
    with (output / "aic_comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(table_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(table_rows)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
