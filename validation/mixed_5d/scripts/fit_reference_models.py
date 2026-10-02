"""Fit Dissmann and refit the specified mixed-family generating vine."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import time

import numpy as np
import pyvinecopulib as pv
import yaml

from validation.mixed_5d.scripts.model import generating_model


def fit_references(data):
    data = np.asfortranarray(data, dtype=float)
    if data.ndim != 2 or data.shape[1] != 5 or not np.isfinite(data).all():
        raise ValueError("Expected a finite observations-by-five matrix")
    if np.any((data <= 0) | (data >= 1)):
        raise ValueError("Observations must lie strictly between zero and one")
    selected = pv.Vinecop.from_data(
        data,
        controls=pv.FitControlsVinecop(
            family_set=pv.one_par,
            tree_criterion="tau",
            selection_criterion="aic",
            parametric_method="mle",
            num_threads=1,
            show_trace=False,
        ),
    )
    fixed = generating_model()
    ground_truth_aic = float(fixed.aic(data))
    # fit(), unlike from_data()/select(), retains each edge's family and rotation.
    fixed.fit(
        data, controls=pv.FitControlsBicop(parametric_method="mle"), num_threads=1
    )
    return {
        "aic_dissmann": float(selected.aic()),
        # ESREL-compatible field name; the reference is the MIXED generating vine.
        "aic_fixed_matrix_clayton": float(fixed.aic()),
        "aic_ground_truth": ground_truth_aic,
        "matrix": selected.matrix.tolist(),
        "fixed_reference": {
            "description": "Generating structure and mixed Clayton/Gaussian families retained; parameters refitted",
            "matrix": fixed.matrix.tolist(),
            "families": [
                [str(c.family).split(".")[-1] for c in tree]
                for tree in fixed.pair_copulas
            ],
            "rotations": [[c.rotation for c in tree] for tree in fixed.pair_copulas],
            "parameters": [
                [c.parameters.tolist() for c in tree] for tree in fixed.pair_copulas
            ],
        },
    }


def fit_file(paths):
    source, output = map(Path, paths)
    result = fit_references(np.loadtxt(source, ndmin=2))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(result, sort_keys=False))
    return hashlib.sha256(source.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument(
        "--run", type=Path, help="Add references to all datasets of an existing run"
    )
    parser.add_argument("--cores", type=int, default=4)
    args = parser.parse_args()
    if args.cores < 1:
        parser.error("cores must be positive")
    if not args.run:
        if not args.input or not args.output:
            parser.error("Provide input and output, or --run")
        fit_file((args.input, args.output))
        return
    if args.input or args.output:
        parser.error("Use either input/output or --run")
    provenance = json.loads((args.run / "provenance.json").read_text())
    jobs, checksums = [], {}
    for iteration in range(1, provenance["config"]["iterations"] + 1):
        directory = args.run / "simulations" / f"iteration_{iteration}"
        source = directory / "vinecop_samples.txt"
        simulation = json.loads((directory / "simulation.json").read_text())
        checksum = hashlib.sha256(source.read_bytes()).hexdigest()
        if (
            simulation["iteration"] != iteration
            or simulation["data_sha256"] != checksum
        ):
            raise ValueError(f"Changed input in iteration {iteration}")
        checksums[str(iteration)] = checksum
        jobs.append((source, directory / f"reference_fits_{iteration}.yaml"))
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.cores) as executor:
        list(executor.map(fit_file, jobs))
    source_files = [Path(__file__), Path(__file__).with_name("model.py")]
    record = {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "iterations": len(jobs),
        "cores": args.cores,
        "wall_seconds": time.monotonic() - started,
        "pyvinecopulib": metadata.version("pyvinecopulib"),
        "data_sha256_by_iteration": checksums,
        "source_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files
        },
        "fixed_reference": "Mixed generating matrix, per-edge families and rotations retained; parameters refitted",
    }
    (args.run / "reference_analysis.json").write_text(
        json.dumps(record, indent=2) + "\n"
    )
    print(f"Added reference fits for {len(jobs)} simulations")


if __name__ == "__main__":
    main()
