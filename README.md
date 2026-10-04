# PSOR Semantic Contract 1.0-draft.1

**Public technical disclosure and executable draft specification**

PSOR Semantic Contract defines a lifecycle for converting source material into a
version-bound, content-addressed **Canonical Semantic Record (CSR)** that can be
used indefinitely without repeatedly reinterpreting natural-language projections.

> **Source is evidence. Promoted semantics is authoritative system state. Language is a projection.**

The core lifecycle is:

```text
Source
  ↓
Interpretation Candidate(s)
  ↓
validation / reconciliation
  ↓
PROMOTION BOUNDARY
  ↓
Canonical Semantic Record
  ↓
language / UI / API / reasoning / automation projections
```

Interpretation may be probabilistic. Promotion and downstream semantic identity are
deterministic and auditable.

## Scope of this repository

This repository is intentionally limited to the standalone Semantic Contract
publication. It contains:

- the normative draft specification;
- JSON Schemas for Semantic Manifest, CSR, Promotion Receipt and Projection;
- the `administrative-communication/1` coverage profile;
- the `psor-draft-json-v1` reference canonicalization and validator;
- synthetic Swedish and German fixtures;
- executable conformance tests;
- related-work notes.

It intentionally contains **no PSOR Core schemas or bindings, no PSOR product
code, no user data, no deployment configuration, and no private PSOR
infrastructure**.

## Version

`psor-semantic-contract/1.0.0-draft.1`

This is a draft specification and a public technical disclosure, not a claim that
all aspects of human meaning can be represented losslessly.

Semantic preservation claims are always **contract-relative**: a transformation is
contract-lossless only for the semantic dimensions declared by its coverage profile.

## Run the conformance suite

Requires Python 3.12+.

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s conformance/tests -v
```

## Release integrity

See `RELEASE-MANIFEST.json`. The manifest lists SHA-256 digests for every file
covered by the release and an aggregate `sha256-path-hash-v1` release digest.

## Licensing

- Specification and prose documentation: **CC BY 4.0**.
- Schemas, reference validator, fixtures and tests: **Apache-2.0**.

See `LICENSE-SPECIFICATION.md` and `LICENSE-CODE`.

## Citation

Citation metadata is provided in `CITATION.cff`.

The canonical public version is the tagged GitHub release; archival identifiers
(DOI and SWHID) are added to the publication receipt when available.
