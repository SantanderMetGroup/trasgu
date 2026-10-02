# pyvinecopulib thread scaling

This benchmark measures repeated fits of one fixed eight-dimensional vine
structure while varying `FitControlsVinecop.num_threads`. The input contains
300 pseudo-observations generated from Clayton copulas with high dependence.
Fits use `pyvinecopulib.one_par`, maximum likelihood estimation, and AIC
selection. The results in `results/thread_summary.csv` were obtained on an
Intel(R) Xeon(R) Gold 5218 CPU @ 2.30GHz.

The script reads `benchmarks/data/input8_300_clayton_high.txt` and selects
one vine structure using one thread; this selection is not timed. It then
fits that fixed structure seven times at each of 1, 2, 4, 8, 16, 20, 24,
28, 32, 36, 40, 44, and 48 threads. The 91 fits run in a shuffled order
with random seed 42. Each fit is timed separately, and the median duration
at each thread count is reported.

The command writes raw measurements to `results/thread_timings.csv` and
medians to `results/thread_summary.csv`, **overwriting both files** if they
exist. Results will vary with the CPU and `pyvinecopulib` version.

## Reproduce the benchmark

Use a checkout of this repository with Python and its dependencies installed
(for example, `python -m pip install -e '.[benchmarks]'`). From the repository
root, run on a compute node with up to 48 CPUs allocated:

```bash
python benchmarks/pyvinecopulib_thread_scaling/benchmark.py
```

## Reproduce the figure

From the repository root, after creating `thread_summary.csv`, run:

```bash
python benchmarks/pyvinecopulib_thread_scaling/plot_results.py
```

The plotting script divides the one-thread median by each measured median,
applies `styles/trasgu.mplstyle`, and writes `figures/thread_scaling.png`,
`.pdf`, and `.svg`. The figure shows measured speedup for this one fit.
