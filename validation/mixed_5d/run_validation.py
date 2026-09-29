"""Run the reproducible mixed-family validation locally through Snakemake."""

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))


def command_output(command):
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=HERE / "runs" / "default")
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--observations", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--cores", type=int, default=4)
    parser.add_argument(
        "--chimera-url", default="http://meteo.unican.es/work/chimera.zarr"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--unlock",
        action="store_true",
        help="Unlock only after confirming no workflow is running",
    )
    args = parser.parse_args()
    if args.iterations < 1 or args.observations < 2 or args.seed < 0 or args.cores < 1:
        parser.error("iterations and cores must be >= 1, observations >= 2, seed >= 0")
    run = args.run_dir.resolve()
    if run == HERE or run == HERE / "results":
        parser.error(
            "Choose a separate run directory, such as validation/mixed_5d/runs/default"
        )
    run.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["MPLCONFIGDIR"] = str(run / ".cache" / "matplotlib")
    env["XDG_CACHE_HOME"] = str(run / ".cache")
    # Avoid hidden numerical-library thread pools within the outer job budget.
    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        env[name] = "1"
    os.environ.setdefault("MPLCONFIGDIR", env["MPLCONFIGDIR"])
    from validation.mixed_5d.scripts.model import MODEL_DESCRIPTION

    config = {
        key: getattr(args, key)
        for key in ("iterations", "observations", "seed", "chimera_url")
    }
    packages = {
        p: metadata.version(p)
        for p in (
            "trasgu",
            "pyvinecopulib",
            "snakemake",
            "numpy",
            "zarr",
            "PyYAML",
            "matplotlib",
        )
    }
    sources = (
        sorted(HERE.glob("*.py"))
        + [HERE / "Snakefile", HERE / "config" / "trasgu.yaml"]
        + sorted((HERE / "scripts").rglob("*.py"))
        + sorted((HERE.parent / "_shared").glob("*.py"))
        + [ROOT / "styles" / "trasgu.mplstyle"]
        + sorted((ROOT / "src" / "trasgu").rglob("*.py"))
        + [ROOT / "src" / "trasgu" / "workflow" / "Snakefile"]
    )
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sources
    }
    identity = {"config": config, "packages": packages, "source_sha256": hashes}
    provenance_path = run / "provenance.json"
    if provenance_path.exists():
        saved = json.loads(provenance_path.read_text())
        if any(saved[key] != value for key, value in identity.items()):
            parser.error(
                "This directory belongs to a different configuration, code or environment. Use a new --run-dir."
            )
    elif not args.dry_run and not args.unlock:
        provenance = {
            **identity,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(),
            "python": sys.version,
            "available_cpus": os.cpu_count(),
            "git_commit": command_output(["git", "rev-parse", "HEAD"]),
            "git_status": command_output(["git", "status", "--short"]),
            "generating_model": MODEL_DESCRIPTION,
            "command": sys.argv,
        }
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
        (run / "environment.txt").write_text(
            command_output([sys.executable, "-m", "pip", "freeze"])
            or "\n".join(
                f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions()
            )
        )
    command = [
        sys.executable,
        "-m",
        "snakemake",
        "--snakefile",
        str(HERE / "Snakefile"),
        "--directory",
        str(run),
        "--cores",
        str(args.cores),
        "--rerun-incomplete",
        "--printshellcmds",
        "--config",
        f"run_dir={run}",
        *[f"{key}={value}" for key, value in config.items()],
    ]
    if args.dry_run:
        command.append("--dry-run")
    if args.unlock:
        command.append("--unlock")
    started = time.monotonic()
    start_utc = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, env=env)
    if not args.dry_run and not args.unlock:
        with (run / "attempts.jsonl").open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        "started_utc": start_utc,
                        "wall_seconds": time.monotonic() - started,
                        "cores": args.cores,
                        "returncode": result.returncode,
                    }
                )
                + "\n"
            )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
