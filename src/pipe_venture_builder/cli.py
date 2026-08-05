"""Command-line entrypoint for the portable Pipe runtime foundation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from . import __version__
from .adopt import generate_product_baseline, write_product_baseline
from .bootstrap import BootstrapOptions, apply_bootstrap, plan_bootstrap
from .discovery import discover_project_root, resolve_baseline_schema
from .doctor import run_doctor
from .errors import PipeError
from .exit_codes import (
    INPUT_INVALID_JSON,
    INPUT_UNAVAILABLE,
    INTERNAL_CONTRACT_ERROR,
    READINESS_BLOCKED,
    SUCCESS,
)
from .tickets import check_conformance, load_registry, parse_ticket, render_ticket
from .tickets.handoff import HandoffTemplateError, load_handoff_template
from .tickets.matrix import BEGIN_MARKER, END_MARKER, emit_markdown_block
from .idea import generate_idea_baseline, write_idea_baseline
from .manifest import resolve_product_root, resolve_toolkit_root
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
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    version_parser = commands.add_parser(
        "version", help="Show the installed Pipe CLI version."
    )
    version_parser.add_argument("--json", action="store_true", dest="as_json")
    version_parser.set_defaults(handler=_handle_version)

    root_parser = commands.add_parser(
        "root", help="Find the nearest Pipe project root."
    )
    root_parser.add_argument(
        "start", nargs="?", default=None, help="Location to search from."
    )
    root_parser.add_argument("--json", action="store_true", dest="as_json")
    root_parser.set_defaults(handler=_handle_root)

    bootstrap_parser = commands.add_parser(
        "bootstrap",
        help="Plan or apply repository-local portable Pipe configuration.",
    )
    bootstrap_parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Product repository root. Defaults to the current directory.",
    )
    bootstrap_parser.add_argument("--product-id")
    bootstrap_parser.add_argument("--entry-mode", choices=("idea", "adopt"))
    bootstrap_parser.add_argument(
        "--runtime",
        choices=("hermes", "codex", "claude-code"),
    )
    bootstrap_parser.add_argument(
        "--fallback-runtime",
        action="append",
        dest="fallback_runtimes",
        choices=("hermes", "codex", "claude-code"),
    )
    bootstrap_parser.add_argument(
        "--capability",
        action="append",
        dest="capabilities",
    )
    bootstrap_parser.add_argument("--linear-project-id")
    bootstrap_parser.add_argument("--github-repository")
    bootstrap_parser.add_argument(
        "--toolkit-root",
        help="Versioned Pipe toolkit root. Defaults to local/package resolution.",
    )
    bootstrap_action = bootstrap_parser.add_mutually_exclusive_group()
    bootstrap_action.add_argument(
        "--plan",
        "--dry-run",
        action="store_const",
        const="plan",
        dest="bootstrap_action",
        help="Show the non-mutating plan (default).",
    )
    bootstrap_action.add_argument(
        "--apply",
        action="store_const",
        const="apply",
        dest="bootstrap_action",
        help="Create the reviewed repository-local manifest.",
    )
    bootstrap_parser.set_defaults(
        handler=_handle_bootstrap,
        bootstrap_action="plan",
    )
    bootstrap_parser.add_argument("--json", action="store_true", dest="as_json")

    doctor_parser = commands.add_parser(
        "doctor",
        help="Run read-only, redacted local Pipe readiness checks.",
    )
    doctor_parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Product repository root. Defaults to the current directory.",
    )
    doctor_parser.add_argument(
        "--toolkit-root",
        help="Versioned Pipe toolkit root. Defaults to local/package resolution.",
    )
    doctor_parser.add_argument("--json", action="store_true", dest="as_json")
    doctor_parser.set_defaults(handler=_handle_doctor)

    idea_parser = commands.add_parser(
        "idea",
        help="Generate a governed ProductBaseline from one brainstorm source.",
    )
    idea_parser.add_argument(
        "source", help="Approved Markdown or JSON brainstorm file."
    )
    idea_parser.add_argument(
        "--root",
        help="Pipe toolkit root used to resolve the canonical ProductBaseline schema.",
    )
    idea_output = idea_parser.add_mutually_exclusive_group(required=True)
    idea_output.add_argument(
        "--output",
        help="Write the baseline to a new file. Existing files are never replaced.",
    )
    idea_output.add_argument("--json", action="store_true", dest="as_json")
    idea_parser.set_defaults(handler=_handle_idea)

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

    baseline_parser = commands.add_parser(
        "baseline", help="Work with ProductBaseline artifacts."
    )
    baseline_commands = baseline_parser.add_subparsers(
        dest="baseline_command", required=True
    )
    validate_parser = baseline_commands.add_parser(
        "validate",
        help="Validate a ProductBaseline JSON artifact.",
    )
    validate_parser.add_argument(
        "baseline", help="ProductBaseline JSON file to validate."
    )
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

    # PIP-832 — contrato de ticket. Offline por construção: nenhum destes comandos
    # abre rede ou toca credencial, então rodam em CI e em pre-push sem gate.
    ticket_parser = commands.add_parser(
        "ticket", help="Work with the Pipe ticket contract."
    )
    ticket_commands = ticket_parser.add_subparsers(dest="ticket_command", required=True)

    ticket_check = ticket_commands.add_parser(
        "check",
        help="Check a ticket body against the required fields for its type.",
    )
    ticket_check.add_argument("body", help="Markdown file with the ticket body.")
    ticket_check.add_argument(
        "--type",
        dest="ticket_type",
        help="Override the Type field when the body does not declare one.",
    )
    ticket_check.add_argument("--json", action="store_true", dest="as_json")
    ticket_check.set_defaults(handler=_handle_ticket_check)

    ticket_render = ticket_commands.add_parser(
        "render",
        help="Render a ticket body from a JSON field map, in contract order.",
    )
    ticket_render.add_argument("fields", help="JSON file mapping field keys to content.")
    ticket_render.add_argument("--json", action="store_true", dest="as_json")
    ticket_render.set_defaults(handler=_handle_ticket_render)

    ticket_matrix = ticket_commands.add_parser(
        "matrix",
        help="Show the field matrix, or rewrite the generated block in the governance doc.",
    )
    ticket_matrix.add_argument(
        "--emit-markdown",
        action="store_true",
        dest="emit_markdown",
        help="Rewrite the generated block in execution/ticket-type-field-matrix.md.",
    )
    ticket_matrix.add_argument("--json", action="store_true", dest="as_json")
    ticket_matrix.set_defaults(handler=_handle_ticket_matrix)

    handoff_parser = commands.add_parser(
        "handoff", help="Work with the canonical delivery handoff."
    )
    handoff_commands = handoff_parser.add_subparsers(
        dest="handoff_command", required=True
    )
    handoff_render = handoff_commands.add_parser(
        "render",
        help="Render the canonical handoff block from execution/ticket-pr-handoff-system.md.",
    )
    handoff_render.add_argument(
        "--values",
        help="Optional JSON file mapping handoff labels to values.",
    )
    handoff_render.add_argument("--json", action="store_true", dest="as_json")
    handoff_render.set_defaults(handler=_handle_handoff_render)

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
        _render_error(
            internal_error, as_json=getattr(args, "as_json", False), stream=err
        )
        return internal_error.exit_code

    exit_code = int(payload.pop("_exit_code", SUCCESS))
    _render_success(payload, as_json=getattr(args, "as_json", False), stream=out)
    return exit_code


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


def _handle_bootstrap(args: argparse.Namespace) -> dict[str, Any]:
    product_root = resolve_product_root(args.target)
    toolkit_root = resolve_toolkit_root(args.toolkit_root, start=product_root)
    options = BootstrapOptions(
        product_id=args.product_id,
        entry_mode=args.entry_mode,
        runtime=args.runtime,
        fallback_runtimes=(
            tuple(args.fallback_runtimes)
            if args.fallback_runtimes is not None
            else None
        ),
        capabilities=(
            tuple(args.capabilities) if args.capabilities is not None else None
        ),
        linear_project_id=args.linear_project_id,
        github_repository=args.github_repository,
    )
    if args.bootstrap_action == "apply":
        result = apply_bootstrap(
            product_root,
            toolkit_root,
            pipe_version=__version__,
            options=options,
        )
        report = run_doctor(product_root, toolkit_root)
        return {
            "ok": report.is_ready,
            "command": "bootstrap",
            "mode": "apply",
            "manifestSchemaVersion": result.manifest["schemaVersion"],
            "result": result.as_dict(),
            "doctor": report.as_dict(),
            "message": (f"Bootstrap {result.action}. {report.human_summary()}"),
            "_exit_code": SUCCESS if report.is_ready else READINESS_BLOCKED,
        }

    result = plan_bootstrap(
        product_root,
        toolkit_root,
        pipe_version=__version__,
        options=options,
    )
    return {
        "ok": True,
        "command": "bootstrap",
        "mode": "plan",
        "manifestSchemaVersion": result.manifest["schemaVersion"],
        "result": result.as_dict(),
        "message": (
            "Bootstrap plan is unchanged; no files would be written."
            if result.action == "unchanged"
            else "Bootstrap plan prepared; no files were written. Review it before --apply."
        ),
    }


def _handle_doctor(args: argparse.Namespace) -> dict[str, Any]:
    product_root = resolve_product_root(args.target)
    toolkit_root = resolve_toolkit_root(args.toolkit_root, start=product_root)
    report = run_doctor(product_root, toolkit_root)
    return {
        "ok": report.is_ready,
        "command": "doctor",
        "status": report.status,
        "report": report.as_dict(),
        "message": report.human_summary(),
        "_exit_code": SUCCESS if report.is_ready else READINESS_BLOCKED,
    }


def _handle_idea(args: argparse.Namespace) -> dict[str, Any]:
    toolkit_root = resolve_toolkit_root(args.root)
    schema_path = resolve_baseline_schema(toolkit_root)
    schema = load_json_document(schema_path, kind="schema")
    baseline = generate_idea_baseline(args.source)
    findings = validate_product_baseline(baseline, schema)
    if findings:
        raise PipeError(
            code="GENERATED_IDEA_BASELINE_INVALID",
            message="Pipe generated an idea ProductBaseline that violates the canonical contract.",
            exit_code=INTERNAL_CONTRACT_ERROR,
            details=[finding.as_dict() for finding in findings[:50]],
        )
    if args.output:
        write_idea_baseline(args.output, baseline)
    return {
        "ok": True,
        "command": "idea",
        "schemaVersion": baseline["schemaVersion"],
        "baselineId": baseline["baselineId"],
        "baseline": baseline if args.as_json else None,
        "message": (
            "Idea ProductBaseline generated. Review is required before founder focus."
            if args.as_json
            else "Idea ProductBaseline written. Review is required before founder focus."
        ),
    }


def _handle_adopt(args: argparse.Namespace) -> dict[str, Any]:
    toolkit_root = resolve_toolkit_root(args.root)
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
    # Standalone validation preserves the original minimal-root contract;
    # idea/adopt consume the full PIP-709 toolkit surface.
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


def _read_text_input(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise PipeError(
            code="INPUT_UNAVAILABLE",
            message=f"Could not read {path}.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc


def _read_json_input(path: str) -> dict[str, Any]:
    raw = _read_text_input(path)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PipeError(
            code="INPUT_INVALID_JSON",
            message=f"{path} is not valid JSON.",
            exit_code=INPUT_INVALID_JSON,
        ) from exc
    if not isinstance(parsed, dict):
        raise PipeError(
            code="INPUT_INVALID_JSON",
            message=f"{path} must contain a JSON object.",
            exit_code=INPUT_INVALID_JSON,
        )
    return parsed


def _handle_ticket_check(args: argparse.Namespace) -> dict[str, Any]:
    body = _read_text_input(args.body)
    parsed = parse_ticket(body)
    if args.ticket_type:
        parsed.fields.setdefault("type", args.ticket_type)
    report = check_conformance(parsed)

    payload: dict[str, Any] = {"ok": report.ok, "command": "ticket.check"}
    payload.update(report.as_dict())
    if report.ok:
        payload["message"] = (
            f"Ticket conforms to the {report.ticket_type} contract."
            + (
                f" {len(report.unparsed)} unrecognised section(s) kept as-is."
                if report.unparsed
                else ""
            )
        )
        return payload

    problems = list(report.problems) + [
        f"missing required field: {item.heading}" for item in report.missing
    ]
    raise PipeError(
        code="TICKET_CONTRACT_VIOLATION",
        message=f"Ticket does not conform to the {report.ticket_type or 'unknown'} contract.",
        exit_code=READINESS_BLOCKED,
        details=[
            {"path": args.body, "message": problem, "rule": "ticket-field-matrix"}
            for problem in problems
        ],
    )


def _handle_ticket_render(args: argparse.Namespace) -> dict[str, Any]:
    fields = _read_json_input(args.fields)
    registry = load_registry()
    unknown = sorted(set(fields) - {field.key for field in registry.all_fields()})
    if unknown:
        raise PipeError(
            code="TICKET_UNKNOWN_FIELD",
            message="Field keys are not in the ticket contract.",
            exit_code=READINESS_BLOCKED,
            details=[
                {"path": args.fields, "message": key, "rule": "ticket-field-matrix"}
                for key in unknown
            ],
        )
    return {
        "ok": True,
        "command": "ticket.render",
        "body": render_ticket(fields, registry),
        "message": render_ticket(fields, registry),
    }


def _handle_ticket_matrix(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    block = emit_markdown_block(registry)
    if not args.emit_markdown:
        return {
            "ok": True,
            "command": "ticket.matrix",
            "types": list(registry.types),
            "message": block,
        }

    root = discover_project_root(None)
    doc = root / "execution/ticket-type-field-matrix.md"
    text = doc.read_text(encoding="utf-8")
    if BEGIN_MARKER not in text or END_MARKER not in text:
        raise PipeError(
            code="GENERATED_BLOCK_MISSING",
            message=f"{doc} has no generated field-matrix block to rewrite.",
            exit_code=READINESS_BLOCKED,
        )
    start = text.index(BEGIN_MARKER) + len(BEGIN_MARKER)
    end = text.index(END_MARKER)
    updated = text[:start] + "\n" + block + text[end:]
    changed = updated != text
    if changed:
        doc.write_text(updated, encoding="utf-8")
    return {
        "ok": True,
        "command": "ticket.matrix",
        "changed": changed,
        "message": (
            "Field matrix rewritten from contracts/ticket-field-matrix.json."
            if changed
            else "Field matrix already in sync."
        ),
    }


def _handle_handoff_render(args: argparse.Namespace) -> dict[str, Any]:
    template = load_handoff_template()
    values = _read_json_input(args.values) if args.values else None
    try:
        body = template.render(values)
    except HandoffTemplateError as exc:
        raise PipeError(
            code="HANDOFF_UNKNOWN_LABEL",
            message=str(exc),
            exit_code=READINESS_BLOCKED,
        ) from exc
    return {
        "ok": True,
        "command": "handoff.render",
        "body": body,
        "message": body,
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
        print(
            f"- {detail['path']}: {detail['message']} ({detail['rule']})", file=stream
        )
