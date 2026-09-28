# Seven-dimensional Clayton experiment data

This package contains 100 independent synthetic datasets with 300 observations
and seven variables each. They were generated from Chimera matrix 252000,
using Clayton pair copulas with parameter 3.1819. All 2,580,480 candidate
matrices were fitted to each dataset. The campaign ran on Altamira's `wncompute_meteo`
partition, with 10 chunks per dataset and 16 workers per chunk.

`simulations/iteration_1` through `iteration_100` contain the original
observations, reference fits, best-fit summaries, detailed best fits,
configurations and main workflow logs. `simulations/iteration_99/fit_iteration_99.csv` is the
only complete exhaustive result table: 2,580,480 rows plus a header. All 100
iterations are represented in `results/aic_comparison.csv`.
The generating-model AIC at fixed parameters and the AIC after refitting the
generating structure with Clayton families are distinct reference values.

The historical scripts and configuration in `original_execution/` are preserved
unchanged. `workflow/` contains the helpers for preparing a new campaign;
`analysis/`, `results/` and `figures/` contain the analysis scripts, compact
comparison table and figures.
The preparation helper defaults to `wncompute_meteo`, matching the retained
profile and the execution partition. Details and
limits of the recovered environment are recorded under `metadata/`.

This is a revised package prepared for review, not a newly published record.
The source deposit is https://doi.org/10.5281/zenodo.21807187. No new DOI has
yet been assigned. Original material is released under the included MIT License.

When the reviewed package is compressed, `metadata/SHA256SUMS` is added to
the archive. From the extracted archive, verify it with
`shasum -a 256 -c metadata/SHA256SUMS`.

## Reproduce the results

Install Trasgu with its benchmark and SLURM dependencies, as described in the
[repository](https://github.com/SantanderMetGroup/trasgu). From this package root:

```bash
python analysis/verify_data.py .
python analysis/build_aic_summaries.py simulations
```

The last command overwrites the derived comparison table. The verification
checks all observation files, compact results and the full table for case 99.
The archive retains main workflow logs, but not a complete set of scheduler
logs for all 1,000 chunk jobs.

## Reproduce the figures

From the package root:

```bash
python analysis/plot_aic_differences.py
python analysis/plot_signed_aic_differences.py
```

The scripts read the comparison table and apply `styles/trasgu.mplstyle`.
They write absolute and signed AIC-difference figures under
`figures` in PNG, PDF and SVG formats.

## Repeat the fitting campaign

Prepare a new directory. By default, Chimera matrices are read directly from
`http://meteo.unican.es/work/chimera.zarr`; no local copy is required.
Use `--chimera /path/to/chimera.zarr` to use a local store instead.
The nodes running the fits need access to the remote store when using the default:

```bash
python workflow/prepare_run.py /scratch/clayton-repeat \
  --inputs simulations
cd /scratch/clayton-repeat
snakemake --cores 5 --dry-run
snakemake --cores 5
```

Review the prepared SLURM profile and adapt partition, account, memory and
runtime to your infrastructure before submitting. The outer workflow
coordinates the simulations; each nested Trasgu workflow launches the chunk
jobs. `--cores 5` is not the total CPU allocation for the distributed campaign.
The prepared workflow refits the references and exhaustive models using the
copied observations, preserving the original reference values separately.

## Generate new observations

The original generator did not save random seeds. To reproduce the original
analysis, reuse the deposited observations. To generate another campaign:

```bash
python workflow/prepare_run.py /scratch/clayton-new \
  --new-data
cd /scratch/clayton-new
python simulate.py 100
snakemake --cores 5 --dry-run
snakemake --cores 5
```

The generator overwrites generated inputs if rerun in the same directory.
The root-level input in the snapshot only establishes the dataset dimension;
the analyzed data are the per-iteration files. Results may vary with package
versions. Historical provenance and current reproduction tools are separate.
