from __future__ import annotations

from pathlib import Path
from typing import Any

from pipe_venture_builder.adapters.hermes import HermesRunContext
from tests.control_plane.helpers import create_plan


BEGIN_AT = "2026-07-21T13:00:00Z"
EVENT_AT = "2026-07-21T13:01:00Z"
LATER_AT = "2026-07-21T13:02:00Z"
SESSION_ONE = "20260721_130000_abc123"
SESSION_TWO = "20260721_130200_def456"


def product_root(directory: Path) -> Path:
    root = directory / "product"
    (root / "product").mkdir(parents=True)
    (root / "product" / "prd.md").write_text("# PRD\n", encoding="utf-8")
    (root / "README.md").write_text("# Product\n", encoding="utf-8")
    return root


def context_for(root: Path, plan: dict[str, Any] | None = None) -> HermesRunContext:
    return HermesRunContext.build(
        product_id="example-product",
        linear_ticket_id="PIP-713",
        workflow="adopt",
        product_root=root,
        artifact_refs=["product/prd.md", "README.md"],
        plan=plan or create_plan(),
    )
