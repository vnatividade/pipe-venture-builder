#!/usr/bin/env python3
"""Local, fixture-only Hermes/Pipe start-block-resume smoke path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from pipe_venture_builder.adapters.hermes import (
    HermesCheckpointStore,
    HermesRunContext,
    HermesRuntimeAdapter,
    HermesRuntimeEvent,
)
from pipe_venture_builder.adapters.hermes.probe import probe_hermes
from pipe_venture_builder.control_plane import LocalControlPlaneStore


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-runtime-probe", action="store_true")
    args = parser.parse_args()
    runtime = (
        {"available": None, "compatible": None, "reason": "probe_skipped"}
        if args.skip_runtime_probe
        else probe_hermes()
    )
    if not args.skip_runtime_probe and not runtime["compatible"]:
        print(json.dumps({"ok": False, "runtime": runtime}, sort_keys=True))
        return 8

    toolkit_root = Path(__file__).resolve().parents[2]
    plan = json.loads(
        (toolkit_root / "integrations/hermes/fixtures/reconciliation-plan.json").read_text(
            encoding="utf-8"
        )
    )
    with TemporaryDirectory(prefix="pipe-hermes-smoke-") as directory:
        state = Path(directory)
        with LocalControlPlaneStore(state / "control-plane.sqlite3") as control:
            checkpoints = HermesCheckpointStore(state / "hermes-checkpoints")
            adapter = HermesRuntimeAdapter(control, checkpoints)
            context = HermesRunContext.build(
                product_id="hermes-smoke",
                linear_ticket_id="PIP-713",
                workflow="adopt",
                product_root=toolkit_root,
                artifact_refs=[
                    "README.md",
                    "integrations/hermes/fixtures/reconciliation-plan.json",
                ],
                plan=plan,
            )
            started = adapter.begin(
                plan=plan,
                context=context,
                session_id="20260721_130000_abc123",
                external_event_id="smoke-begin-1",
                occurred_at="2026-07-21T13:00:00Z",
            )
            blocked = adapter.record_event(
                started["runId"],
                HermesRuntimeEvent.build(
                    external_event_id="smoke-unavailable-1",
                    kind="runtime.unavailable",
                    session_id="20260721_130000_abc123",
                    occurred_at="2026-07-21T13:01:00Z",
                ),
            )
            resumed = adapter.resume(
                run_id=started["runId"],
                session_id="20260721_130200_def456",
                external_event_id="smoke-resume-1",
                occurred_at="2026-07-21T13:02:00Z",
            )
            audit_valid = control.verify_audit_chain(started["runId"])
            result = {
                "ok": (
                    started["state"] == "running"
                    and blocked["state"] == "runtime_blocked"
                    and resumed["state"] == "running"
                    and resumed["attempt"] == 2
                    and audit_valid
                ),
                "runtime": runtime,
                "startedState": started["state"],
                "blockedState": blocked["state"],
                "resumedState": resumed["state"],
                "attempt": resumed["attempt"],
                "auditChainValid": audit_valid,
                "externalMutationPerformed": False,
            }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["ok"] else 9


if __name__ == "__main__":
    raise SystemExit(main())
