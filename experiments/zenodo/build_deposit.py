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
from pathlib import Path

VERSION = "v1"
EXPECTED_SHIP_CHUNK_SHA256 = (
    "c6acbf1db281905e186701f64616c00aad1c6b00dfc44d18aa72e7d3d4703d60"
)
EXCLUDED_NAMES = {
    ".DS_Store",
    ".ruff_cache",
    ".snakemake",
    "__pycache__",
    "fontlist-v3.11.0.json",
}
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


def copy_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Required directory not found: {source}")
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(*EXCLUDED_NAMES),
        dirs_exist_ok=True,
    )


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


def successful_log(logs: list[Path]) -> Path | None:
    successes = []
    for path in logs:
        contents = path.read_text(encoding="utf-8", errors="replace")
        saved_result = "Results saved to" in contents
        completed_job = "1 of 1 steps (100%) done" in contents
        failed_job = any(
            marker in contents
            for marker in (
                "command exited with non-zero exit code",
                "WorkflowError:",
                "CANCELLED",
            )
        )
        if (saved_result or completed_job) and not failed_job:
            successes.append(path)
    return max(successes, key=lambda path: int(path.stem)) if successes else None


def validate_ship_source(repo: Path) -> None:
    experiment = repo / "experiments" / "ship_wake"
    common = repo / "experiments" / "zenodo"
    required_files = (
        experiment / "zenodo" / "DATASET_README.md",
        experiment / "zenodo" / "RAW_CHUNK_README.md",
        experiment / "zenodo" / "execution_environment.txt",
        experiment / "zenodo" / "software_revision.txt",
        experiment / "PrepareData.py",
        experiment / "dissmann.py",
        experiment / "plot_large_aic_cdf.py",
        experiment / "processed_aic_cdf.npz",
        experiment / "results" / "best_fits.txt",
        experiment / "results" / "large_aic_cdf.pdf",
        experiment / "results" / "large_aic_cdf.png",
        experiment / ".trasgu_ship_wake" / "fit_chunk_0067_4000000.csv",
        repo / "styles" / "trasgu.mplstyle",
        common / "LICENSE",
        common / "RIGHTS.md",
        common / "THIRD_PARTY_NOTICES.md",
    )
    required_directories = (
        experiment / "execution_snapshot",
        experiment / ".snakemake" / "slurm_logs" / "rule_fit_chunk",
        experiment / ".snakemake" / "log",
    )
    missing = [path for path in required_files if not path.is_file()]
    missing.extend(path for path in required_directories if not path.is_dir())
    if missing:
        details = "\n  ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Ship-wake package source is incomplete:\n  {details}")


def validate_clayton_source(source: Path) -> None:
    required = (
        "README.md",
        "metadata",
        "workflow_snapshots",
        "runs_by_sample_size",
        "repeated_300/summary",
        "sample_size_scaling/summary",
        "sample_size_scaling/timing_logs",
        "representative_full_fits/iteration_99_300",
        "representative_full_fits/iteration_1_3000",
    )
    missing = [name for name in required if not (source / name).exists()]
    if missing:
        raise RuntimeError(
            "Clayton package source is incomplete; missing: " + ", ".join(missing)
        )


def build_ship_wake(repo: Path, staging: Path) -> Path:
    experiment = repo / "experiments" / "ship_wake"
    common = repo / "experiments" / "zenodo"
    package = staging / f"ship_wake-softwarex-{VERSION}"

    copy_file(experiment / "zenodo" / "DATASET_README.md", package / "README.md")
    copy_file(common / "LICENSE", package / "LICENSE")
    copy_file(common / "RIGHTS.md", package / "RIGHTS.md")
    copy_file(common / "THIRD_PARTY_NOTICES.md", package / "THIRD_PARTY_NOTICES.md")
    for name in ("PrepareData.py", "dissmann.py"):
        copy_file(experiment / name, package / "code" / name)
    copy_tree(experiment / "execution_snapshot", package / "workflow_snapshot")
    copy_file(
        experiment / "results" / "best_fits.txt",
        package / "results" / "best_fits.txt",
    )
    copy_file(
        experiment / "plot_large_aic_cdf.py",
        package / "analysis" / "plot_large_aic_cdf.py",
    )
    copy_file(
        experiment / "processed_aic_cdf.npz",
        package / "analysis" / "processed_aic_cdf.npz",
    )
    copy_file(
        repo / "styles" / "trasgu.mplstyle",
        package / "analysis" / "styles" / "trasgu.mplstyle",
    )
    for suffix in ("pdf", "png"):
        copy_file(
            experiment / "results" / f"large_aic_cdf.{suffix}",
            package / "analysis" / "results" / f"large_aic_cdf.{suffix}",
        )
    for name in ("execution_environment.txt", "software_revision.txt"):
        copy_file(experiment / "zenodo" / name, package / "metadata" / name)

    raw_chunk = experiment / ".trasgu_ship_wake" / "fit_chunk_0067_4000000.csv"
    if sha256(raw_chunk) != EXPECTED_SHIP_CHUNK_SHA256:
        raise RuntimeError(f"Unexpected representative chunk contents: {raw_chunk}")
    if sum(1 for _ in raw_chunk.open("rb")) != 4_000_000:
        raise RuntimeError(f"Representative chunk does not have 4,000,000 rows: {raw_chunk}")
    compressed_chunk = package / "raw_results" / f"{raw_chunk.name}.gz"
    compressed_chunk.parent.mkdir(parents=True, exist_ok=True)
    with (
        raw_chunk.open("rb") as source,
        compressed_chunk.open("wb") as target,
        gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as output,
    ):
        shutil.copyfileobj(source, output)
    copy_file(
        experiment / "zenodo" / "RAW_CHUNK_README.md",
        package / "raw_results" / "README.md",
    )

    log_root = experiment / ".snakemake" / "slurm_logs" / "rule_fit_chunk"
    chunk_rows: list[tuple[str, str, str]] = []
    for chunk_number in range(166):
        chunk = f"{chunk_number:04d}"
        logs = sorted((log_root / chunk).glob("*.log"))
        success = successful_log(logs)
        if success is None:
            raise RuntimeError(f"No successful SLURM log found for chunk {chunk}")
        copy_file(success, package / "logs" / "successful_chunks" / f"chunk_{chunk}.log")
        failures = [path for path in logs if path != success]
        for failure in failures:
            copy_file(
                failure,
                package / "logs" / "failed_chunk_attempts" / chunk / failure.name,
            )
        chunk_rows.append((chunk, success.stem, ";".join(path.stem for path in failures)))

    manifest = package / "metadata" / "chunk_manifest.csv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("chunk_id", "successful_slurm_job_id", "other_attempt_job_ids"))
        writer.writerows(chunk_rows)

    workflow_logs = sorted((experiment / ".snakemake" / "log").glob("*.log"))
    final_logs = [
        path
        for path in workflow_logs
        if "2 of 2 steps (100%) done"
        in path.read_text(encoding="utf-8", errors="replace")
    ]
    if not final_logs:
        raise RuntimeError("Final successful Snakemake combination log not found")
    final_log = max(final_logs)
    copy_file(final_log, package / "logs" / "final_combination.log")
    for log in workflow_logs:
        if log != final_log:
            copy_file(log, package / "logs" / "workflow_attempts" / log.name)

    verify_ship_exclusions(package)
    write_checksums(package)
    verify_checksums(package)
    return package


def build_clayton(source: Path, staging: Path) -> Path:
    validate_clayton_source(source)
    package = staging / f"clayton_7d-softwarex-{VERSION}"
    copy_tree(source, package)
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
    checksummed = sorted(path for path in output.iterdir() if path.is_file() and path.name != "SHA256SUMS")
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
        "--clayton-source",
        type=Path,
        help="prepared Clayton package root; omit to build only ship_wake",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    validate_ship_source(repo)
    if args.clayton_source:
        validate_clayton_source(args.clayton_source.resolve())
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    common = repo / "experiments" / "zenodo"
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
        packages = [build_ship_wake(repo, staging)]
        if args.clayton_source:
            packages.append(build_clayton(args.clayton_source.resolve(), staging))
        for package in packages:
            make_archive(package, output / f"{package.name}.tar.gz")

    write_outer_manifest(output)
    print(f"Zenodo upload directory created: {output}")
    for path in sorted(output.iterdir()):
        print(f"  {path.name}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
