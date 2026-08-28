# Ship-wake experiment data

This data package accompanies the Trasgu SoftwareX article. It preserves the
analysis code, workflow snapshot, selected derived results, execution evidence,
and one representative raw output chunk from the exhaustive fit of all
660,602,880 eight-dimensional Chimera matrices.

## Contents

- `code`: scripts used to prepare the observations and run the comparison.
- `analysis`: processed AIC distribution, plotting script, style, and figures.
- `workflow_snapshot`: exact workflow and cluster configuration used.
- `results/best_fits.txt`: compact summary derived from the complete fit.
- `raw_results`: gzip-compressed chunk 0067 (4,000,000 rows).
- `logs/successful_chunks`: one successful SLURM log for each of 166 chunks.
- `logs/failed_chunk_attempts`: earlier attempts retained as execution evidence.
- `logs/workflow_attempts`: top-level Snakemake execution attempts.
- `logs/final_combination.log`: successful final combination run.
- `metadata/chunk_manifest.csv`: mapping from chunks to SLURM job identifiers.
- `metadata/execution_environment.txt`: execution-system summary.
- `metadata/software_revision.txt`: software-release and provenance details.
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

## Source-data availability

The third-party source observations are not publicly available and are not
included in this package. Row-level pseudo-observations derived from them are
also excluded. Complete numerical reproduction therefore requires obtaining
authorized access to the source observations independently. The public package
supports inspection of the workflow, derived fit results, figures, and
execution provenance.
