# Related work

PSOR Semantic Contract builds on established ideas rather than claiming invention
of language-independent semantics.

Relevant technical traditions include:

- formal semantics and scope-sensitive representations such as DRT and MRS;
- Abstract Meaning Representation (AMR) and Uniform Meaning Representation (UMR);
- interlingual systems such as Universal Networking Language (UNL);
- Grammatical Framework (GF), separating abstract syntax from language-specific
  concrete syntax;
- Semantic Web and provenance standards, including W3C PROV-O, SHACL and RDF
  Dataset Canonicalization;
- nanopublications and content-addressed/verifiable semantic artifacts;
- event sourcing and append-only state;
- neuro-symbolic semantic parsing.

Two especially close patent families should also be read when evaluating the
field:

- US 12,724,957, *Formal transformer: system and method for deterministically
  transforming documents into multiple representations...*;
- US 12,001,805 and related Gyan Meaning Representation hyperGraph work.

The distinctive design focus of this specification is the **semantic lifecycle
and authority boundary**: probabilistic or heterogeneous interpretation may
produce candidates; a versioned contract governs promotion; promotion creates a
content-addressed immutable interpretation record; generated projections are
non-authoritative relative to that record; semantic correction occurs by
supersession rather than mutation.

This document is descriptive technical context, not a legal novelty opinion.

## Selected references

- W3C PROV-O: https://www.w3.org/TR/prov-o/
- W3C SHACL: https://www.w3.org/TR/shacl/
- RDF Dataset Canonicalization: https://www.w3.org/TR/rdf-canon/
- GF: https://www.grammaticalframework.org/
- ACL Anthology: https://aclanthology.org/
- US 12,724,957: https://patents.justia.com/patent/12724957
- US 12,001,805: https://patents.justia.com/patent/12001805
