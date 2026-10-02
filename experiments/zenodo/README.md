# SoftwareX experiment data deposit

The upload bundle keeps the Clayton and ship-wake experiments in separate
archives. The revised Clayton archive contains 100 datasets of 300
observations, selected per-iteration results and a complete exhaustive table
only for case 99. Both archives are packaged from their reviewed staging directories.

The source record is https://doi.org/10.5281/zenodo.21807187. This revised
bundle has not yet been built or uploaded and has no new DOI. `CITATION.cff` marks it as a draft. Finalize its version and DOI when
publishing the revision.

The reviewed Clayton package is maintained directly in `staging/clayton_7d/`.
Its README, license, manifest and provenance metadata are kept in Git. The
staged code, results, figures and observations are local copies; the code and
compact results are maintained in `../clayton_7d/`. Changes to those files must
be copied into staging and reviewed before packaging. The builder never
refreshes them automatically.

`downloads/` retains the previous deposit as a backup for both experiments. It is excluded from Git. `dist/` is created when
packaging and is also excluded from Git.

## Review the deposit

From the repository root, with the project and benchmark dependencies installed:

```bash
python experiments/zenodo/build_deposit.py --verify-only
```

This checks both staged packages without writing files.
A fresh Git checkout contains only the staged documentation and metadata;
restore the reviewed local package files before verifying or compressing it.

## Package the reviewed deposit

After reviewing the staging directory, run:

```bash
python experiments/zenodo/build_deposit.py \
  --output-dir experiments/zenodo/dist/repeated-300-v2
```

The output directory must be empty. The builder verifies both packages, copies
the reviewed staging directories to a temporary directory, adds checksums and
compresses them. It does not regenerate summaries, figures or fits, or modify
staging. Use `--clayton-staging` to choose another reviewed directory.
Ship-wake is packaged from `staging/ship_wake/` in the same way; use
`--ship-staging` to select another reviewed directory.

The resulting bundle contains:

```text
README.md
CITATION.cff
LICENSE
RIGHTS.md
THIRD_PARTY_NOTICES.md
MANIFEST.csv
SHA256SUMS
clayton_7d-softwarex-v2.tar.gz
ship_wake-softwarex-v2.tar.gz
```

## Verify the deposit

From the output directory, run:

```bash
shasum -a 256 -c SHA256SUMS
```

Each archive also includes an internal `metadata/SHA256SUMS`. The archive
READMEs document their contents and reproduction commands. Original code,
generated data and derived materials use the MIT License. Ship-wake source
observations and their row-level pseudo-observations are excluded; see
`RIGHTS.md` and `THIRD_PARTY_NOTICES.md`.

The reviewed ship-wake package is in `staging/ship_wake/`. Its README,
manifest, provenance metadata and raw-chunk description are tracked by Git.
Source observations and pseudo-observations are excluded. Local original
execution files and the private source CSV are retained in
`downloads/ship_wake_local/`, excluded from Git.
