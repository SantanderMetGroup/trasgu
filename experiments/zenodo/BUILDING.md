# Building and publishing the SoftwareX experiment deposit

The Clayton package is reviewed in `staging/clayton_7d/`. Edit its README and
metadata there; these are the authoritative copies tracked by Git. Keep the
local staged scripts, data, results and figures until publication. `downloads/`
is a backup and is not used to rebuild Clayton.

## Verify before packaging

From the repository root:

```bash
python experiments/zenodo/build_deposit.py --verify-only
```

This command validates the 100 Clayton inputs, compact results and full case-99
table, plus the ship-wake raw chunk and logs, without generating files. Review documentation and figures directly in
staging as well.

## Package after review

```bash
python experiments/zenodo/build_deposit.py \
  --output-dir experiments/zenodo/dist/repeated-300-v2
```

The builder packages the reviewed files without regenerating scientific
outputs. It adds `metadata/SHA256SUMS` in a temporary copy, leaves staging
untouched, and writes archives and outer integrity manifests to the output
directory. A non-empty output directory is rejected.

## Before publication

1. Review the staging contents and finalize citation/version metadata.
2. Generate the archives and verify their internal and outer checksums.
3. Confirm that ship-wake source observations and pseudo-observations are excluded.
4. Upload the output files as one Zenodo record with the MIT License.
5. Preview and download the draft files before publication.
6. Keep `downloads/` until the replacement deposit has been verified and published.

The reviewed ship-wake package is in `staging/ship_wake/`. Its README,
manifest, provenance metadata and raw-chunk description are tracked by Git.
Source observations and pseudo-observations are excluded. Local original
execution files and the private source CSV are retained in
`downloads/ship_wake_local/`, excluded from Git.
