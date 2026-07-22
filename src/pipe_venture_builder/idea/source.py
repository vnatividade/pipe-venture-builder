"""Safe deterministic ingestion for Markdown and JSON brainstorm sources."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import (
    BASELINE_INVALID,
    INPUT_INVALID_JSON,
    INPUT_UNAVAILABLE,
)
from pipe_venture_builder.inventory.safety import read_allowlisted_text

from .ids import digest

MAX_FIELD_LENGTH = 2_000
MAX_LIST_ITEMS = 20
SUPPORTED_SUFFIXES = {".json", ".markdown", ".md"}

FIELD_ALIASES = {
    "name": {
        "idea name",
        "name",
        "nome",
        "nome da ideia",
        "nome do produto",
        "product name",
    },
    "summary": {"idea", "ideia", "raw idea", "resumo", "summary"},
    "target_user": {
        "audiencia",
        "persona",
        "publico alvo",
        "target market",
        "target user",
        "usuario alvo",
    },
    "problem": {"main problem", "problema", "problem"},
    "promise": {
        "desired result",
        "promessa",
        "promise",
        "resultado desejado",
        "resultado esperado",
    },
    "mechanism": {"mechanism", "mecanismo", "proposed solution", "solucao", "solution"},
    "channel": {"canal", "channel", "primary channel", "primeiro canal"},
    "solution_path": {"caminho da solucao", "path", "solution path"},
    "assumptions": {"assumptions", "hipoteses", "suposicoes"},
    "unknowns": {"duvidas", "open questions", "perguntas em aberto", "unknowns"},
    "evidence_claims": {"evidence", "evidencias", "evidence claims", "provas"},
}

_ALIAS_TO_FIELD = {
    alias: field for field, aliases in FIELD_ALIASES.items() for alias in aliases
}
_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_PHONE_CANDIDATE = re.compile(r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
_CUSTOMER_FIELD = re.compile(
    r"(?im)^\s*(?:customer|cliente|prospect|respondent|entrevistad[oa])\s*"
    r"(?:name|nome|email|e-mail|phone|telefone|id|identifier|identificador)\s*[:=]"
)
_NUMBERED_PRODUCT_HEADING = re.compile(r"^(?:idea|product|produto)\s+\d+\b")


@dataclass(frozen=True, slots=True)
class IdeaSource:
    source_name: str
    source_digest: str
    source_type: str
    name: str | None
    summary: str | None
    target_user: str | None
    problem: str | None
    promise: str | None
    mechanism: str | None
    channel: str | None
    solution_path: str | None
    assumptions: tuple[str, ...]
    unknowns: tuple[str, ...]
    evidence_claims: tuple[str, ...]


def load_idea_source(path: str | Path) -> IdeaSource:
    candidate = Path(path)
    if candidate.is_symlink():
        raise _source_error(
            "IDEA_SOURCE_BLOCKED",
            "The brainstorm source was blocked by the sensitive-data or bounded-input policy.",
        )
    try:
        source = candidate.resolve(strict=True)
    except (OSError, FileNotFoundError) as exc:
        raise _source_error(
            "IDEA_SOURCE_UNAVAILABLE", "The brainstorm source is unavailable."
        ) from exc
    if not source.is_file() or source.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise _source_error(
            "IDEA_SOURCE_UNSUPPORTED",
            "The brainstorm source must be one Markdown or JSON file.",
        )
    if _contains_personal_or_customer_data(source.name):
        raise _source_error(
            "IDEA_SOURCE_BLOCKED",
            "The brainstorm source filename appears to contain personal or customer data and was not ingested.",
        )

    safe_text = read_allowlisted_text(source)
    if safe_text.status != "safe" or safe_text.text is None:
        raise _source_error(
            "IDEA_SOURCE_BLOCKED",
            "The brainstorm source was blocked by the sensitive-data or bounded-input policy.",
        )
    if _contains_personal_or_customer_data(safe_text.text):
        raise _source_error(
            "IDEA_SOURCE_BLOCKED",
            "The brainstorm source appears to contain personal or customer data and was not ingested.",
        )

    fields = (
        _parse_json(safe_text.text)
        if source.suffix.lower() == ".json"
        else _parse_markdown(safe_text.text)
    )
    return IdeaSource(
        source_name=source.name,
        source_digest=digest(safe_text.text),
        source_type="brainstorm",
        name=_single(fields, "name"),
        summary=_single(fields, "summary"),
        target_user=_single(fields, "target_user"),
        problem=_single(fields, "problem"),
        promise=_single(fields, "promise"),
        mechanism=_single(fields, "mechanism"),
        channel=_single(fields, "channel"),
        solution_path=_single(fields, "solution_path"),
        assumptions=tuple(fields.get("assumptions", ())),
        unknowns=tuple(fields.get("unknowns", ())),
        evidence_claims=tuple(fields.get("evidence_claims", ())),
    )


def _parse_json(text: str) -> dict[str, tuple[str, ...]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PipeError(
            code="IDEA_SOURCE_INVALID_JSON",
            message=f"The brainstorm source is not valid JSON (line {exc.lineno}, column {exc.colno}).",
            exit_code=INPUT_INVALID_JSON,
        ) from exc

    payload = _unwrap_single_product(payload)
    if not isinstance(payload, dict):
        raise _source_error(
            "IDEA_SOURCE_INVALID",
            "The brainstorm JSON must contain one product object.",
            invalid=True,
        )

    result: dict[str, tuple[str, ...]] = {}
    for key, value in payload.items():
        field = _ALIAS_TO_FIELD.get(_normalize_heading(str(key)))
        if field is None:
            continue
        values = _coerce_values(value)
        if (
            field not in {"assumptions", "unknowns", "evidence_claims"}
            and len(values) > 1
        ):
            raise _multiple_products_error()
        if values:
            result[field] = values
    return result


def _unwrap_single_product(payload: Any) -> Any:
    if isinstance(payload, list):
        if len(payload) > 1:
            raise _multiple_products_error()
        if not payload:
            raise _source_error(
                "IDEA_SOURCE_INVALID",
                "The brainstorm source does not contain a product idea.",
                invalid=True,
            )
        return payload[0]
    if not isinstance(payload, dict):
        return payload
    for wrapper in ("ideas", "products", "ideias", "produtos"):
        value = payload.get(wrapper)
        if value is None:
            continue
        if not isinstance(value, list) or len(value) != 1:
            if isinstance(value, list) and len(value) > 1:
                raise _multiple_products_error()
            raise _source_error(
                "IDEA_SOURCE_INVALID",
                "The brainstorm collection must contain exactly one product idea.",
                invalid=True,
            )
        return value[0]
    return payload


def _parse_markdown(text: str) -> dict[str, tuple[str, ...]]:
    sections: dict[str, list[str]] = {}
    headings: list[tuple[int, str]] = []
    current_field: str | None = None
    in_fence = False

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^(#{1,3})\s+(.+?)\s*$", stripped)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            headings.append((level, title))
            normalized = _normalize_heading(title)
            current_field = _ALIAS_TO_FIELD.get(normalized)
            if level == 1 and current_field is None:
                sections.setdefault("name", []).append(title)
            continue
        if current_field and stripped:
            sections.setdefault(current_field, []).append(stripped)

    top_level_names = [title for level, title in headings if level == 1]
    numbered_product_headings = [
        title
        for _level, title in headings
        if _NUMBERED_PRODUCT_HEADING.match(_normalize_heading(title))
    ]
    if len(top_level_names) > 1 or len(numbered_product_headings) > 1:
        raise _multiple_products_error()

    result: dict[str, tuple[str, ...]] = {}
    list_fields = {"assumptions", "unknowns", "evidence_claims"}
    for field, lines in sections.items():
        cleaned = [_clean_value(re.sub(r"^[-*+]\s+", "", line)) for line in lines]
        cleaned = [value for value in cleaned if value]
        if not cleaned:
            continue
        if field in list_fields:
            result[field] = tuple(_deduplicate(cleaned[:MAX_LIST_ITEMS]))
        else:
            combined = _clean_value(" ".join(cleaned))
            if combined:
                result[field] = (combined,)
    return result


def _coerce_values(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        cleaned = _clean_value(value)
        return (cleaned,) if cleaned else ()
    if isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            raise _source_error(
                "IDEA_SOURCE_TOO_COMPLEX",
                "The brainstorm source contains too many values for one field.",
                invalid=True,
            )
        cleaned = [_clean_value(item) for item in value if isinstance(item, str)]
        return tuple(_deduplicate([item for item in cleaned if item]))
    if value is None:
        return ()
    raise _source_error(
        "IDEA_SOURCE_INVALID",
        "Brainstorm fields must contain text or lists of text.",
        invalid=True,
    )


def _clean_value(value: str) -> str:
    compact = " ".join(value.strip().split())
    if len(compact) > MAX_FIELD_LENGTH:
        raise _source_error(
            "IDEA_SOURCE_TOO_COMPLEX",
            "A brainstorm field exceeds the bounded input limit.",
            invalid=True,
        )
    return compact


def _single(fields: dict[str, tuple[str, ...]], name: str) -> str | None:
    values = fields.get(name, ())
    return values[0] if values else None


def _normalize_heading(value: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    normalized = re.sub(r"[^a-zA-Z0-9]+", " ", normalized).strip().lower()
    return normalized


def _contains_personal_or_customer_data(text: str) -> bool:
    if _EMAIL.search(text) or _CUSTOMER_FIELD.search(text):
        return True
    return any(
        len(re.sub(r"\D", "", match.group(0))) >= 10
        for match in _PHONE_CANDIDATE.finditer(text)
    )


def _deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _multiple_products_error() -> PipeError:
    return _source_error(
        "IDEA_MULTIPLE_PRODUCTS",
        "The brainstorm describes multiple products. Split it into one source per product before running pipe idea.",
        invalid=True,
    )


def _source_error(code: str, message: str, *, invalid: bool = False) -> PipeError:
    return PipeError(
        code=code,
        message=message,
        exit_code=BASELINE_INVALID if invalid else INPUT_UNAVAILABLE,
    )
