# Ship-wake experiment

This experiment fits the eight variables selected from the ship-and-wake data
set in `UI-1_ship_and_wake_data_for_TUDelft.csv`.

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
in Git because it is generated from the included source data. The Trasgu
configuration uses the public Chimera Zarr store by default. On a cluster
without internet access, download a local copy and add its location to
`trasgu.yaml`, for example:

```yaml
trasgu_url: /scratch/user/chimera.zarr
```

The Dissmann comparison uses the same prepared observations:

```bash
cd experiments/ship_wake
python dissmann.py
```
