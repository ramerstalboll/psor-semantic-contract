import copy
import json
import unittest
from pathlib import Path

from semantic.validator import (
    canonical_bytes,
    finalize_record,
    semantic_digest_hex,
    semantically_equivalent,
    validate_projection,
    validate_record,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "semantic" / "fixtures"


def load_fixture(name):
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class SemanticContractDraft1Tests(unittest.TestCase):
    def setUp(self):
        self.sv = load_fixture("not-approved-sv.json")
        self.de = load_fixture("not-approved-de.json")

    def test_frozen_swedish_fixture_is_valid(self):
        self.assertEqual([], validate_record(self.sv))

    def test_frozen_german_fixture_is_valid(self):
        self.assertEqual([], validate_record(self.de))

    def test_known_semantic_digest_is_deterministic(self):
        self.assertEqual(
            "cfa7aa3f328eff4c577b76edab94498db5d1bc05d8dbb3541c99ef00c489295a",
            semantic_digest_hex(self.sv),
        )
        self.assertEqual(canonical_bytes(self.sv), canonical_bytes(self.sv))

    def test_cross_language_records_have_same_semantic_signature(self):
        self.assertNotEqual(self.sv["recordId"], self.de["recordId"])
        self.assertTrue(semantically_equivalent(self.sv, self.de))

    def test_not_approved_is_not_rejected(self):
        strengthened = copy.deepcopy(self.sv)
        strengthened["statements"][0]["expression"] = {
            "kind": "predicate",
            "predicate": "REJECTED",
            "roles": {"theme": {"kind": "entity", "id": "application:123"}},
        }
        strengthened = finalize_record(strengthened)
        self.assertEqual([], validate_record(strengthened))
        self.assertFalse(semantically_equivalent(self.sv, strengthened))

    def test_modal_scope_not_must_differs_from_must_not(self):
        pay = {
            "kind": "predicate",
            "predicate": "PAY",
            "roles": {
                "agent": {"kind": "entity", "id": "company:1"},
                "theme": {"kind": "entity", "id": "refund:1"},
            },
        }

        not_must = copy.deepcopy(self.sv)
        not_must["statements"][0]["expression"] = {
            "kind": "operator",
            "operator": "NOT",
            "operands": [
                {"kind": "operator", "operator": "MUST", "operands": [pay]}
            ],
        }
        not_must = finalize_record(not_must)

        must_not = copy.deepcopy(self.sv)
        must_not["statements"][0]["expression"] = {
            "kind": "operator",
            "operator": "MUST",
            "operands": [
                {"kind": "operator", "operator": "NOT", "operands": [pay]}
            ],
        }
        must_not = finalize_record(must_not)

        self.assertEqual([], validate_record(not_must))
        self.assertEqual([], validate_record(must_not))
        self.assertFalse(semantically_equivalent(not_must, must_not))

    def test_source_statement_requires_attribution(self):
        candidate = copy.deepcopy(self.sv)
        del candidate["statements"][0]["attribution"]
        errors = validate_record(candidate)
        self.assertTrue(any("attribution" in error for error in errors), errors)

    def test_source_provenance_must_reference_preserved_source(self):
        candidate = copy.deepcopy(self.sv)
        candidate["statements"][0]["provenance"][0]["sourceId"] = "source:missing"
        candidate = finalize_record(candidate)
        errors = validate_record(candidate)
        self.assertTrue(any("unknown source" in error for error in errors), errors)

    def test_material_unresolved_must_be_bound_into_receipt(self):
        candidate = copy.deepcopy(self.sv)
        candidate["unresolved"] = [
            {
                "id": "unresolved:recipient",
                "semanticDimension": "referents-and-identity",
                "description": "Recipient identity cannot be resolved.",
                "material": True,
                "alternatives": [
                    {
                        "kind": "predicate",
                        "predicate": "IDENTITY",
                        "roles": {
                            "referent": {"kind": "entity", "id": "recipient:unknown"},
                            "candidate": {"kind": "entity", "id": "person:a"},
                        },
                    },
                    {
                        "kind": "predicate",
                        "predicate": "IDENTITY",
                        "roles": {
                            "referent": {"kind": "entity", "id": "recipient:unknown"},
                            "candidate": {"kind": "entity", "id": "person:b"},
                        },
                    },
                ],
            }
        ]
        candidate["manifest"]["unresolvedIds"] = ["unresolved:recipient"]
        candidate["promotionReceipt"]["unresolvedMaterialIds"] = []
        candidate = finalize_record(candidate)
        errors = validate_record(candidate)
        self.assertTrue(
            any("unresolvedMaterialIds" in error for error in errors), errors
        )

    def test_a2_requires_independent_validation_groups(self):
        candidate = copy.deepcopy(self.sv)
        candidate["promotionReceipt"]["validationPaths"][1]["independenceGroup"] = "model-a"
        errors = validate_record(candidate)
        self.assertTrue(any("independent validation groups" in error for error in errors), errors)

    def test_a3_requires_human_adjudication(self):
        candidate = copy.deepcopy(self.sv)
        candidate["promotionReceipt"]["assuranceLevel"] = "A3"
        errors = validate_record(candidate)
        self.assertTrue(any("human adjudication" in error for error in errors), errors)

    def test_semantic_tampering_breaks_content_address(self):
        tampered = copy.deepcopy(self.sv)
        tampered["statements"][0]["expression"]["operator"] = "MUST"
        errors = validate_record(tampered)
        self.assertTrue(any("recordId does not match" in error for error in errors), errors)

    def test_operator_arity_is_checked(self):
        candidate = copy.deepcopy(self.sv)
        expression = candidate["statements"][0]["expression"]
        expression["operands"].append(copy.deepcopy(expression["operands"][0]))
        candidate = finalize_record(candidate)
        errors = validate_record(candidate)
        self.assertTrue(any("requires exactly one operand" in error for error in errors), errors)

    def test_projection_is_bound_to_parent_but_not_semantic_state(self):
        projection = {
            "projectionId": "projection:de:1",
            "parentRecordId": self.sv["recordId"],
            "parentSemanticDigest": self.sv["promotionReceipt"]["semanticDigest"],
            "kind": "natural-language",
            "language": "de",
            "mediaType": "text/plain",
            "content": "Der Antrag ist nicht genehmigt.",
            "generatedAt": "2026-10-04T01:00:00Z",
            "generator": {"id": "fixture-renderer", "version": "1"},
        }
        self.assertEqual([], validate_projection(projection, self.sv))

        wrong = copy.deepcopy(projection)
        wrong["parentRecordId"] = self.de["recordId"]
        errors = validate_projection(wrong, self.sv)
        self.assertTrue(any("parentRecordId" in error for error in errors), errors)

    def test_supersession_creates_new_record_without_mutating_old(self):
        successor = copy.deepcopy(self.sv)
        successor["manifest"]["supersedesRecordIds"] = [self.sv["recordId"]]
        successor["statements"][0]["epistemicStatus"] = "uncertain"
        successor = finalize_record(successor)

        self.assertEqual([], validate_record(successor))
        self.assertNotEqual(self.sv["recordId"], successor["recordId"])
        self.assertEqual(
            [self.sv["recordId"]],
            successor["manifest"]["supersedesRecordIds"],
        )

    def test_manifest_must_close_over_record_ids(self):
        candidate = copy.deepcopy(self.sv)
        candidate["manifest"]["statementIds"] = []
        candidate = finalize_record(candidate)
        errors = validate_record(candidate)
        self.assertTrue(any("statementIds" in error for error in errors), errors)

    def test_derived_statement_requires_derivation_link(self):
        candidate = copy.deepcopy(self.sv)
        candidate["statements"][0]["assertionKind"] = "derived"
        candidate["statements"][0].pop("provenance", None)
        errors = validate_record(candidate)
        self.assertTrue(any("derivedFromStatementIds" in error for error in errors), errors)

    def test_draft_canonicalization_rejects_floats(self):
        candidate = copy.deepcopy(self.sv)
        candidate["statements"][0]["expression"] = {
            "kind": "predicate",
            "predicate": "AMOUNT",
            "roles": {
                "value": {"kind": "literal", "value": 1.5}
            },
        }
        with self.assertRaises(ValueError):
            semantic_digest_hex(candidate)


if __name__ == "__main__":
    unittest.main()
