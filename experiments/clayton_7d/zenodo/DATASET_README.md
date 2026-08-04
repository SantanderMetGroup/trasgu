# Seven-dimensional Clayton experiment data

This data package accompanies the Trasgu SoftwareX article. It contains the
generated inputs and selected outputs for exhaustive fits of all 2,580,480
seven-dimensional Chimera matrices.

Two experiments are represented:

1. 100 independent synthetic datasets with 300 observations each.
2. One synthetic dataset for each of 100, 300, 600, 1000, 1500, 2000, 2500,
   and 3000 observations. The 300-observation point is iteration 1 of the
   repeated experiment.

The generating model uses Chimera matrix 252000 and Clayton pair copulas with
parameter 3.1819. The package preserves the original workflow and
configuration snapshots, including infrastructure-specific paths.

## Contents

- `workflow_snapshots`: exact run files also published with the software.
- `runs_by_sample_size`: generated observations, reference fits, selected best
  fit, detailed best-fit description, configuration, and main Trasgu log.
- `repeated_300/summary`: aggregate results for all 100 repeated fits.
- `sample_size_scaling/summary`: AIC and timing summaries and figures.
- `sample_size_scaling/timing_logs`: successful per-chunk SLURM logs used to
  derive the timing table.
- `representative_full_fits`: complete 2,580,480-row exhaustive result tables
  for iteration 99 at 300 observations and iteration 1 at 3000 observations.
- `metadata`: execution provenance and SHA-256 checksums.

The root-level `vinecop_samples.txt` in each workflow snapshot is a bootstrap
input used by the historical script to determine the seven-variable Chimera
collection. The analyzed synthetic inputs are the files stored inside the
iteration directories.

Snakemake state, caches, font caches, and per-chunk CSV files duplicating the
combined representative result tables are excluded.

## Integrity

From the package root, verify all deposited files with:

```bash
shasum -a 256 -c metadata/SHA256SUMS
```

## Related software

- Trasgu repository: https://github.com/fernanqv/trasgu
- Trasgu release/tag used for publication: pending
- Dataset DOI: pending

The original workflows, synthetic data, results, figures, logs, and
documentation in this package are released under the MIT License.
