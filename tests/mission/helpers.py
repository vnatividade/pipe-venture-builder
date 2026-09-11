"""Fixtures for the Mission Loop tests. No network, no secrets, no real repo."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from tests.helpers import REPOSITORY_ROOT

MISSION_SCHEMA = REPOSITORY_ROOT / "schemas/Mission.schema.json"
CREATED_AT = "2026-09-10T22:00:00Z"
LATER = "2026-09-10T23:00:00Z"
EVEN_LATER = "2026-09-11T00:00:00Z"


def load_mission_schema() -> dict[str, Any]:
    return json.loads(MISSION_SCHEMA.read_text(encoding="utf-8"))


def mission_input() -> dict[str, Any]:
    """A founder-authored Mission draft, before ids and fingerprint exist."""

    return {
        "schemaVersion": "0.1.0",
        "version": 1,
        "supersedes": None,
        "title": "Docs param de contradizer o codigo",
        "intent": "As docs do Pipe descrevem o que o codigo faz hoje.",
        "problem": "README e catalogo dizem que nao ha CLI.",
        "who": "Fundador e agentes que leem o repositorio.",
        "successCriteria": [
            {
                "id": "C1",
                "text": "README nao diz que idea/adopt sao follow-up",
                "kind": "check",
                "command": "! grep -n 'remain follow-up' README.md",
                "cwd": ".",
            },
            {
                "id": "C2",
                "text": "catalogo de comandos existe e cita o CLI",
                "kind": "artifact",
                "path": "execution/pipe-command-catalog.md",
                "mustMatch": "pipe (idea|adopt)",
            },
            {
                "id": "C3",
                "text": "texto novo afirma so o que o codigo mostra",
                "kind": "rubric",
                "question": "O texto novo afirma apenas o que o codigo mostra?",
            },
        ],
        "nonGoals": ["Alterar CLAUDE.md ou AGENTS.md"],
        "delegable": ["Editar os seis arquivos Markdown do write set"],
        "reservedToHuman": ["Merge do PR"],
        "constraints": {
            "maxCycles": 3,
            "maxBudgetUsd": 15,
            "maxTurnsPerRun": 60,
            "productionAllowed": False,
            "secretsAllowed": False,
            "externalCommsAllowed": False,
            "billingAllowed": False,
        },
        "workspace": {
            "repo": "/private/tmp/pipe-mission-loop",
            "baseRef": "origin/main",
            "writeSet": ["README.md", "execution/pipe-command-catalog.md"],
        },
        "delivery": {"kind": "pull_request", "requireChecks": True},
        "linearTicketIds": ["PIP-901"],
    }


def mission_variant(**overrides: Any) -> dict[str, Any]:
    document = copy.deepcopy(mission_input())
    document.update(overrides)
    return document


def write_json(path: Path, value: Any) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path
