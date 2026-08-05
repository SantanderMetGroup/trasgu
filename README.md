# trasgu

`trasgu` is a CLI-first toolkit for fitting vine copulas over structured [Chimera](https://research.tudelft.nl/en/datasets/chimera-a-database-with-regular-vine-matrices-on-4-to-8-nodes/) Zarr matrices. It splits large Chimera matrix collections into chunks, fits each chunk independently, monitors progress, and combines the results into CSV output.

It supports local execution through Snakemake and HPC execution through SLURM profiles.

## Installation

Install the latest published release as a command-line tool:

```bash
uv tool install trasgu
```

Trasgu is a standard Python package, so installation with `pip` is also
supported:

```bash
python -m pip install trasgu
```

To use the locked environment from a source checkout:

```bash
git clone https://github.com/SantanderMetGroup/trasgu.git
cd trasgu
uv sync --frozen --no-dev
```

### GitHub Codespaces

You can try `trasgu` in GitHub Codespaces without installing Python or `uv` locally.

1. Open the repository on GitHub.
2. Click **Code** -> **Codespaces** -> **Create codespace on main**.
3. Wait for the Dev Container setup to finish. It installs `uv` and syncs the locked runtime environment automatically.
4. Run the minimal example:

```bash
trasgu_examples minimal ./minimal
cd minimal
trasgu_run --dry-run
```

The Codespace terminal already uses the project `.venv`, so `trasgu` commands should work without activating the environment manually.

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

For SLURM execution, install the optional SLURM extra:

```bash
uv sync --frozen --extra slurm
```

## Quickstart

```bash
trasgu_examples minimal ./minimal
cd minimal
trasgu_count_chunks
trasgu_run --dry-run
trasgu_run
trasgu_monitor
trasgu_combine
```

The run writes chunk CSV files to `.trasgu_minimal/` and combines them into `fit_minimal.csv` next to `trasgu.yaml`.

You can also run commands without activating the environment:

```bash
trasgu_examples minimal ./minimal
cd minimal
uv run --project .. --frozen trasgu_run --dry-run
```

## Configuration

Each run directory contains a `trasgu.yaml` file. Relative paths in `trasgu.yaml` are resolved from the run directory.

Minimal example:

```yaml
data_file: input6_500_gumbel_high.txt
chunk_size: 1000
```

## CLI commands

- `trasgu_run`: run the packaged Snakemake workflow.
- `trasgu_count_chunks`: print the number of chunks.
- `trasgu_time_fit`: estimate time per configured chunk.
- `trasgu_monitor`: show chunk completion status.
- `trasgu_combine`: combine chunk CSV files.
- `trasgu_best_fits`: print or export the lowest-AIC fitted models.
- `trasgu_fit_chunk`: manually fit one chunk.
- `trasgu_get_matrix`: print one Chimera matrix.
- `trasgu_download_zarr`: download Chimera Zarr arrays for offline execution.
- `trasgu_examples`: copy packaged examples to a local working directory.

All commands support `--help`.

## Documentation

The documentation source lives in `docs/` and is configured by `mkdocs.yml`.

Build locally:

```bash
uvx --with mkdocs-material mkdocs build --strict
```

Serve locally:

```bash
uvx --with mkdocs-material mkdocs serve
```

Start with:

- [Getting started](https://santandermetgroup.github.io/trasgu/getting-started/)
- [Run configuration](https://santandermetgroup.github.io/trasgu/run-configuration/)
- [CLI reference](https://santandermetgroup.github.io/trasgu/cli-reference/)
- [SLURM and HPC](https://santandermetgroup.github.io/trasgu/slurm-hpc/)
- [Troubleshooting](https://santandermetgroup.github.io/trasgu/troubleshooting/)

## Development

```bash
uv sync --frozen
uv run pytest
uv run ruff check .
```

## Scientific experiments

Article-scale case studies live under `experiments/`, separately from the
small examples packaged with Trasgu:

- `clayton_7d` contains the code snapshots and compact results for repeated
  seven-dimensional synthetic fits and sample-size scaling. Complete outputs
  are prepared for the accompanying Zenodo data deposit.
- `ship_wake` contains the eight-variable ship-wake case study.

See [`experiments/README.md`](https://github.com/SantanderMetGroup/trasgu/blob/develop/experiments/README.md) for the distinction
between execution snapshots, committed summaries, and the common external data
record containing both experiments.

## Benchmarks

Controlled performance measurements live under `benchmarks/`. They are kept
separate from scientific experiments and use the shared Matplotlib style in
`styles/trasgu.mplstyle`.

- `dimensional_workload` summarizes the fitting workload from four to eight
  variables.
- `pyvinecopulib_thread_scaling` measures the scaling of one fixed fit as the
  number of `pyvinecopulib` threads increases.

See [`benchmarks/README.md`](https://github.com/SantanderMetGroup/trasgu/blob/develop/benchmarks/README.md) for the benchmark protocol
and reproduction commands.

## Validation

Scientific validation workflows live under `validation/`. They compare Trasgu
with reference fits and, where applicable, the previous manual implementation.
See [`validation/README.md`](https://github.com/SantanderMetGroup/trasgu/blob/develop/validation/README.md) for the available cases and
reproduction commands.

## Cloud validation

The `Cloud validation` GitHub Actions workflow runs the packaged Snakemake
workflow on a clean GitHub-hosted Linux runner. It configures `trasgu` to use
all cores reported by the runner, checks that the example completed, and
uploads the resulting CSV, checksums, environment details, and Snakemake logs
as a workflow artifact.

The workflow runs after relevant pushes and can also be started manually from
the Actions tab.
