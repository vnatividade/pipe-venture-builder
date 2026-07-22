"""Deterministic human rendering for ReconciliationPlan values."""

from __future__ import annotations

from typing import Any, Mapping


def render_reconciliation_plan(plan: Mapping[str, Any]) -> str:
    """Render identifiers and fixed planner text without copying source content."""

    summary = plan["summary"]
    lines = [
        f"Reconciliation plan {plan['planId']} — {plan['status']}",
        (
            "Summary: "
            f"{summary['total']} action(s), {summary['proposed']} proposed, "
            f"{summary['blocked']} blocked, "
            f"{summary['alreadySatisfied']} already satisfied, "
            f"{summary['investigate']} investigate."
        ),
    ]
    if plan["actions"]:
        lines.append("Actions:")
        for action in plan["actions"]:
            source_ids = ",".join(action["sourceArtifactIds"])
            target_ids = ",".join(action["targetRecordIds"]) or "unresolved"
            lines.append(
                f"- {action['actionId']} [{action['status']}] "
                f"{action['actionType']} {action['targetSystem']} "
                f"source={source_ids} target={target_ids} "
                f"match={action['matchStrategy']}/{action['confidence']}"
            )
    if plan["blockers"]:
        lines.append("Blockers:")
        for blocker in plan["blockers"]:
            lines.append(
                f"- {blocker['blockerId']} [{blocker['severity']}] "
                f"{blocker['type']}: {blocker['description']}"
            )
    lines.append("No external mutation was performed; every action requires review.")
    return "\n".join(lines) + "\n"
