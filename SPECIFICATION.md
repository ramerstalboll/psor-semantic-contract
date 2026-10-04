# PSOR Semantic Contract 1.0 — Draft 0.1

**Status:** design draft; not adopted; not a PSOR Core release.  
**Target contract:** `psor-semantic-contract/1.0`  
**Normative draft identifier:** `1.0.0-draft.1`

## 1. Purpose

PSOR Semantic Contract 1.0 defines when information extracted or interpreted from a source may be promoted from a provisional interpretation into durable semantic state.

The central rule is:

> **Source is evidence. Promoted semantics is authoritative system state. Language is a projection.**

“Authoritative” means authoritative for **the system's recorded interpretation of what a source expresses under an exact contract version and coverage profile**. It does not mean that a source assertion is factually or legally true.

The contract is intentionally **independent of PSOR Core**. It can be implemented by any system. PSOR Core is one possible binding.

The contract is designed to prevent semantic degradation across repeated translation, summarization, model calls, product boundaries and long-lived storage. A source may be interpreted by probabilistic or deterministic mechanisms, but downstream consumers rely on the promoted semantic record rather than repeatedly reinterpreting language projections.

## 2. Non-goals

This contract does not claim to:

- capture every aspect of human meaning;
- prove that source assertions are true;
- eliminate genuine ambiguity in natural language;
- prescribe a particular LLM, parser, ontology, storage engine or graph technology;
- make every natural-language rendering perfectly invertible;
- replace original evidence;
- make probabilistic interpretation deterministic.

Instead, it makes semantic preservation testable **with respect to a declared semantic coverage profile**.

## 3. Abstract model

### 3.1 Source

An immutable piece of preserved evidence or source material.

Examples include an email, letter, PDF, screenshot, API payload, transcript, form or captured message.

A Source has an identifier, cryptographic digest and enough metadata to retrieve or audit the preserved evidence.

### 3.2 Semantic Statement

A structured proposition derived from or about one or more Sources.

A statement contains an expression and may contain attribution, provenance, epistemic status and derivation links.

The baseline expression model consists of:

- **predicate expressions** — a predicate plus named semantic roles;
- **operator expressions** — an explicit operator applied to one or more nested expressions.

This intentionally makes scope structural.

Examples:

`NOT(APPROVED(application))`

and

`MUST(NOT(PAY(company)))`

are represented as different expression trees.

### 3.3 Interpretation Candidate

A provisional proposed semantic interpretation produced by one or more mechanisms, including LLMs, deterministic parsers, rules, human annotation or hybrids.

A candidate is never authoritative semantic state merely because it was generated.

### 3.4 Canonical Semantic Record (CSR)

A **content-addressed closed semantic package** containing:

- preserved Source references and digests;
- Semantic Statements;
- explicit unresolved/ambiguous items;
- an exact Semantic Manifest;
- a Promotion Receipt.

The CSR is the durable representation of an interpretation under an exact Semantic Contract version and coverage profile.

The abstract CSR is independent of PSOR Core, RDF, JSON-LD and any particular database.

### 3.5 Promotion

The explicit transition by which an Interpretation Candidate becomes a CSR after satisfying the applicable contract and assurance requirements.

Promotion is the boundary between potentially probabilistic interpretation and deterministic downstream reliance.

### 3.6 Promotion Receipt

The immutable record of why a specific CSR was promotable. It binds at least:

- exact source digests;
- exact Semantic Contract version;
- exact coverage-profile version;
- semantics-affecting vocabulary/ontology versions;
- candidate identifiers or preserved candidate outputs;
- validation paths and results;
- unresolved material ambiguity, if permitted;
- promotion assurance level;
- canonicalization algorithm;
- semantic digest;
- promotion timestamp.

### 3.7 Projection

Any representation generated from a CSR for a consumer, including natural-language text, summaries, UI views, notifications, API payloads and integration formats.

A projection is not authoritative over the CSR from which it was generated.

### 3.8 Supersession

A new CSR may correct, extend or reinterpret an earlier CSR.

The earlier CSR is never mutated. The new CSR explicitly names the record it supersedes and preserves provenance for the change.

### 3.9 Contract-lossless

A transformation is **contract-lossless** when no information required by the declared semantic coverage profile is removed, strengthened, weakened or silently resolved.

Contract-lossless does not mean “all human meaning has been captured”.

## 4. Semantic Manifest

Every CSR MUST contain an immutable Semantic Manifest that identifies at least:

- Semantic Contract name and exact version;
- coverage-profile identifier and exact version;
- all semantics-affecting vocabulary/ontology identifiers and versions;
- Source identifiers;
- Semantic Statement identifiers;
- unresolved-item identifiers;
- canonicalization algorithm and digest algorithm;
- superseded CSR identifiers, when applicable.

The reference JSON binding is defined by `semantic/schema/semantic-manifest.schema.json`.

## 5. Baseline semantic coverage profile

The proposed `administrative-communication/1` profile requires preservation, where present, of:

1. **Referents and identity** — actors, resources, requests, cases and other referenced things, including unresolved identity.
2. **Predicates and semantic roles** — what action/state is asserted and who or what participates in each role.
3. **Polarity and negation scope**.
4. **Modality and deontic force** — e.g. MUST, MAY, CAN, SHOULD, PROHIBITED and their scope.
5. **Quantification** — e.g. ALL, SOME, NONE, cardinalities and scope where material.
6. **Conditions and alternatives** — IF, UNLESS, AND, OR and material branch conditions.
7. **Temporal semantics** — event time, validity, ordering, deadlines and temporal scope where expressed.
8. **Attribution** — who asserts, requests, reports, promises, denies or decides what.
9. **Epistemic status** — asserted, inferred, estimated, uncertain, ambiguous or unknown.
10. **Values** — amounts, units, identifiers, references and exact literals where material.
11. **Provenance** — Source and source location/span sufficient to audit each material source-derived proposition.

Pragmatics, irony, metaphor and emotional tone are outside this baseline unless a future coverage profile explicitly includes them.

## 6. Normative invariants

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are normative requirements of this draft.

### SC-01 — Source preservation

Every promoted CSR MUST reference preserved Sources. A derived representation MUST NOT substitute for an available original Source.

### SC-02 — Provenance completeness

Every material source-derived Semantic Statement MUST be traceable to a Source and to a sufficiently precise source location or span when the medium permits it.

### SC-03 — Attribution preservation

Attribution MUST be represented as part of meaning.

`COMPANY_ASSERTS(P)` MUST NOT be silently reduced to `P`.

### SC-04 — Operator and scope preservation

Negation, modality, quantification and conditions MUST retain explicit scope.

`NOT(MUST(PAY))` is not semantically equivalent to `MUST(NOT(PAY))`.

`NOT(APPROVED(application))` MUST NOT be strengthened to `REJECTED(application)` unless separately justified.

### SC-05 — Uncertainty conservation

Ambiguity, uncertainty and unknown values MUST NOT silently become certainty downstream.

Where a required distinction cannot be resolved, the CSR MUST preserve an explicit unresolved state or competing alternatives.

### SC-06 — Inference separation

Source assertions, system inferences and normative/legal effects MUST remain distinguishable.

Derived statements MUST preserve derivation links and MUST NOT masquerade as source statements.

### SC-07 — Semantic closure under the declared profile

For every semantic dimension required by the declared coverage profile, material information present in the Source MUST be represented or explicitly marked unresolved/unsupported.

### SC-08 — Deterministic canonicalization

A promoted CSR MUST name a canonicalization algorithm and digest algorithm such that the covered semantic payload has a deterministic canonical representation and digest.

### SC-09 — Exact version binding

A CSR MUST bind the exact Semantic Contract version, coverage-profile version and all semantics-affecting vocabulary/ontology versions used for promotion.

### SC-10 — Promotion immutability

After promotion, semantic data covered by the CSR digest MUST NOT change.

### SC-11 — Supersession, not mutation

Corrections, reinterpretations and ontology improvements MUST produce a new CSR. They MUST NOT rewrite the historical CSR.

### SC-12 — Projection non-authority

A projection MUST NOT overwrite, weaken or strengthen its parent CSR merely because it has been reformatted, summarized, translated or rendered.

If a projection participates in a later real-world communication, that communicated representation is ingested as a **new Source**.

### SC-13 — No reinterpretation through projections

A downstream component that receives a CSR MUST consume the CSR for semantic information already represented there.

It MUST NOT re-parse a generated projection and treat that result as a replacement for the parent CSR.

New inference is permitted, but MUST remain derived semantics under SC-06.

### SC-14 — Candidate disagreement preservation

Material disagreement between interpretation candidates MUST be reconciled, explicitly adjudicated or preserved as unresolved before promotion at an assurance level that claims the disputed dimension as resolved.

Repeated prompting of one model MUST NOT automatically be described as independent validation.

### SC-15 — Semantic round-trip conformance

A projection mechanism that claims reversible semantic conformance SHOULD demonstrate:

`parse(render(CSR, projectionProfile)) ≡ CSR`

with equivalence evaluated only over semantic dimensions declared by the applicable coverage/profile pair.

Textual identity is neither required nor expected.

### SC-16 — Cross-language invariance

Different language renderings of the same CSR MUST derive from the same promoted semantic source.

A conforming multilingual renderer SHOULD pass SC-15 for every claimed language/profile combination.

### SC-17 — Reproducible verification

A verifier MUST be able to validate the CSR using preserved Source references, exact manifests, captured interpretation evidence, deterministic validators and named canonicalization/digest algorithms.

Bit-for-bit regeneration of a historical probabilistic model output is not required if that output itself was preserved for the promotion decision.

### SC-18 — Append-only semantic lifecycle

Candidate creation, validation, promotion, projection, derived inference and supersession MUST be auditable as distinct lifecycle events.

Historical semantic state MUST NOT disappear through silent overwrite.

## 7. Promotion assurance levels

These levels describe evidence for **the interpretation**, not truth of underlying claims.

### A0 — Candidate

Not promoted. No authoritative downstream reliance.

### A1 — Validated

At least one interpretation path, complete source provenance, structural/semantic invariant validation and explicit unresolved states.

### A2 — Cross-validated

A1 plus materially independent interpretation or validation paths for profile-designated material dimensions, with disagreements reconciled or preserved.

### A3 — Adjudicated

A2 plus explicit human/domain-authority adjudication where required.

Implementations MAY define stricter profiles. They MUST NOT relabel lower assurance as higher assurance without satisfying declared requirements.

## 8. Reference JSON binding

The draft repository contains an executable reference binding under `semantic/`:

- `schema/semantic-record.schema.json`
- `schema/semantic-manifest.schema.json`
- `schema/promotion-receipt.schema.json`
- `validator.py`
- `fixtures/`

The reference binding uses an explicitly limited canonical JSON algorithm named `psor-draft-json-v1`.

For the semantic-digest payload:

1. `recordId` and `promotionReceipt` are excluded to avoid circular addressing.
2. Object keys are sorted lexicographically.
3. Arrays that are sets in the abstract model are sorted by stable identifiers.
4. Expression operand order is preserved because operator order may be semantically significant.
5. Scalars are limited to strings, integers, booleans and null; floating-point numbers are not permitted in the digest-covered draft subset.
6. The normalized value is serialized as UTF-8 JSON without insignificant whitespace.
7. SHA-256 is applied to those bytes.
8. A promoted record identifier is `csr:sha256:<hex-digest>`.

This draft algorithm exists to make the first conformance suite executable. A future standards-based binding MAY replace it without changing the abstract contract.

## 9. Example: avoiding semantic strengthening

Source:

> Ansökan är inte godkänd.

A valid structured expression is:

`NOT(APPROVED(application_123))`

attributed to the relevant source actor and traced to the source sentence.

It does **not** automatically imply:

`REJECTED(application_123)`

because “not approved” may also describe a pending or incomplete state.

A separately evidenced domain rule MAY derive rejection, but that result becomes a derived statement under SC-06.

## 10. Lifecycle

```text
Source(s)
   |
   v
Interpretation Candidate(s)
   |
   +--> contract checks
   +--> independent parser/model/human validation
   +--> ambiguity/reconciliation
   |
   v
PROMOTION BOUNDARY
   |
   v
Canonical Semantic Record + Promotion Receipt
   |
   +--> state
   +--> reasoning
   +--> automation
   +--> APIs
   +--> Swedish rendering
   +--> German rendering
   +--> future projections
```

There is deliberately no authority path from a projection back into its parent CSR.

## 11. Bindings

The Semantic Contract is implementation-neutral.

Possible bindings include:

- JSON/JSON Schema;
- RDF/JSON-LD;
- W3C PROV-O for provenance;
- SHACL for graph constraints;
- RDF Dataset Canonicalization for an RDF binding;
- domain models such as PSOR Core.

A binding MUST preserve the abstract invariants and publish testable mapping/canonicalization rules.

PSOR-specific and other domain-model bindings are deliberately outside this publication.

## 12. Conformance classes for 1.0

Before final 1.0, the reference suite SHOULD include:

- negation-scope pairs;
- modality-scope pairs;
- quantifier-scope pairs;
- attribution-vs-fact pairs;
- ambiguous referent cases;
- temporal validity cases;
- source-vs-inference cases;
- competing-source cases;
- multilingual round-trips;
- semantic-strengthening traps;
- supersession without mutation;
- projection re-ingestion as new evidence;
- deterministic semantic-digest fixtures;
- candidate-disagreement and assurance-level downgrade cases.

## 13. Design thesis

PSOR does not attempt to make language immutable.

It makes **interpreted information content-addressable, contract-bound, auditable and immutable**, while treating language and other consumer formats as non-authoritative projections of that information.

The durable object is therefore best described as:

> **an immutable interpretation under a versioned semantic contract**

rather than “immutable meaning”.
