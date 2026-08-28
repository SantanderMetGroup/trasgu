# pyvinecopulib thread scaling

This benchmark measures repeated fits of one fixed eight-dimensional vine
structure while varying `FitControlsVinecop.num_threads`. Execution order is
randomized and the median duration is used for the scaling figure.

The input contains 300 pseudo-observations synthetically generated using
Clayton copulas with high dependence. The benchmark was run on the same
infrastructure as the seven-dimensional Clayton experiments: an Intel Xeon
Silver 4208 CPU at 2.10 GHz, using `pyvinecopulib` 0.7.6.

Run the benchmark and regenerate the figure from the repository root:

```bash
python benchmarks/pyvinecopulib_thread_scaling/benchmark.py
python benchmarks/pyvinecopulib_thread_scaling/plot_results.py
```

`results/thread_summary.csv` contains the measurements used by the existing
article figure. Rerunning the benchmark replaces it and also writes the raw
measurements to `results/thread_timings.csv`.

The figure reports only measured `pyvinecopulib` thread scaling. It does not
claim or assume ideal scaling for Trasgu workers.
