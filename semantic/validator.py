"""Reference validator for PSOR Semantic Contract 1.0-draft.1.

This is deliberately small and implementation-neutral. It validates the draft JSON
binding, cross-record invariants, promotion assurance and the draft content-addressed
semantic digest.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "schema"

SCHEMA_PATHS = {
    "manifest": SCHEMA_DIR / "semantic-manifest.schema.json",
    "receipt": SCHEMA_DIR / "promotion-receipt.schema.json",
    "record": SCHEMA_DIR / "semantic-record.schema.json",
    "projection": SCHEMA_DIR / "projection.schema.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


SCHEMAS = {name: _load_json(path) for name, path in SCHEMA_PATHS.items()}
REGISTRY = Registry()
for schema in SCHEMAS.values():
    REGISTRY = REGISTRY.with_resource(schema["$id"], Resource.from_contents(schema))

FORMAT_CHECKER = FormatChecker()

_SET_STRING_KEYS = {
    "sourceIds",
    "statementIds",
    "unresolvedIds",
    "supersedesRecordIds",
    "derivedFromStatementIds",
}
_SET_OBJECT_ID_KEYS = {"sources", "statements", "unresolved"}


def _canonical_normalize(value: Any, parent_key: str | None = None) -> Any:
    if isinstance(value, float):
        raise ValueError("psor-draft-json-v1 forbids floating-point values")

    if isinstance(value, dict):
        return {
            key: _canonical_normalize(value[key], key)
            for key in sorted(value)
        }

    if isinstance(value, list):
        normalized = [_canonical_normalize(item, parent_key) for item in value]

        if parent_key in _SET_STRING_KEYS:
            return sorted(normalized)

        if (
            parent_key in _SET_OBJECT_ID_KEYS
            and all(isinstance(item, dict) and "id" in item for item in normalized)
        ):
            return sorted(normalized, key=lambda item: item["id"])

        if parent_key == "vocabularies":
            return sorted(normalized, key=lambda item: (item["id"], item["version"]))

        if parent_key == "provenance":
            return sorted(
                normalized,
                key=lambda item: json.dumps(
                    item, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ),
            )

        return normalized

    if value is None or isinstance(value, (str, int, bool)):
        return value

    raise ValueError(f"unsupported canonical value type: {type(value).__name__}")


def semantic_payload(record: dict[str, Any]) -> dict[str, Any]:
    """Return exactly the data covered by the semantic digest.

    recordId and promotionReceipt are excluded to avoid circular addressing.
    """
    return {
        "manifest": copy.deepcopy(record["manifest"]),
        "sources": copy.deepcopy(record["sources"]),
        "statements": copy.deepcopy(record["statements"]),
        "unresolved": copy.deepcopy(record["unresolved"]),
    }


def canonical_bytes(record: dict[str, Any]) -> bytes:
    normalized = _canonical_normalize(semantic_payload(record))
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def semantic_digest_hex(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def expected_record_id(record: dict[str, Any]) -> str:
    return f"csr:sha256:{semantic_digest_hex(record)}"


def finalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Fill content-addressed identity fields on a draft record."""
    result = copy.deepcopy(record)
    digest = semantic_digest_hex(result)
    record_id = f"csr:sha256:{digest}"
    result["recordId"] = record_id
    result["promotionReceipt"]["recordId"] = record_id
    result["promotionReceipt"]["semanticDigest"] = f"sha256:{digest}"
    return result


def _schema_errors(instance: Any, schema_name: str) -> list[str]:
    validator = Draft202012Validator(
        SCHEMAS[schema_name],
        registry=REGISTRY,
        format_checker=FORMAT_CHECKER,
    )
    return [
        f"schema:{schema_name}:{'/'.join(str(p) for p in error.absolute_path)}:{error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    ]


def _walk_expression(expression: dict[str, Any], errors: list[str], path: str) -> None:
    if expression.get("kind") != "operator":
        return

    operator = expression["operator"]
    operands = expression["operands"]
    unary = {"NOT", "MUST", "MAY", "CAN", "SHOULD", "PROHIBITED", "ALL", "SOME", "NONE"}
    binary = {"IF", "UNLESS", "BEFORE", "AFTER", "UNTIL"}

    if operator in unary and len(operands) != 1:
        errors.append(f"{path}:operator {operator} requires exactly one operand")
    if operator in binary and len(operands) != 2:
        errors.append(f"{path}:operator {operator} requires exactly two operands")
    if operator in {"AND", "OR"} and len(operands) < 2:
        errors.append(f"{path}:operator {operator} requires at least two operands")

    for index, operand in enumerate(operands):
        _walk_expression(operand, errors, f"{path}.operands[{index}]")


def validate_record(record: dict[str, Any]) -> list[str]:
    errors = _schema_errors(record, "record")
    if errors:
        return errors

    manifest = record["manifest"]
    receipt = record["promotionReceipt"]

    source_ids = [item["id"] for item in record["sources"]]
    statement_ids = [item["id"] for item in record["statements"]]
    unresolved_ids = [item["id"] for item in record["unresolved"]]

    for label, values in (
        ("source", source_ids),
        ("statement", statement_ids),
        ("unresolved", unresolved_ids),
    ):
        if len(values) != len(set(values)):
            errors.append(f"duplicate {label} id")

    if set(source_ids) != set(manifest["sourceIds"]):
        errors.append("manifest sourceIds do not exactly match record sources")
    if set(statement_ids) != set(manifest["statementIds"]):
        errors.append("manifest statementIds do not exactly match record statements")
    if set(unresolved_ids) != set(manifest["unresolvedIds"]):
        errors.append("manifest unresolvedIds do not exactly match record unresolved items")

    source_set = set(source_ids)
    statement_set = set(statement_ids)

    for statement in record["statements"]:
        _walk_expression(statement["expression"], errors, f"statement:{statement['id']}")
        for provenance in statement.get("provenance", []):
            if provenance["sourceId"] not in source_set:
                errors.append(
                    f"statement:{statement['id']}:unknown source {provenance['sourceId']}"
                )
        for parent_id in statement.get("derivedFromStatementIds", []):
            if parent_id not in statement_set:
                errors.append(
                    f"statement:{statement['id']}:unknown derived parent {parent_id}"
                )

    if receipt["semanticContract"] != manifest["semanticContract"]:
        errors.append("promotion receipt semanticContract differs from manifest")
    if receipt["coverageProfile"] != manifest["coverageProfile"]:
        errors.append("promotion receipt coverageProfile differs from manifest")
    if receipt["canonicalization"] != manifest["canonicalization"]:
        errors.append("promotion receipt canonicalization differs from manifest")

    material_unresolved = {
        item["id"] for item in record["unresolved"] if item["material"]
    }
    if set(receipt["unresolvedMaterialIds"]) != material_unresolved:
        errors.append("receipt unresolvedMaterialIds do not match material unresolved items")

    groups = {path["independenceGroup"] for path in receipt["validationPaths"]}
    assurance = receipt["assuranceLevel"]
    if assurance in {"A2", "A3"} and len(groups) < 2:
        errors.append(f"{assurance} requires at least two independent validation groups")
    if assurance == "A3" and not any(
        path["kind"] == "human" for path in receipt["validationPaths"]
    ):
        errors.append("A3 requires a human adjudication validation path")

    digest = semantic_digest_hex(record)
    wanted_id = f"csr:sha256:{digest}"
    wanted_digest = f"sha256:{digest}"

    if record["recordId"] != wanted_id:
        errors.append("recordId does not match canonical semantic digest")
    if receipt["recordId"] != record["recordId"]:
        errors.append("promotion receipt recordId differs from recordId")
    if receipt["semanticDigest"] != wanted_digest:
        errors.append("promotion receipt semanticDigest does not match canonical payload")

    if record["recordId"] in manifest.get("supersedesRecordIds", []):
        errors.append("record cannot supersede itself")

    return errors


def validate_projection(
    projection: dict[str, Any], parent_record: dict[str, Any]
) -> list[str]:
    errors = _schema_errors(projection, "projection")
    if errors:
        return errors

    if projection["parentRecordId"] != parent_record["recordId"]:
        errors.append("projection parentRecordId differs from parent CSR")
    if (
        projection["parentSemanticDigest"]
        != parent_record["promotionReceipt"]["semanticDigest"]
    ):
        errors.append("projection parentSemanticDigest differs from parent CSR")

    return errors


def _meaning_statement(statement: dict[str, Any]) -> dict[str, Any]:
    result = {
        "assertionKind": statement["assertionKind"],
        "expression": statement["expression"],
        "epistemicStatus": statement["epistemicStatus"],
        "material": statement["material"],
    }
    if "attribution" in statement:
        result["attribution"] = statement["attribution"]
    return result


def semantic_signature(record: dict[str, Any]) -> bytes:
    """Canonical comparison signature excluding language/source-specific provenance."""
    meaning = {
        "statements": [_meaning_statement(s) for s in record["statements"]],
        "unresolved": [
            {
                "semanticDimension": item["semanticDimension"],
                "material": item["material"],
                "alternatives": item.get("alternatives", []),
            }
            for item in record["unresolved"]
        ],
    }

    meaning["statements"] = sorted(
        meaning["statements"],
        key=lambda item: json.dumps(
            _canonical_normalize(item),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
    meaning["unresolved"] = sorted(
        meaning["unresolved"],
        key=lambda item: json.dumps(
            _canonical_normalize(item),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

    return json.dumps(
        _canonical_normalize(meaning),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def semantically_equivalent(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return semantic_signature(left) == semantic_signature(right)
