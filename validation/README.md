# Validation

This directory aims to demonstrate that **Trasgu with Chimera matrices stored
in Zarr** reproduces **manual sequential fitting using the original Chimera
files from TU Delft**. The comparison fits every matrix with both methods,
using identical observations and `pyvinecopulib` settings, and checks the AIC
of every fitted model, not only the best fit.

Generation uses families belonging to `pyvinecopulib.one_par` (Clayton or
Gaussian). Exhaustive fitting and Dißmann selection use `one_par`; fixed-model
references retain the generating families and re-estimate their parameters.

Each case contains 100 simulations with 300 observations each:

| Case | Generating model | Matrices per dataset | Trasgu–manual agreement |
| --- | --- | --- | --- |
| [ESREL](esrel/README.md) | 5 variables, 10 Clayton edges | 480 | All 48,000 paired fits agree |
| [Mixed families](mixed_5d/README.md) | 5 variables, 6 Clayton and 4 Gaussian edges | 480 | All 48,000 paired fits agree |


Both cases fit **all matrices in both ways** and obtain the
same AICs within `1e-5`, with maximum discrepancies below `5e-7`, consistent
with Trasgu's six-decimal CSV output.  Both methods use
`pyvinecopulib`, so this validates matrix storage and execution rather than
independently validating the fitting library.

From the repository root, install with `uv sync --frozen --extra benchmarks`.
Each case README provides its run command and results. Compact results belong
in `results/`; generated observations, catalogues, full fit tables and logs
are ignored by Git. Figures use `styles/trasgu.mplstyle`.
