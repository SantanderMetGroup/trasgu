# Validation

This directory contains scientific validation workflows. These are distinct
from the small packaged examples, performance benchmarks, and article case
studies.

## Cases

- `clayton_6_t13`: repeated synthetic validation for a fixed
  six-dimensional Clayton vine, comparing exhaustive Chimera fitting,
  Dissmann selection, and the fixed generating structure.
- `esrel`: five-dimensional validation used for the ESREL workflow. It also
  preserves the previous manual implementation under `legacy/` so its output
  can be compared with Trasgu.

Generated simulation directories are written below each case as
`simulations/` and are ignored by Git. Curated comparison tables and figures
belong in each case's `results/` directory.

Regenerate the validation figures from the repository root:

```bash
python validation/plot_aic_differences.py \
  validation/clayton_6_t13/results/aic_comparison.csv
python validation/plot_aic_differences.py \
  validation/esrel/results/aic_comparison.csv
```

All figures use the shared style in `styles/trasgu.mplstyle`.
