#!/usr/bin/env python3
"""Build and verify the Zenodo archives for the Trasgu experiments."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import shutil
import tarfile
import tempfile
import subprocess
import sys
from pathlib import Path

EXPECTED_SHIP_CHUNK_SHA256 = (
    "c6acbf1db281905e186701f64616c00aad1c6b00dfc44d18aa72e7d3d4703d60"
)
FORBIDDEN_SHIP_NAMES = {
    "UI-1_ship_and_wake_data_for_TUDelft.csv",
    "unity_inbound.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Required file not found: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def write_checksums(root: Path) -> None:
    checksum_file = root / "metadata" / "SHA256SUMS"
    checksum_file.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path for path in root.rglob("*") if path.is_file() and path != checksum_file
    )
    with checksum_file.open("w", encoding="utf-8", newline="\n") as stream:
        for path in files:
            stream.write(f"{sha256(path)}  {path.relative_to(root).as_posix()}\n")


def verify_checksums(root: Path) -> None:
    checksum_file = root / "metadata" / "SHA256SUMS"
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = root / relative
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Checksum mismatch for {path}: {actual} != {expected}")


def verify_ship_exclusions(root: Path) -> None:
    included_names = {path.name for path in root.rglob("*") if path.is_file()}
    forbidden = sorted(included_names & FORBIDDEN_SHIP_NAMES)
    if forbidden:
        raise RuntimeError(
            "Ship-wake package contains excluded source data: " + ", ".join(forbidden)
        )


def make_archive(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with (
        destination.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed,
        tarfile.open(fileobj=compressed, mode="w") as archive,
    ):
        for path in [source, *sorted(source.rglob("*"))]:
            relative = path.relative_to(source.parent)
            info = archive.gettarinfo(str(path), arcname=relative.as_posix())
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            if path.is_file():
                with path.open("rb") as stream:
                    archive.addfile(info, stream)
            else:
                archive.addfile(info)


def validate_ship_source(source: Path) -> None:
    required = (
        "README.md", "LICENSE", "MANIFEST.txt", "workflow/prepare_run.py",
        "original_execution/Snakefile", "original_execution/trasgu.yaml",
        "original_execution/slurm_profile.yaml", "analysis/plot_large_aic_cdf.py",
        "results/best_fits.txt", "results/processed_aic_cdf.npz",
        "figures/large_aic_cdf.pdf", "figures/large_aic_cdf.png",
        "styles/trasgu.mplstyle", "metadata/chunk_manifest.csv",
        "metadata/execution_environment.txt", "metadata/software_revision.txt",
        "logs/final_combination.log",
    )
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise RuntimeError("Ship-wake staging is incomplete: " + ", ".join(missing))
    verify_ship_exclusions(source)
    digest = hashlib.sha256()
    count = 0
    with gzip.open(source / "raw_results/fit_chunk_0067_4000000.csv.gz", "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            count += block.count(b"\n")
    if digest.hexdigest() != EXPECTED_SHIP_CHUNK_SHA256 or count != 4_000_000:
        raise RuntimeError("Ship-wake raw chunk differs from the deposited original")
    with (source / "metadata/chunk_manifest.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    if [row["chunk_id"] for row in rows] != [f"{i:04d}" for i in range(166)]:
        raise RuntimeError("Expected manifest entries for all 166 chunks")
    for row in rows:
        log = source / "logs/successful_chunks" / f"chunk_{row['chunk_id']}.log"
        content = log.read_text()
        if "Results saved to" not in content and "1 of 1 steps (100%) done" not in content:
            raise RuntimeError(f"No completion marker in {log}")
        for job in filter(None, row["other_attempt_job_ids"].split(";")):
            if not (source / "logs/failed_chunk_attempts" / row["chunk_id"] / f"{job}.log").is_file():
                raise RuntimeError(f"Missing archived attempt {job}")
    print("Verified ship-wake chunk and execution logs for all 166 chunks.")


def validate_clayton_source(source: Path) -> None:
    required = (
        "README.md", "LICENSE", "MANIFEST.txt",
        "metadata/software_revision.txt", "metadata/execution_commands.txt",
        "metadata/execution_environment.txt", "metadata/package_provenance.txt",
        "original_execution", "workflow", "analysis", "figures",
        "styles/trasgu.mplstyle", "results/aic_comparison.csv",
        "simulations/iteration_99/fit_iteration_99.csv",
    )
    missing = [name for name in required if not (source / name).exists()]
    if missing:
        raise RuntimeError("Clayton staging is incomplete: " + ", ".join(missing))
    verifier = Path(__file__).resolve().parents[1] / "clayton_7d/analysis/verify_data.py"
    subprocess.run([sys.executable, str(verifier), str(source)], check=True)


def build_package(source: Path, staging: Path, name: str) -> Path:
    """Package the reviewed files without regenerating scientific outputs."""
    package = staging / name
    # Keep the reviewed directory untouched; checksums belong to the archive copy.
    shutil.copytree(source, package)
    write_checksums(package)
    verify_checksums(package)
    return package


def write_outer_manifest(output: Path) -> None:
    files = sorted(
        path
        for path in output.iterdir()
        if path.is_file() and path.name not in {"MANIFEST.csv", "SHA256SUMS"}
    )
    with (output / "MANIFEST.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("filename", "size_bytes", "sha256"))
        for path in files:
            writer.writerow((path.name, path.stat().st_size, sha256(path)))
    checksummed = sorted(
        path
        for path in output.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    with (output / "SHA256SUMS").open("w", encoding="utf-8", newline="\n") as stream:
        for path in checksummed:
            stream.write(f"{sha256(path)}  {path.name}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "dist",
        help="directory that will contain the files uploaded to Zenodo",
    )
    parser.add_argument(
        "--clayton-staging",
        type=Path,
        default=Path(__file__).resolve().parent / "staging/clayton_7d",
        help="reviewed Clayton package directory",
    )
    parser.add_argument(
        "--ship-staging",
        type=Path,
        default=Path(__file__).resolve().parent / "staging/ship_wake",
        help="reviewed ship-wake package directory",
    )
    parser.add_argument(
        "--verify-only", action="store_true",
        help="check both staging directories without creating archives",
    )
    args = parser.parse_args()

    validate_clayton_source(args.clayton_staging.resolve())
    validate_ship_source(args.ship_staging.resolve())
    if args.verify_only:
        print("Both staging directories verified; no files generated.")
        return
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    common = Path(__file__).resolve().parent
    for name in (
        "README.md",
        "CITATION.cff",
        "LICENSE",
        "RIGHTS.md",
        "THIRD_PARTY_NOTICES.md",
    ):
        copy_file(common / name, output / name)

    with tempfile.TemporaryDirectory(prefix="trasgu-zenodo-") as temporary:
        staging = Path(temporary)
        packages = [
            build_package(args.clayton_staging.resolve(), staging, "clayton_7d-softwarex-v2"),
            build_package(args.ship_staging.resolve(), staging, "ship_wake-softwarex-v2"),
        ]
        for package in packages:
            make_archive(package, output / f"{package.name}.tar.gz")

    write_outer_manifest(output)
    print(f"Zenodo upload directory created: {output}")
    for path in sorted(output.iterdir()):
        print(f"  {path.name}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
