# Seven-dimensional Clayton experiments

This directory contains the code snapshots and compact results for two
seven-dimensional synthetic-data experiments:

- `repeated_300`: 100 independent fits, each using 300 observations.
- `sample_size_scaling`: one fit for each of 100, 300, 600, 1000, 1500,
  2000, 2500, and 3000 observations.

All datasets were simulated from Chimera matrix 252000 with Clayton pair
copulas and parameter 3.1819 (Kendall's tau approximately 0.61). Every
exhaustive fit considered all 2,580,480 seven-dimensional Chimera matrices.

## Execution snapshots

The `Snakefile`, `trasgu.yaml`, `slurm_profile.yaml`, and companion scripts
under each `execution_snapshot` are preserved byte for byte as used for the
reported executions. They contain GPFS paths and SLURM settings specific to
the original infrastructure and are provenance records, not portable
defaults. Repeating an experiment requires adapting the Chimera Zarr path,
SLURM resources, profile, and filesystem paths.

Each snapshot also retains a root-level `vinecop_samples.txt`. This is a
bootstrap input used by `Trasgu` to infer that the Chimera collection has
seven variables before `simulate.py` generates the actual datasets. It is not
one of the analyzed datasets; those are stored per iteration in the Zenodo
data deposit.

For sample-size scaling, the 300-observation timing uses iteration 1 of the
100-run experiment. The other sizes were run once. The original workflow was
invoked with 100 iterations for `repeated_300` and one iteration for each
sample-size run.

## Results and figures

Compact CSV summaries and publication figures are committed under each
`results` directory. All figures use `styles/trasgu.mplstyle`.

Regenerate the figures from the repository root:

```bash
python experiments/clayton_7d/analysis/plot_aic_differences.py
python experiments/clayton_7d/analysis/analyze_total_slurm_execution_time.py \
  --from-csv
```

After extracting the Zenodo data, rebuild both AIC tables with:

```bash
python experiments/clayton_7d/analysis/build_aic_summaries.py \
  /path/to/extracted/runs_by_sample_size
```

The complete synthetic inputs, per-run outputs, timing logs, and two
representative exhaustive result tables are kept outside Git and will be
published together with the ship-wake archive in one Zenodo data record. See
`zenodo/README.md` for the Clayton archive layout and `../zenodo/README.md` for
the common deposit. Replace the pending DOI after publication.

Zenodo data DOI: https://doi.org/10.5281/zenodo.21807187.
