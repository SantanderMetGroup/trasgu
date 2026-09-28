# Seven-dimensional Clayton experiment

This experiment fits all 2,580,480 seven-dimensional Chimera matrices to each
of 100 independent synthetic datasets containing 300 observations. The 100
inputs were generated from Chimera matrix 252000 with Clayton pair copulas
and parameter 3.1819 (Kendall's tau approximately 0.61). Fits use
`pyvinecopulib.one_par`, maximum likelihood estimation, and AIC selection.

The campaign ran on Altamira's `wncompute_meteo` partition. Each dataset was divided
into 10 chunks of at most 260,000 matrices, with 16 workers per fitting job:
1,000 fitting jobs across the 100 datasets. The outer Snakemake workflow
coordinated the simulations and invoked Trasgu's workflow for each one. Its
recorded command was `snakemake --snakefile Snakefile --config iterations=100
--cores 5`; those five cores control the outer workflow, not the total CPUs
used by the fitting jobs.

The historical files in `original_execution` are preserved as
execution records. The preparation script below defaults to
`wncompute_meteo`, matching the retained profile.

GitHub contains the scripts, snapshots, compact comparison table and figures.
The data package uploaded to Zenodo contains the 100 original inputs, per-iteration reference
and best-fit results, configurations and main logs. Only iteration 99 retains
the complete 2,580,480-row exhaustive result table. See
[`../zenodo/staging/clayton_7d/README.md`](../zenodo/staging/clayton_7d/README.md) for the revised package and source deposit.

The repository is organized as follows:

```text
clayton_7d/
├── README.md
├── workflow/             # Prepare and launch a new campaign
├── original_execution/   # Original scripts, configuration and bootstrap input
├── analysis/             # Verify results and reproduce tables and figures
├── results/              # Compact comparison of the 100 simulations
└── figures/              # Figures in PDF, PNG and SVG formats
```

`workflow/` adapts the original configuration for a new working directory.
`original_execution/` records the files used during the original campaign.
The data package adds `simulations/iteration_1` through `iteration_100`,
with the full fit table stored inside `simulations/iteration_99/`.

## Reproduce the results

Use a checkout of this repository with Python and its dependencies installed
(for example, `python -m pip install -e '.[benchmarks,slurm]'`). Extract the
revised `clayton_7d-softwarex-v2.tar.gz` package, then run from the repository
root, replacing `/path/to/clayton_7d-softwarex-v2` with its location:

```bash
python experiments/clayton_7d/analysis/verify_data.py /path/to/clayton_7d-softwarex-v2
python experiments/clayton_7d/analysis/build_aic_summaries.py \
  /path/to/clayton_7d-softwarex-v2/simulations
```

The first command checks all 100 inputs and compact results and the complete
case-99 table. The second writes `results/aic_comparison.csv`,
**overwriting that file**. Each row records the iteration, selected matrix,
exhaustive AIC, Dissmann AIC, AIC after refitting the generating structure
with Clayton families, and AIC of the generating model at its fixed parameters.
These last two reference values describe different models.

## Reproduce the figures

From the repository root, run:

```bash
python experiments/clayton_7d/analysis/plot_aic_differences.py
python experiments/clayton_7d/analysis/plot_signed_aic_differences.py
```

The scripts read the compact table, apply `styles/trasgu.mplstyle`, and write
`aic_differences` and `signed_aic_differences` under `figures`
in PNG, PDF and SVG formats. Both compare the exhaustive and Dissmann AIC
with the refitted generating structure; the first uses absolute differences
and the second retains their signs.

## Repeat the fitting campaign

Prepare a new working directory using the deposited observations. By default,
Chimera matrices are read directly from
`http://meteo.unican.es/work/chimera.zarr`; no local copy is required.
Use `--chimera /path/to/chimera.zarr` to use a local store instead.
The nodes running the fits need access to the remote store when using the default:

```bash
python experiments/clayton_7d/workflow/prepare_run.py \
  /scratch/clayton-repeat \
  --inputs /path/to/clayton_7d-softwarex-v2/simulations
cd /scratch/clayton-repeat
snakemake --cores 5 --dry-run
snakemake --cores 5
```

Review `slurm_profile.yaml` before submission and adapt the partition,
account, memory and time limits to the available cluster. Use `--partition`
and `--workers` when preparing the directory to change their defaults.
The prepared workflow reads the copied observations, refits the reference
models, launches the exhaustive fits, selects the best candidates and writes
`aic_comparison.csv` in the working directory. Original reference results are
retained as `references_original.yaml`. The workflow does not generate data.
Use `--iterations 1` during preparation for a one-dataset trial; even that
trial fits the complete collection of 2,580,480 matrices.

## Generate new observations

The historical generator did not record random seeds. The deposited inputs
are therefore needed to repeat the original analysis. To generate a new
campaign using the same model, prepare another directory and run the copied
generator before launching Snakemake:

```bash
python experiments/clayton_7d/workflow/prepare_run.py \
  /scratch/clayton-new --new-data
cd /scratch/clayton-new
python simulate.py 100
snakemake --cores 5 --dry-run
snakemake --cores 5
```

`simulate.py` writes new observations and reference fits for iterations 1–100.
Its root-level `vinecop_samples.txt` is a bootstrap input used to infer the
seven-variable collection, not an analyzed dataset. Repeating the generator
in the same directory overwrites its generated inputs. 
