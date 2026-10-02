#!/usr/bin/env python3
"""Prepare an isolated run using deposited observations or newly simulated data."""

import argparse
import shutil
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE.parent / "original_execution"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--inputs", type=Path, help="Deposited simulations directory"
    )
    source.add_argument(
        "--new-data",
        action="store_true",
        help="Prepare for running simulate.py separately",
    )
    parser.add_argument(
        "--chimera",
        default="http://meteo.unican.es/work/chimera.zarr",
        help="Chimera Zarr URL or local directory (default: remote store)",
    )
    parser.add_argument("--partition", default="wncompute_meteo")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 100 or args.workers < 1:
        parser.error("Use 1–100 iterations and at least one worker")
    destination = args.destination.resolve()
    if destination.exists():
        parser.error("The destination must not exist; choose a new run directory")
    chimera = args.chimera
    if not chimera.startswith(("http://", "https://")):
        local_store = Path(chimera).resolve()
        if not local_store.is_dir():
            parser.error("--chimera must be an HTTP(S) URL or an existing local directory")
        chimera = str(local_store)
    if args.inputs:
        for i in range(1, args.iterations + 1):
            run = args.inputs / f"iteration_{i}"
            data = np.loadtxt(run / "vinecop_samples.txt", ndmin=2)
            if (
                data.shape != (300, 7)
                or not np.isfinite(data).all()
                or not ((data > 0) & (data < 1)).all()
            ):
                parser.error(f"Invalid observations in {run}")
            if not (run / "references.yaml").is_file():
                parser.error(f"Missing references.yaml in {run}")
    destination.mkdir(parents=True)
    for name in ("simulate.py", "select_best_vine.py", "vinecop_samples.txt"):
        shutil.copy2(SNAPSHOT / name, destination / name)
    config = yaml.safe_load((SNAPSHOT / "trasgu.yaml").read_text())
    config.pop("trasgu_url", None)
    config.update(chimera_url=chimera, max_workers=args.workers)
    (destination / "trasgu.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    profile = yaml.safe_load((SNAPSHOT / "slurm_profile.yaml").read_text())
    profile["default-resources"]["slurm_partition"] = args.partition
    (destination / "slurm_profile.yaml").write_text(
        yaml.safe_dump(profile, sort_keys=False)
    )
    (destination / "campaign.yaml").write_text(
        yaml.safe_dump({"iterations": args.iterations})
    )
    for name in ("Snakefile", "fit_references.py"):
        shutil.copy2(HERE / name, destination / name)
    shutil.copy2(
        HERE.parent / "analysis/build_aic_summaries.py",
        destination / "build_aic_summaries.py",
    )
    if args.inputs:
        for i in range(1, args.iterations + 1):
            run = destination / "simulations" / f"iteration_{i}"
            run.mkdir(parents=True)
            shutil.copy2(
                args.inputs / run.name / "vinecop_samples.txt",
                run / "vinecop_samples.txt",
            )
            shutil.copy2(
                args.inputs / run.name / "references.yaml",
                run / "references_original.yaml",
            )
            shutil.copy2(destination / "trasgu.yaml", run / "trasgu.yaml")
    print(destination)
    if args.new_data:
        print(
            f"Generate inputs first: python {destination / 'simulate.py'} {args.iterations}"
        )
    print(
        "Review slurm_profile.yaml before submitting jobs. Start with snakemake --cores 5 --dry-run."
    )


if __name__ == "__main__":
    main()
