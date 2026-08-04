# Clayton 7D Zenodo data package

The Clayton component of the Zenodo deposit is prepared outside the Git
repository as `clayton_7d-softwarex-v1.tar.gz`. It is uploaded alongside the
ship-wake archive in one common Zenodo record. GitHub contains only code
snapshots, compact result tables, figures, and this manifest.

The data package contains:

- the generated inputs and selected outputs for all 100 repeated 300-sample
  fits;
- the generated inputs and selected outputs for every sample-size run;
- per-chunk SLURM logs used to derive the timing summary;
- complete 2,580,480-row result tables for the 3000-sample run and iteration
  99 of the 300-sample experiment;
- exact workflow snapshots and provenance metadata.

Snakemake caches, scheduler state, font caches, and duplicate per-chunk CSVs
are deliberately excluded. The package includes `SHA256SUMS` for integrity
checking.

The package is released under the MIT License. Before publishing, record the
Zenodo DOI and replace the unresolved Trasgu execution revision in
`metadata/software_revision.txt` if it can be recovered.

Zenodo DOI: pending.
