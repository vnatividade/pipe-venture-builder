"""Mission status: a JSON report and a short human summary in pt-BR.

The report answers "where are we, why, what depends on you" from durable
state only. It never includes the founder's intent text, prompts, or outputs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .store import MissionStore


SUPERVISOR_PID_FILE = "supervisor.pid"


def default_mission_home() -> Path:
    """Per-mission working directory root: ``~/.pipe/mission/<missionId>/``."""

    return Path.home() / ".pipe" / "mission"


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def supervisor_liveness(mission_id: str, home: Path | None = None) -> dict[str, Any]:
    """``{"alive": None}`` without a pid file; otherwise the pid and a probe."""

    root = Path(home) if home is not None else default_mission_home()
    pid_file = root / mission_id / SUPERVISOR_PID_FILE
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return {"alive": None}
    return {"alive": pid_is_alive(pid), "pid": pid}


def build_status(
    store: MissionStore, mission_id: str, *, home: Path | None = None
) -> dict[str, Any]:
    document = store.get(mission_id)
    runs = store.list_runs(mission_id)
    current = max(runs, key=lambda run: (run["cycle"], run["attempt"]), default=None)
    last = store.last_event(mission_id)
    return {
        "missionId": document["missionId"],
        "title": document["title"],
        "status": document["status"],
        "version": document["version"],
        "cycle": current["cycle"] if current else 0,
        "attempt": current["attempt"] if current else 0,
        "maxCycles": document["constraints"]["maxCycles"],
        "criteria": [
            {"id": item["id"], "kind": item["kind"], "satisfied": item["satisfied"]}
            for item in store.criteria_status(mission_id)
        ],
        "pendingDecisions": store.pending_decisions(mission_id),
        "costUsd": store.total_cost_usd(mission_id),
        "maxBudgetUsd": document["constraints"]["maxBudgetUsd"],
        "runs": store.run_counts(mission_id),
        "sessionIds": [run["session_id"] for run in runs if run["session_id"]],
        "lastEvent": (
            {
                "sequence": last["sequence"],
                "eventType": last["eventType"],
                "occurredAt": last["occurredAt"],
            }
            if last
            else None
        ),
        "auditChainValid": store.verify_chain(mission_id),
        "updatedAt": document["updatedAt"],
        "supervisor": supervisor_liveness(document["missionId"], home),
    }


def render_status_text(status: dict[str, Any]) -> str:
    satisfied = sum(1 for item in status["criteria"] if item["satisfied"])
    total = len(status["criteria"])
    where = (
        f"Onde estamos: missão {status['missionId']} \"{status['title']}\" está "
        f"{status['status']} (ciclo {status['cycle']}/{status['maxCycles']}, "
        f"tentativa {status['attempt']}); critérios {satisfied}/{total} satisfeitos; "
        f"custo US$ {status['costUsd']:.2f} de {status['maxBudgetUsd']:.2f}."
    )

    last = status["lastEvent"]
    why = (
        f"Por quê: último evento {last['eventType']} em {last['occurredAt']}."
        if last
        else "Por quê: nenhum evento registrado."
    )
    if not status["auditChainValid"]:
        why += " ATENÇÃO: cadeia de auditoria inválida; o supervisor não deve continuar."
    runs = status["runs"]
    if runs:
        why += " Runs: " + ", ".join(f"{count} {name}" for name, count in sorted(runs.items())) + "."

    pending = status["pendingDecisions"]
    if not pending:
        you = "O que depende de você: nada."
    else:
        plural = "decisão pendente" if len(pending) == 1 else "decisões pendentes"
        lines = [f"O que depende de você: {len(pending)} {plural}."]
        for decision in pending:
            options = ", ".join(decision["options"])
            deadline = f"; prazo: {decision['deadline']}" if decision["deadline"] else ""
            lines.append(
                f"  - {decision['decisionId']} [{decision['kind']}] bloqueia "
                f"{decision['blockedScope']}; opções: {options}; "
                f"padrão seguro: {decision['safeDefault']}{deadline}."
            )
        you = "\n".join(lines)
    return "\n".join((where, why, you))
