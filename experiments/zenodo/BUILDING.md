# Building and publishing the SoftwareX experiment deposit

This document contains maintainer instructions. It is kept in the Git
repository and is not included in the Zenodo deposit.

## Build the deposit

Build and verify the locally available ship-wake package from the repository
root:

```bash
python3 experiments/zenodo/build_deposit.py
```

The command writes the upload-ready files to `experiments/zenodo/dist`, which
is ignored by Git. It refuses to overwrite a non-empty output directory.

To include Clayton, first arrange its external results according to
`../clayton_7d/zenodo/MANIFEST.txt`, then run:

```bash
python3 experiments/zenodo/build_deposit.py \
  --clayton-source /path/to/clayton_7d-softwarex-v1
```

The builder checks the required Clayton directories, generates internal and
outer SHA-256 manifests, and creates deterministic gzip-compressed tar files.

## Before publication

1. Build both archives from the curated package sources.
2. Verify the internal and outer hashes against `SHA256SUMS`.
3. Confirm that no ship-wake source observations or pseudo-observations occur
   in the upload.
4. Upload the files from `experiments/zenodo/dist` as one Zenodo record.
5. Select `MIT License` in Zenodo's license field.
6. Preview and download the draft files before publication.
