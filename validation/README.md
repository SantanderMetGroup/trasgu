# Validation

This directory aims to demonstrate that **Trasgu with Chimera matrices stored
in Zarr** reproduces **manual sequential fitting using the original Chimera
files from TU Delft**. The comparison fits every matrix with both methods,
using identical observations and `pyvinecopulib` settings, and checks the AIC
of every fitted model, not only the best fit.

## Validation designs

Both cases use the same five-variable generating structure (Chimera ID 61).
Each contains 100 simulations with 300 observations each. The linked
configurations show the full matrix and the family, rotation and parameter
of every generating bicopula.

| Case and complete configuration | Generating bicopulas | Master seed | Matrices per dataset | Paired AIC comparisons |
| --- | --- | --- | --- | --- |
| [ESREL](esrel/README.md#generating-configuration) | 10 Clayton, θ = 3.1819 | 20260928 | 480 | 48,000 |
| [Mixed families](mixed_5d/README.md#generating-configuration) | 6 Clayton, θ = 3.1819; 4 Gaussian, ρ = 0.5 | 20260929 | 480 | 48,000 |

All generating rotations are zero. The Gaussian edges in the mixed case are
(tree, edge) = (1, 2), (1, 3), (2, 2) and (3, 2), using the numbering in the
family and parameter arrays (row = tree, column = edge).

Together, the cases provide **96,000 paired AIC comparisons**:
2 cases × 100 datasets × 480 structures. Each comparison pairs one Trasgu fit
with one manual sequential fit of the same structure to the same observations.
This means 96,000 structure fits per method, or 192,000 across both methods;
additional Dißmann and fixed-model reference fits are outside this count.

## Generating models and fitting controls

The configurations above define how observations are generated. Exhaustive
fitting and Dißmann selection instead use candidate families from
`pyvinecopulib.one_par`, AIC family selection and maximum likelihood parameter
estimation. They are not restricted to the generating family assignment.
The additional fixed-model references retain the generating structure and
families and re-estimate their parameters.

## Agreement and reproduction

Both cases fit **all matrices in both ways** and obtain the
same AICs within `1e-5`, with maximum discrepancies below `5e-7`, consistent
with Trasgu's six-decimal CSV output.  Both methods use
`pyvinecopulib`, so this validates matrix storage and execution rather than
independently validating the fitting library.

From the repository root, install with `uv sync --frozen --extra benchmarks`.
Each case README provides its run command and results. Compact results belong
in `results/`; generated observations, catalogues, full fit tables and logs
are ignored by Git. Figures use `styles/trasgu.mplstyle`.
