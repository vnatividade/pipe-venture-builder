"""Versioned ProductManifest constants."""

from pathlib import Path

MANIFEST_SCHEMA_VERSION = "0.1.0"
MANIFEST_RELATIVE_PATH = Path(".pipe/project.json")
MANIFEST_SCHEMA_RELATIVE_PATH = Path("schemas/ProductManifest.schema.json")
SUPPORTED_RUNTIMES = ("hermes", "codex", "claude-code")
DEFAULT_CAPABILITIES = ("capability.internal.atelier",)
DEFAULT_RUNTIME = "hermes"
DEFAULT_FALLBACK_RUNTIMES = ("codex", "claude-code")
