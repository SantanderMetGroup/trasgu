# Scientific experiments

This directory contains article-scale scientific case studies. Small runnable
examples distributed with Trasgu remain under `src/trasgu/examples`, while
controlled performance measurements live under `benchmarks` and validation
workflows under `validation`.

- [Clayton 7D](clayton_7d/README.md): 100 synthetic datasets of 300 observations fitted across all
  seven-dimensional Chimera matrices. The generated inputs and selected
  outputs are distributed through Zenodo.
- [Ship wake](ship_wake/README.md): exhaustive fitting of eight variables selected from the
  ship-and-wake dataset, together with a Dissmann comparison. A representative
  raw chunk and the curated execution logs are prepared for the same deposit.

Each experiment README documents whether its configurations are portable or
preserved as exact, infrastructure-specific execution snapshots.

The two experiments are published together in one Zenodo record, as separate
archives so that either dataset can be downloaded independently. See
[`zenodo/README.md`](zenodo/README.md) for the common deposit layout.
