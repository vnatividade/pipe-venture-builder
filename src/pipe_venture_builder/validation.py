"""ProductBaseline JSON loading and Draft 2020-12 validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from .errors import PipeError
from .exit_codes import (
    BASELINE_INVALID,
    INPUT_INVALID_JSON,
    INPUT_UNAVAILABLE,
    INTERNAL_CONTRACT_ERROR,
)

MAX_VALIDATION_ERRORS = 50


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """A sanitized validation finding that never includes instance values."""

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


def load_json_document(path: str | Path, *, kind: str) -> Any:
    """Load JSON while reporting position but never echoing source contents."""

    document_path = Path(path).expanduser()
    try:
        with document_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise PipeError(
            code=f"{kind.upper()}_UNAVAILABLE",
            message=f"The {kind} file is unavailable.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
    except (PermissionError, OSError) as exc:
        raise PipeError(
            code=f"{kind.upper()}_UNAVAILABLE",
            message=f"The {kind} file could not be read.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
    except UnicodeDecodeError as exc:
        raise PipeError(
            code=f"{kind.upper()}_INVALID_JSON",
            message=f"The {kind} file is not UTF-8 JSON (byte {exc.start}).",
            exit_code=INPUT_INVALID_JSON,
        ) from exc
    except json.JSONDecodeError as exc:
        raise PipeError(
            code=f"{kind.upper()}_INVALID_JSON",
            message=f"The {kind} file is not valid JSON (line {exc.lineno}, column {exc.colno}).",
            exit_code=INPUT_INVALID_JSON,
        ) from exc


def validate_product_baseline(instance: Any, schema: Any) -> list[ValidationFinding]:
    """Return sanitized findings for *instance* against ProductBaseline *schema*."""

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise PipeError(
            code="BASELINE_SCHEMA_INVALID",
            message="The ProductBaseline schema is not a valid Draft 2020-12 contract.",
            exit_code=INTERNAL_CONTRACT_ERROR,
        ) from exc

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (_pointer(error.absolute_path), _pointer(error.absolute_schema_path)),
    )
    return [_sanitize_error(error) for error in errors]


def validate_product_baseline_files(
    baseline_path: str | Path,
    schema_path: str | Path,
) -> list[ValidationFinding]:
    """Load and validate a ProductBaseline and its canonical schema."""

    baseline = load_json_document(baseline_path, kind="baseline")
    schema = load_json_document(schema_path, kind="schema")
    return validate_product_baseline(baseline, schema)


def invalid_baseline_error(findings: Iterable[ValidationFinding]) -> PipeError:
    """Build the stable domain error returned for schema-invalid baselines."""

    all_findings = list(findings)
    details = [finding.as_dict() for finding in all_findings[:MAX_VALIDATION_ERRORS]]
    if len(all_findings) > MAX_VALIDATION_ERRORS:
        message = (
            f"ProductBaseline validation failed with {len(all_findings)} error(s); "
            f"showing the first {MAX_VALIDATION_ERRORS}."
        )
    else:
        message = f"ProductBaseline validation failed with {len(all_findings)} error(s)."
    return PipeError(
        code="BASELINE_INVALID",
        message=message,
        exit_code=BASELINE_INVALID,
        details=details,
    )


def _pointer(parts: Iterable[Any]) -> str:
    encoded = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(encoded) if encoded else "/"


def _sanitize_error(error: ValidationError) -> ValidationFinding:
    rule = str(error.validator or "schema")
    return ValidationFinding(
        path=_pointer(error.absolute_path),
        schema_path=_pointer(error.absolute_schema_path),
        rule=rule,
        message=_safe_message(error),
    )


def _safe_message(error: ValidationError) -> str:
    """Describe the failed rule using schema metadata, never the instance value."""

    rule = error.validator
    expected = error.validator_value

    if rule == "required":
        missing = [name for name in expected if not isinstance(error.instance, dict) or name not in error.instance]
        if len(missing) == 1:
            return f"Missing required property: {missing[0]}."
        return "One or more required properties are missing."
    if rule == "type":
        allowed = ", ".join(expected) if isinstance(expected, list) else str(expected)
        return f"Expected value type: {allowed}."
    if rule == "enum":
        return "Value is not one of the allowed schema values."
    if rule == "const":
        return "Value does not match the required schema constant."
    if rule == "format":
        return f"Value does not match required format: {expected}."
    if rule == "pattern":
        return "String does not match the required schema pattern."
    if rule == "minLength":
        return f"String is shorter than the minimum length of {expected}."
    if rule == "maxLength":
        return f"String is longer than the maximum length of {expected}."
    if rule == "minItems":
        return f"Array contains fewer than {expected} required item(s)."
    if rule == "maxItems":
        return f"Array contains more than {expected} allowed item(s)."
    if rule == "uniqueItems":
        return "Array items must be unique."
    if rule == "additionalProperties":
        return "One or more unexpected properties are not allowed."
    if rule == "oneOf":
        return "Value does not match exactly one allowed schema shape."
    if rule == "anyOf":
        return "Value does not match any allowed schema shape."
    if rule == "allOf":
        return "Value does not satisfy all required schema rules."
    return "Value does not satisfy the schema rule."
