# Dimensional workload

This benchmark estimates the time needed to fit every Chimera matrix for
four to eight variables. Each input contains 300 pseudo-observations generated
from Clayton copulas with high dependence. Fits use one CPU core,
`pyvinecopulib.one_par`, maximum likelihood estimation, and AIC selection.
The results in `results/timings.csv` were obtained on an Intel(R) Xeon(R)
Gold 5218 CPU @ 2.30GHz.

## Reproduce the benchmark

Use a checkout of this repository with Python and its dependencies installed
(for example, `python -m pip install -e '.[benchmarks]'`). Provide a local
Chimera Zarr store containing `matrices4` through `matrices8`. From the
repository root, run on a compute node with one CPU core allocated:

```bash
python benchmarks/dimensional_workload/benchmark.py /path/to/chimera.zarr
```

The script reads the five `benchmarks/data/input*_300_clayton_high.txt` files.
It fits all 24 matrices for four variables and all 480 for five variables.
For each of six, seven, and eight variables, it fits 1,000 evenly spaced
matrices and multiplies their mean fitting time by the total number of
matrices. Matrix loading is excluded from the timed intervals. The resulting
estimates describe serial fitting time on one core; they are not workflow
wall-clock times. To change the sample size, pass `--sample N`.

The command writes `benchmarks/dimensional_workload/results/timings.csv`,
**overwriting that file** if it exists. The CSV records the number of fits
timed and whether each total was measured or extrapolated. Results will vary
with the CPU and `pyvinecopulib` version.

## Reproduce the figure

From the repository root, after creating `timings.csv`, run:

```bash
python benchmarks/dimensional_workload/plot_results.py
```

The plotting script reads `results/timings.csv`, applies
`styles/trasgu.mplstyle`, and writes `figures/dimensional_workload.png`,
`.pdf`, and `.svg`.
