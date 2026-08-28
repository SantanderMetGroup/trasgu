# Dimensional workload

This benchmark summarizes the workload required to fit every Chimera matrix
for four to eight variables. Each input contains 300 pseudo-observations
synthetically generated using Clayton copulas with high dependence. The
fitting setup uses one CPU core and the one-parameter families available in
`pyvinecopulib`.

The benchmark was run on the same infrastructure as the seven-dimensional
Clayton experiments: an Intel Xeon Silver 4208 CPU at 2.10 GHz, using
`pyvinecopulib` 0.7.6. The values in `results/timings.csv` are those used by
the article figure.

Generate the figure from the repository root:

```bash
python benchmarks/dimensional_workload/plot_results.py
```
