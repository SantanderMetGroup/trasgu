#!/usr/bin/env python3
"""Prepare a new ship-wake run from an authorized copy of the source data."""

import argparse
import shutil
from pathlib import Path

import yaml

from prepare_data import prepare

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--chimera", default="http://meteo.unican.es/work/chimera.zarr")
    parser.add_argument("--partition", default="wncompute_ifca")
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists() or not args.data.is_file() or args.workers < 1:
        parser.error("Use a new destination, an existing data file and positive workers")
    chimera = args.chimera
    if not chimera.startswith(("http://", "https://")):
        local = Path(chimera).resolve()
        if not local.is_dir():
            parser.error("--chimera must be an HTTP(S) URL or a local Zarr directory")
        chimera = str(local)
    original = HERE.parent / "original_execution"
    config = yaml.safe_load((original / "trasgu.yaml").read_text())
    config.update(data_file="unity_inbound.txt", chimera_url=chimera, max_workers=args.workers)
    profile = yaml.safe_load((original / "slurm_profile.yaml").read_text())
    profile["default-resources"]["slurm_partition"] = args.partition
    destination.mkdir(parents=True)
    prepare(args.data, destination / "unity_inbound.txt")
    (destination / "trasgu.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    (destination / "slurm_profile.yaml").write_text(yaml.safe_dump(profile, sort_keys=False))
    shutil.copy2(HERE / "dissmann.py", destination / "dissmann.py")
    print(f"Prepared {destination}. Review slurm_profile.yaml before submitting jobs.")


if __name__ == "__main__":
    main()
