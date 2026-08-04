# SoftwareX experiment data deposit

The data accompanying the Trasgu SoftwareX article are prepared outside this
Git repository and published as one versioned Zenodo record. The upload keeps
the two experiments in separate archives:

```text
README.md
CITATION.cff
LICENSE
THIRD_PARTY_NOTICES.md
MANIFEST.csv
SHA256SUMS
clayton_7d-softwarex-v1.tar.gz
ship_wake-softwarex-v1.tar.gz
```

`clayton_7d` contains the synthetic validation and sample-size study.
`ship_wake` contains the large-scale case study, curated execution logs, and a
representative raw output chunk. Separate archives avoid forcing users to
download data for an experiment they do not need, while the common Zenodo
record provides one DOI for the article's complete experimental evidence.

All original code, generated data, derived results, figures, and documentation
in the deposit are released under the MIT License. Third-party source material
is covered only when its copyright holder has licensed it compatibly; see
`THIRD_PARTY_NOTICES.md`.

Before publication:

1. confirm the origin and reuse terms of the ship-wake source CSV;
2. replace all `pending` release and DOI fields;
3. verify the archive hashes against `SHA256SUMS`;
4. upload the eight files above as one Zenodo record;
5. select `MIT License` in Zenodo's license field;
6. add the resulting DOI to both experiment READMEs and the article.

Zenodo data DOI: pending.
