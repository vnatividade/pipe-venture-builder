"""Reconciliação Linear do Pipe (PIP-834): leitura, comparação e relatório. Sem mutação."""

from .lifecycle import LifecycleFinding, find_lifecycle_drift
from .reconciler import ReconciliationReport, reconcile
from .report import render_report, report_path

__all__ = [
    "LifecycleFinding",
    "ReconciliationReport",
    "find_lifecycle_drift",
    "reconcile",
    "render_report",
    "report_path",
]
