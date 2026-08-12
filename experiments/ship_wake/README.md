# Ship-wake experiment

This experiment fits the eight variables selected from the ship-and-wake data
set in `UI-1_ship_and_wake_data_for_TUDelft.csv`. The exhaustive search covers
all 660,602,880 eight-dimensional Chimera matrices in 166 chunks.

## Repository contents

- `PrepareData.py` creates the pseudo-observations used by both fits.
- `trasgu.yaml` and `slurm_profile.yaml` are the configurations used for the
  reported cluster execution.
- `execution_snapshot` preserves those configurations and the exact Trasgu
  `Snakefile` recovered from Snakemake's source cache.
- `results/best_fits.txt` contains the compact fitted-model summary committed
  to Git.
- `zenodo/README.md` describes the raw result and logs kept outside Git for the
  accompanying data deposit.

The execution configuration is a provenance snapshot: it contains GPFS paths
and SLURM settings for the original IFCA infrastructure. Adapt the Chimera
Zarr path, profile, resources, and filesystem paths before repeating the run.

## Running the experiment

Install Trasgu with the dependencies needed to prepare the data:

```bash
python -m pip install -e '.[benchmarks]'
```

Generate the pseudo-observations and run the exhaustive fit from the repository
root:

```bash
python experiments/ship_wake/PrepareData.py
cd experiments/ship_wake
trasgu_run --profile slurm
```

`PrepareData.py` writes `unity_inbound.txt`, which is intentionally not stored
in Git because it is generated from the included source data. The preserved
configuration points to the local Chimera Zarr store used for the execution.
Replace `chimera_url` with a path or URL accessible from the target system, for
example:

```yaml
chimera_url: /scratch/user/chimera.zarr
```

The Dissmann comparison uses the same prepared observations:

```bash
cd experiments/ship_wake
python dissmann.py
```

## Archived data

The Git repository deliberately excludes Snakemake state and exhaustive result
tables. The accompanying Zenodo record contains one representative 4,000,000-
row raw chunk, the final successful log for every chunk, the failed attempts
needed to document retries, the final combination log, and integrity
manifests. The deposited raw chunk is evidence of the output format and scale;
it is not the complete 660,602,880-row result table.

Original workflows, derived results, logs, and documentation are released
under MIT. The provenance and reuse terms of the source ship-wake CSV must be
confirmed separately before publishing the Zenodo record.

Zenodo data DOI: https://doi.org/10.5281/zenodo.21807187.
