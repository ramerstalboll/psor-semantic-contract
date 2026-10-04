# PSOR Semantic Contract — reference implementation

This directory is the standalone executable reference binding for
**PSOR Semantic Contract 1.0.0-draft.1**.

It does not depend semantically on PSOR Core. The surrounding repository is used
for development and CI only. A future public `psor-semantic-contract` repository
can be assembled from this directory plus the normative specification and
selected related-work documentation.

## Abstract lifecycle

```text
Source
  ↓
Interpretation Candidate(s)
  ↓
validation / reconciliation
  ↓
PROMOTION
  ↓
Canonical Semantic Record
  ↓
Projection(s)
```

Promotion is the authority boundary. Candidate generation may be probabilistic.
Promoted state is exact-version-bound, content-addressed and immutable.

## Reference JSON binding

Schemas:

- `schema/semantic-manifest.schema.json`
- `schema/semantic-record.schema.json`
- `schema/promotion-receipt.schema.json`
- `schema/projection.schema.json`

Reference implementation:

- `validator.py` — schema checks, cross-reference checks, promotion assurance,
  canonical digest verification, projection-parent verification and semantic
  comparison signatures.

Coverage profile:

- `profiles/administrative-communication-1.json`

Frozen examples:

- `fixtures/not-approved-sv.json`
- `fixtures/not-approved-de.json`

The two fixtures have different content-addressed CSR identifiers because they
have different source evidence, but their contract-covered semantic signatures
are equivalent.

## Draft canonicalization

`psor-draft-json-v1` exists only to make draft.1 mechanically reproducible.

The semantic digest covers:

- Semantic Manifest;
- Sources;
- Semantic Statements;
- unresolved semantic items.

It excludes `recordId` and `promotionReceipt` to avoid circular addressing.

The validator normalizes set-like arrays, sorts object keys, preserves
semantically significant expression operand order, encodes the result as compact
UTF-8 JSON and calculates SHA-256.

Floating-point values are excluded from the draft digest subset. This avoids
cross-runtime number-serialization ambiguity until a final canonicalization
binding is selected.

## Conformance

From the repository root:

```sh
python -m pip install -r requirements-dev.txt
python -m unittest conformance.tests.test_semantic_contract -v
```

The Semantic Contract tests are also included in `npm run check`.

The current suite covers:

- frozen digest reproducibility;
- cross-language semantic equivalence after parsing;
- NOT(APPROVED) ≠ REJECTED;
- NOT(MUST(P)) ≠ MUST(NOT(P));
- source attribution;
- source provenance closure;
- explicit unresolved material ambiguity;
- A2 independent validation;
- A3 human adjudication;
- tamper detection through content addressing;
- operator arity;
- projection-to-parent binding;
- supersession without mutation;
- manifest closure;
- derived-statement lineage;
- exclusion of floating-point values from draft canonicalization.

The suite does **not** contain a Swedish/German natural-language parser or
renderer. Those are separate implementations that may later claim SC-15/SC-16
conformance.

## Domain bindings

Domain-model bindings, including PSOR-specific bindings, are deliberately outside this standalone publication.
