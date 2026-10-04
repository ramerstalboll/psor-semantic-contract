# Semantic Contract conformance fixtures

These fixtures are synthetic and contain no real user data.

- `not-approved-sv.json` is a promoted Swedish CSR for
  `NOT(APPROVED(application:123))`.
- `not-approved-de.json` represents the same contract-covered meaning from a
  German source and therefore has a different content digest but the same
  semantic comparison signature.

The reference tests derive negative and scope-contrast cases from these frozen
fixtures. This keeps the fixtures small while testing:

- deterministic content addressing;
- cross-language semantic equivalence;
- NOT(APPROVED) versus REJECTED strengthening;
- NOT(MUST(P)) versus MUST(NOT(P));
- attribution and provenance requirements;
- A2/A3 promotion assurance;
- explicit unresolved material ambiguity;
- projection parent binding;
- supersession without mutation.

The cross-language fixture tests semantic equivalence **after parsing**. It does
not claim that draft.1 includes a Swedish or German natural-language parser.
Parser/generator implementations are separate components that can claim SC-15
round-trip conformance against this contract.
