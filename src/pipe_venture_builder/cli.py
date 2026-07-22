"""Command-line entrypoint for the portable Pipe runtime foundation."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Sequence, TextIO

from . import __version__
from .adopt import generate_product_baseline, write_product_baseline
from .discovery import discover_project_root, resolve_baseline_schema
from .errors import PipeError
from .exit_codes import INTERNAL_CONTRACT_ERROR, SUCCESS
from .validation import (
    invalid_baseline_error,
    load_json_document,
    validate_product_baseline,
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

    adopt_parser = commands.add_parser(
        "adopt",
        help="Generate a safe ProductBaseline from a local repository.",
    )
    adopt_parser.add_argument(
        "repository",
        nargs="?",
        default=".",
        help="Existing product repository to inventory. Defaults to the current directory.",
    )
    adopt_parser.add_argument(
        "--root",
        help="Pipe toolkit root used to resolve the canonical ProductBaseline schema.",
    )
    adopt_output = adopt_parser.add_mutually_exclusive_group(required=True)
    adopt_output.add_argument(
        "--output",
        help="Write the baseline to a new file. Existing files are never replaced.",
    )
    adopt_output.add_argument("--json", action="store_true", dest="as_json")
    adopt_parser.set_defaults(handler=_handle_adopt)

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


def _handle_adopt(args: argparse.Namespace) -> dict[str, Any]:
    toolkit_root = discover_project_root(args.root)
    schema_path = resolve_baseline_schema(toolkit_root)
    schema = load_json_document(schema_path, kind="schema")
    baseline = generate_product_baseline(args.repository)
    findings = validate_product_baseline(baseline, schema)
    if findings:
        raise PipeError(
            code="GENERATED_BASELINE_INVALID",
            message="Pipe generated a ProductBaseline that violates the canonical contract.",
            exit_code=INTERNAL_CONTRACT_ERROR,
            details=[finding.as_dict() for finding in findings[:50]],
        )
    if args.output:
        write_product_baseline(args.output, baseline)
    return {
        "ok": True,
        "command": "adopt",
        "schemaVersion": baseline["schemaVersion"],
        "baselineId": baseline["baselineId"],
        "baseline": baseline if args.as_json else None,
        "message": (
            "ProductBaseline generated. Review is required before downstream routing."
            if args.as_json
            else "ProductBaseline written. Review is required before downstream routing."
        ),
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
