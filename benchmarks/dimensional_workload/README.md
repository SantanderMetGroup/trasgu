# Dimensional workload

This benchmark summarizes the workload required to fit every Chimera matrix
for four to eight variables. Each input contains 300 pseudo-observations and
the fitting setup uses one CPU core and the one-parameter families available
in `pyvinecopulib`.

The values currently recorded in `results/timings.csv` are the values used by
the existing article figure. Before publication, record the machine,
`pyvinecopulib` version, repetition strategy, and whether each total was
measured directly or extrapolated from per-fit timings.

Generate the figure from the repository root:

```bash
python benchmarks/dimensional_workload/plot_results.py
```
