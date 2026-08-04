# Ship-wake Zenodo data package

The ship-wake component is prepared outside Git as
`ship_wake-softwarex-v1.tar.gz` and uploaded in the same Zenodo record as the
Clayton 7D archive.

It contains:

- the exact workflow and cluster-configuration snapshot;
- the source observations and preparation script;
- the compact best-fit summary;
- raw chunk `0067`, containing 4,000,000 rows for vine IDs 268,000,000 through
  271,999,999;
- one successful SLURM log for each of the 166 chunks;
- the failed production attempts, separated from successful logs;
- the final Snakemake log that combined all 166 chunks;
- a chunk manifest and SHA-256 checksums.

The representative CSV is preserved without a header. Its columns are
`vine_id`, `n_parameters`, and `aic`. It represents approximately 0.61% of the
660,602,880 matrices and must not be interpreted as the complete exhaustive
result table. The compact best-fit summary was derived from the complete
combined result before that large intermediate file was discarded.

Snakemake metadata, scheduler state, source-cache duplicates, matplotlib font
caches, and exploratory top-level logs are excluded.

The original workflow, derived results, logs, manifests, and documentation are
released under the MIT License. The license of the source ship-wake CSV must be
confirmed separately; see `THIRD_PARTY_NOTICES.md` in the common deposit.

Zenodo data DOI: pending.
