"""Bounded, allowlist-first repository inventory."""

from __future__ import annotations

import json
import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE

from .safety import is_sensitive_path, read_allowlisted_text

APPROVED_METADATA_FILES = (
    "README.md",
    "README.rst",
    "README.txt",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
)
TEST_ROOT_NAMES = {"__tests__", "spec", "specs", "test", "tests"}
TEST_SUFFIXES = {
    ".cs",
    ".dart",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".svn",
    ".tox",
    ".venv",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
MAX_WALKED_ENTRIES = 10_000
MAX_TEST_FILES = 500


@dataclass(frozen=True, slots=True)
class MetadataDocument:
    relative_path: str
    kind: str
    product_name: str | None


@dataclass(frozen=True, slots=True)
class TestInventory:
    root: str
    file_count: int


@dataclass(frozen=True, slots=True)
class RepositoryInventory:
    root: Path
    product_name: str
    documents: tuple[MetadataDocument, ...]
    tests: tuple[TestInventory, ...]
    skipped_source_count: int
    traversal_truncated: bool


def inventory_repository(path: str | Path) -> RepositoryInventory:
    """Inspect only approved metadata and test-path names from a repository."""

    candidate = Path(path)
    try:
        root = candidate.resolve(strict=True)
    except (OSError, FileNotFoundError) as exc:
        raise PipeError(
            code="ADOPT_REPOSITORY_UNAVAILABLE",
            message="The adoption repository is unavailable.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
    if not root.is_dir():
        raise PipeError(
            code="ADOPT_REPOSITORY_UNAVAILABLE",
            message="The adoption repository must be a directory.",
            exit_code=INPUT_UNAVAILABLE,
        )

    documents: list[MetadataDocument] = []
    skipped = 0
    metadata_bounded = False
    for filename in APPROVED_METADATA_FILES:
        source = root / filename
        if not source.exists():
            continue
        result = read_allowlisted_text(source)
        if result.status == "bounded":
            metadata_bounded = True
            continue
        if result.status != "safe" or result.text is None:
            skipped += 1
            continue
        documents.append(
            MetadataDocument(
                relative_path=filename,
                kind=_document_kind(filename),
                product_name=_extract_product_name(filename, result.text),
            )
        )

    tests, skipped_tests, truncated = _inventory_tests(root)
    skipped += skipped_tests
    product_name = next(
        (document.product_name for document in documents if document.product_name),
        None,
    )
    if not product_name:
        product_name = (
            root.name if not is_sensitive_path(Path(root.name)) else "Adopted Product"
        )
    product_name = _safe_display_name(product_name) or "Adopted Product"

    return RepositoryInventory(
        root=root,
        product_name=product_name,
        documents=tuple(
            sorted(documents, key=lambda item: item.relative_path.casefold())
        ),
        tests=tuple(sorted(tests, key=lambda item: item.root.casefold())),
        skipped_source_count=skipped,
        traversal_truncated=truncated or metadata_bounded,
    )


def _inventory_tests(root: Path) -> tuple[list[TestInventory], int, bool]:
    counts: dict[str, int] = {}
    skipped = 0
    walked = 0
    truncated = False

    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        relative = current_path.relative_to(root)
        depth = len(relative.parts)
        if depth >= 6:
            directory_names[:] = []
        else:
            kept_directories = []
            for name in sorted(directory_names):
                if name in IGNORED_DIRECTORIES:
                    continue
                relative_child = relative / name
                if is_sensitive_path(relative_child):
                    skipped += 1
                    continue
                kept_directories.append(name)
            directory_names[:] = kept_directories

        walked += len(directory_names) + len(file_names)
        if walked > MAX_WALKED_ENTRIES:
            truncated = True
            break

        test_root = _test_root_for(relative)
        if test_root is None:
            continue
        for name in sorted(file_names):
            relative_file = relative / name
            if is_sensitive_path(relative_file):
                skipped += 1
                continue
            if Path(name).suffix.lower() not in TEST_SUFFIXES:
                continue
            counts[test_root] = counts.get(test_root, 0) + 1
            if sum(counts.values()) >= MAX_TEST_FILES:
                truncated = True
                break
        if truncated:
            break

    return (
        [TestInventory(key, value) for key, value in counts.items()],
        skipped,
        truncated,
    )


def _test_root_for(relative: Path) -> str | None:
    for index, part in enumerate(relative.parts):
        if part.lower() in TEST_ROOT_NAMES:
            return Path(*relative.parts[: index + 1]).as_posix() + "/"
    return None


def _document_kind(filename: str) -> str:
    return "readme" if filename.lower().startswith("readme") else "package_metadata"


def _extract_product_name(filename: str, text: str) -> str | None:
    lowered = filename.lower()
    try:
        if lowered == "pyproject.toml":
            value = tomllib.loads(text).get("project", {}).get("name")
            return _safe_display_name(value) if isinstance(value, str) else None
        if lowered == "cargo.toml":
            value = tomllib.loads(text).get("package", {}).get("name")
            return _safe_display_name(value) if isinstance(value, str) else None
        if lowered == "package.json":
            value = json.loads(text).get("name")
            return _safe_display_name(value) if isinstance(value, str) else None
        if lowered == "go.mod":
            match = re.search(r"(?m)^\s*module\s+([^\s]+)", text)
            return (
                _safe_display_name(match.group(1).rsplit("/", 1)[-1]) if match else None
            )
        if lowered.startswith("readme"):
            match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
            return _safe_display_name(match.group(1)) if match else None
    except (ValueError, TypeError, tomllib.TOMLDecodeError, json.JSONDecodeError):
        return None
    return None


def _safe_display_name(value: str) -> str | None:
    compact = " ".join(value.strip().split())
    if not compact or len(compact) > 120:
        return None
    if is_sensitive_path(Path(compact)):
        return None
    if not re.fullmatch(r"[\w .@/+-]+", compact, flags=re.UNICODE):
        return None
    return compact
