# Ship-wake experiment data

This data package accompanies the Trasgu SoftwareX article. It preserves the
inputs, workflow snapshot, selected results, execution evidence, and one
representative raw output chunk from the exhaustive fit of all 660,602,880
eight-dimensional Chimera matrices.

## Contents

- `input`: source observations and the scripts used to prepare and fit them.
- `workflow_snapshot`: exact workflow and cluster configuration used.
- `results/best_fits.txt`: compact summary derived from the complete fit.
- `raw_results`: gzip-compressed chunk 0067 (4,000,000 rows).
- `logs/successful_chunks`: one successful SLURM log for each of 166 chunks.
- `logs/failed_chunk_attempts`: earlier attempts retained as execution evidence.
- `logs/workflow_attempts`: top-level Snakemake execution attempts.
- `logs/final_combination.log`: successful final combination run.
- `metadata/chunk_manifest.csv`: mapping from chunks to SLURM job identifiers.
- `metadata/SHA256SUMS`: checksums for all files in this package.

The representative raw CSV has no header. Its columns are `vine_id`,
`n_parameters`, and `aic`; it covers vine IDs 268,000,000 through 271,999,999.
It represents approximately 0.61% of the exhaustive search and is not the
complete result table.

## Integrity

From the extracted package root, verify all files with:

```bash
shasum -a 256 -c metadata/SHA256SUMS
```

## Related software and data

- Trasgu software DOI: https://doi.org/10.5281/zenodo.21806023
- Trasgu repository: https://github.com/SantanderMetGroup/trasgu
- Chimera matrices dataset DOI: https://doi.org/10.5281/zenodo.21804549
- Experimental dataset DOI: https://doi.org/10.5281/zenodo.21807187

The source ship-wake CSV is included on the assumption that its redistribution
terms permit publication. This permission must be confirmed before publishing
the Zenodo record. See `THIRD_PARTY_NOTICES.md`.
