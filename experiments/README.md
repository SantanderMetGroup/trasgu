# Scientific experiments

This directory contains article-scale scientific case studies. Small runnable
examples distributed with Trasgu remain under `src/trasgu/examples`, while
controlled performance measurements live under `benchmarks` and validation
workflows under `validation`.

- `clayton_7d`: repeated synthetic validation and sample-size scaling across
  all seven-dimensional Chimera matrices. Complete generated data and selected
  raw outputs are prepared for the accompanying Zenodo data deposit.
- `ship_wake`: exhaustive fitting of eight variables selected from the
  ship-and-wake dataset, together with a Dissmann comparison. A representative
  raw chunk and the curated execution logs are prepared for the same deposit.

Each experiment README documents whether its configurations are portable or
preserved as exact, infrastructure-specific execution snapshots.

The two experiments are published together in one Zenodo record, as separate
archives so that either dataset can be downloaded independently. See
[`zenodo/README.md`](zenodo/README.md) for the common deposit layout.
