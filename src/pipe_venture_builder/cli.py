"""Command-line entrypoint for the portable Pipe runtime foundation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from . import __version__
from .discovery import discover_project_root, resolve_baseline_schema
from .errors import PipeError
from .exit_codes import INTERNAL_CONTRACT_ERROR, SUCCESS
from .validation import (
    invalid_baseline_error,
    validate_product_baseline_files,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipe",
        description="Governed AI product delivery from idea or existing product context.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    version_parser = commands.add_parser("version", help="Show the installed Pipe CLI version.")
    version_parser.add_argument("--json", action="store_true", dest="as_json")
    version_parser.set_defaults(handler=_handle_version)

    root_parser = commands.add_parser("root", help="Find the nearest Pipe project root.")
    root_parser.add_argument("start", nargs="?", default=None, help="Location to search from.")
    root_parser.add_argument("--json", action="store_true", dest="as_json")
    root_parser.set_defaults(handler=_handle_root)

    baseline_parser = commands.add_parser("baseline", help="Work with ProductBaseline artifacts.")
    baseline_commands = baseline_parser.add_subparsers(dest="baseline_command", required=True)
    validate_parser = baseline_commands.add_parser(
        "validate",
        help="Validate a ProductBaseline JSON artifact.",
    )
    validate_parser.add_argument("baseline", help="ProductBaseline JSON file to validate.")
    validate_parser.add_argument(
        "--root",
        help="Pipe repository root or a location inside it. Defaults to the current directory.",
    )
    validate_parser.add_argument(
        "--schema",
        help="Schema path, absolute or relative to the discovered Pipe root.",
    )
    validate_parser.add_argument("--json", action="store_true", dest="as_json")
    validate_parser.set_defaults(handler=_handle_baseline_validate)

    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI and return a stable exit code."""

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = args.handler(args)
    except PipeError as exc:
        _render_error(exc, as_json=getattr(args, "as_json", False), stream=err)
        return exc.exit_code
    except Exception:
        internal_error = PipeError(
            code="INTERNAL_ERROR",
            message="Pipe stopped after an unexpected internal error.",
            exit_code=INTERNAL_CONTRACT_ERROR,
        )
        _render_error(internal_error, as_json=getattr(args, "as_json", False), stream=err)
        return internal_error.exit_code

    _render_success(payload, as_json=getattr(args, "as_json", False), stream=out)
    return SUCCESS


def _handle_version(_args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ok": True,
        "command": "version",
        "version": __version__,
        "message": f"pipe {__version__}",
    }


def _handle_root(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root(args.start)
    return {
        "ok": True,
        "command": "root",
        "root": str(root),
        "message": str(root),
    }


def _handle_baseline_validate(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root(args.root)
    schema_path = resolve_baseline_schema(root, args.schema)
    findings = validate_product_baseline_files(args.baseline, schema_path)
    if findings:
        raise invalid_baseline_error(findings)
    return {
        "ok": True,
        "command": "baseline.validate",
        "schemaVersion": "0.1.0",
        "message": "ProductBaseline is valid.",
    }


def _render_success(payload: dict[str, Any], *, as_json: bool, stream: TextIO) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True), file=stream)
    else:
        print(payload["message"], file=stream)


def _render_error(error: PipeError, *, as_json: bool, stream: TextIO) -> None:
    payload = {
        "ok": False,
        "code": error.code,
        "exitCode": error.exit_code,
        "message": error.message,
        "errors": error.details,
    }
    if as_json:
        print(json.dumps(payload, sort_keys=True), file=stream)
        return

    print(f"Error [{error.code}]: {error.message}", file=stream)
    for detail in error.details:
        print(f"- {detail['path']}: {detail['message']} ({detail['rule']})", file=stream)
