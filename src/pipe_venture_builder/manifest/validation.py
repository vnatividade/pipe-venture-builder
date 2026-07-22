"""Sanitized JSON Schema validation for portable toolkit contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INTERNAL_CONTRACT_ERROR, MANIFEST_INVALID
from pipe_venture_builder.inventory.safety import contains_sensitive_value

_SENSITIVE_PREFIX = re.compile(
    r"(?i)^(?:lin_api_|github_pat_|gh[pousr]_|sk-|AKIA[0-9A-Z])"
)


@dataclass(frozen=True, slots=True)
class ContractFinding:
    path: str
    schema_path: str
    rule: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "schemaPath": self.schema_path,
            "rule": self.rule,
            "message": self.message,
        }


def validate_document(instance: Any, schema: Any) -> list[ContractFinding]:
    """Validate any local Pipe contract without echoing instance values."""

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (
            _pointer(error.absolute_path),
            _pointer(error.absolute_schema_path),
        ),
    )
    return [_sanitize_error(error) for error in errors]


def validate_product_manifest(instance: Any, schema: Any) -> list[ContractFinding]:
    try:
        findings = validate_document(instance, schema)
    except SchemaError as exc:
        raise PipeError(
            code="MANIFEST_SCHEMA_INVALID",
            message="The ProductManifest schema is not a valid Draft 2020-12 contract.",
            exit_code=INTERNAL_CONTRACT_ERROR,
        ) from exc

    if isinstance(instance, dict):
        runtime = instance.get("runtime")
        if isinstance(runtime, dict):
            preferred = runtime.get("preferred")
            fallbacks = runtime.get("fallbacks")
            if isinstance(fallbacks, list) and preferred in fallbacks:
                findings.append(
                    ContractFinding(
                        path="/runtime/fallbacks",
                        schema_path="/properties/runtime",
                        rule="distinctRuntimeSelection",
                        message="The preferred runtime cannot also be a fallback.",
                    )
                )
        if any(_looks_sensitive(value) for value in _strings(instance)):
            findings.append(
                ContractFinding(
                    path="/",
                    schema_path="/",
                    rule="sensitiveValue",
                    message="ProductManifest cannot contain secret-shaped values.",
                )
            )
    return sorted(findings, key=lambda item: (item.path, item.schema_path, item.rule))


def invalid_manifest_error(findings: Iterable[ContractFinding]) -> PipeError:
    all_findings = list(findings)
    return PipeError(
        code="MANIFEST_INVALID",
        message=f"ProductManifest validation failed with {len(all_findings)} error(s).",
        exit_code=MANIFEST_INVALID,
        details=[finding.as_dict() for finding in all_findings[:50]],
    )


def _pointer(parts: Iterable[Any]) -> str:
    encoded = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(encoded) if encoded else "/"


def _sanitize_error(error: ValidationError) -> ContractFinding:
    rule = str(error.validator or "schema")
    return ContractFinding(
        path=_pointer(error.absolute_path),
        schema_path=_pointer(error.absolute_schema_path),
        rule=rule,
        message=_safe_message(error),
    )


def _safe_message(error: ValidationError) -> str:
    rule = error.validator
    expected = error.validator_value
    if rule == "required":
        missing = [
            name
            for name in expected
            if not isinstance(error.instance, dict) or name not in error.instance
        ]
        return (
            f"Missing required property: {missing[0]}."
            if len(missing) == 1
            else "One or more required properties are missing."
        )
    if rule == "type":
        allowed = ", ".join(expected) if isinstance(expected, list) else str(expected)
        return f"Expected value type: {allowed}."
    if rule == "format":
        return f"Value does not match required format: {expected}."
    if rule == "additionalProperties":
        return "One or more undeclared properties are present."
    if rule == "minLength":
        return f"Text must contain at least {expected} character(s)."
    if rule == "maxItems":
        return f"List must contain at most {expected} item(s)."
    if rule == "uniqueItems":
        return "List items must be unique."
    if rule in {"enum", "const", "pattern"}:
        return f"Value does not satisfy the schema {rule} rule."
    return f"Value does not satisfy the schema rule: {rule}."


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(_strings(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_strings(item))
        return result
    return []


def _looks_sensitive(value: str) -> bool:
    return (
        contains_sensitive_value(value) or _SENSITIVE_PREFIX.search(value) is not None
    )
