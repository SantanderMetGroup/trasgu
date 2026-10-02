# Ship-wake experiment

This experiment fits all 660,602,880 eight-dimensional Chimera matrices to
179 complete observations from the ship-wave dataset. Eight columns are
selected after removing incomplete rows and transformed into pseudo-observations.
The exhaustive fit uses 166 chunks of at most 4,000,000 matrices. The Dissmann
comparison uses the same observations and `pyvinecopulib.one_par`, maximum
likelihood estimation and AIC selection.

The first phase ran in `compute` with 8 workers per chunk; the remaining
chunks were completed in `wncompute_ifca` with 32 workers after a disk-quota
interruption. `original_execution/` preserves the workflow and configuration
from the resumed phase. Its GPFS paths and SLURM resources describe that
execution. `workflow/` contains helpers for preparing a new run.

The source observations can be requested by contacting A. C. Muscalus,
K. A. Haas and D. R. Webster, authors of *Observations of Primary Ship Waves
at the Margins of a Confined Tidal River*, Journal of Waterway, Port, Coastal,
and Ocean Engineering 150(5), 04024009 (2024),
[doi:10.1061/JWPED5.WWENG-2062](https://doi.org/10.1061/JWPED5.WWENG-2062).
Neither the source observations nor their row-level pseudo-observations are
included in GitHub or Zenodo.

`results/best_fits.txt` contains the compact fitted-model summary.
`results/processed_aic_cdf.npz` contains the processed AIC distribution needed
to reproduce the figure. The retained raw chunk is only a representative
subset and cannot reconstruct this full distribution.

The repository contains `workflow/`, `original_execution/`, `analysis/`,
`results/` and `figures/`. The accompanying Zenodo package (`ship_wake-softwarex-v2.tar.gz`)
additionally contains selected logs and one representative raw chunk. The source deposit is
[doi:10.5281/zenodo.21807187](https://doi.org/10.5281/zenodo.21807187); see
[`../zenodo/README.md`](../zenodo/README.md) for the common package layout and building instructions.

## Reproduce the figure

Install Trasgu with its benchmark dependencies. Run from the repository root:

```bash
python experiments/ship_wake/analysis/plot_large_aic_cdf.py
```

The script reads `results/processed_aic_cdf.npz`, applies `trasgu.mplstyle`,
and writes PDF and PNG files under `figures/`, overwriting existing figures.
No source observations are needed for this step.

## Repeat the fitting

Obtain the source CSV from the authors cited above and install Trasgu with
its benchmark and SLURM dependencies (`python -m pip install -e '.[benchmarks,slurm]'`
from a repository checkout). From the repository root:

```bash
python experiments/ship_wake/workflow/prepare_run.py /scratch/ship-wake-repeat \
  --data /path/to/UI-1_ship_and_wake_data_for_TUDelft.csv
cd /scratch/ship-wake-repeat
trasgu_run --profile slurm_profile.yaml --dry-run
trasgu_run --profile slurm_profile.yaml
python dissmann.py > dissmann.txt
```

The helper creates pseudo-observations and an adapted configuration in a new
directory. Review the SLURM account, partition, memory and runtime before
submission. Defaults match the resumed phase: `wncompute_ifca`, 32 workers
and chunks of 4,000,000 matrices. Use `--partition` and `--workers` to change
these settings. Chimera is read remotely by default; use `--chimera` for a
local directory or another HTTP(S) URL. Nodes need access to the selected store.
The archived scripts and configuration in `original_execution/` are preserved
as execution records. Numerical results may depend on software versions.

Zenodo data DOI: https://doi.org/10.5281/zenodo.21807187.
