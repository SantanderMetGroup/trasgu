# SoftwareX experiment data deposit

The data accompanying the Trasgu SoftwareX article are prepared outside this
Git repository and published as one versioned Zenodo record. The upload keeps
the two experiments in separate archives:

```text
README.md
CITATION.cff
LICENSE
RIGHTS.md
THIRD_PARTY_NOTICES.md
MANIFEST.csv
SHA256SUMS
clayton_7d-softwarex-v1.tar.gz
ship_wake-softwarex-v1.tar.gz
```

`clayton_7d` contains the synthetic validation and sample-size study.
`ship_wake` contains the large-scale case study, curated execution logs, and a
representative raw output chunk. The third-party source observations and the
row-level pseudo-observations derived from them are not included. Separate
archives avoid forcing users to download data for an experiment they do not
need, while the common Zenodo record provides one DOI for the article's
experimental evidence.

All original code, generated data, derived results, figures, and documentation
in the deposit are released under the MIT License. See `RIGHTS.md` and
`THIRD_PARTY_NOTICES.md` for the scope of the deposit and the excluded
third-party material.

Zenodo data DOI: https://doi.org/10.5281/zenodo.21807187.

Related archived objects:

- Chimera matrices: https://doi.org/10.5281/zenodo.21804549
- Trasgu software: https://doi.org/10.5281/zenodo.21806023
