"""Relatório de reconciliação em disco (PIP-834).

Mora em `~/.pipe/linear/`, **fora do git**: relatório é observação datada, não
artefato de fonte de verdade. Versionar transformaria cada execução em ruído de diff.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

REPORT_ROOT_ENV = "PIPE_LINEAR_REPORT_ROOT"


def report_root(environment: Mapping[str, str] | None = None) -> Path:
    env = environment if environment is not None else os.environ
    configured = env.get(REPORT_ROOT_ENV)
    return Path(configured).expanduser() if configured else Path.home() / ".pipe" / "linear"


def report_path(project_id: str, captured_at: str, environment: Mapping[str, str] | None = None) -> Path:
    # Timestamp no nome mantém o histórico sem banco: comparar duas execuções é `diff`.
    stamp = "".join(ch for ch in captured_at if ch.isdigit())
    safe_project = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in project_id)
    return report_root(environment) / f"{safe_project}-{stamp}.json"


def render_report(report: Mapping[str, Any]) -> str:
    """Resumo legível. O JSON completo vai para o arquivo; isto é o que cabe no terminal."""
    summary = report.get("summary", {})
    lines = [
        "Reconciliação Linear",
        f"  artefatos sem ticket:      {summary.get('coverageProposals', 0)}",
        f"  achados de ciclo de vida:  {summary.get('lifecycleFindings', 0)}"
        f" ({summary.get('lifecycleBlocking', 0)} bloqueantes)",
        f"  conformidade de corpo:     {summary.get('contractStatus')}",
        f"  bloqueios do plano:        {summary.get('blockers', 0)}",
    ]
    for finding in report.get("lifecycle", []):
        marker = "!" if finding.get("severity") == "blocking" else "-"
        lines.append(f"  {marker} {finding.get('sourceKey')}: {finding.get('rule')}")
    if report.get("contract", {}).get("status") == "unavailable":
        lines.append("")
        lines.append("  Conformidade de corpo NÃO foi verificada (não é o mesmo que estar em dia):")
        lines.append(f"  {report['contract'].get('reason')}")
    return "\n".join(lines)


def write_report(report: Mapping[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
