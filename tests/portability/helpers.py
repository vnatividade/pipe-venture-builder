from __future__ import annotations

import json
from pathlib import Path
import subprocess

from pipe_venture_builder.bootstrap import BootstrapOptions, apply_bootstrap
from pipe_venture_builder.manifest import resolve_toolkit_root


TOOLKIT_ROOT = Path(__file__).resolve().parents[2]


def initialize_product_repository(root: Path, *, mode: bool = True) -> None:
    subprocess.run(
        ["git", "init", "--quiet", str(root)],
        check=True,
        capture_output=True,
        text=True,
    )
    if mode:
        pipe_directory = root / ".pipe"
        pipe_directory.mkdir(exist_ok=True)
        mode_payload = json.loads(
            (TOOLKIT_ROOT / ".pipe/mode.json").read_text(encoding="utf-8")
        )
        (pipe_directory / "mode.json").write_text(
            json.dumps(mode_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def bootstrap_product(root: Path, **overrides: object) -> dict[str, object]:
    options = BootstrapOptions(
        product_id=str(overrides.get("product_id", "portable-product")),
        entry_mode=str(overrides.get("entry_mode", "adopt")),
        runtime=str(overrides.get("runtime", "hermes")),
        fallback_runtimes=tuple(
            overrides.get("fallback_runtimes", ("codex", "claude-code"))
        ),
        capabilities=tuple(
            overrides.get("capabilities", ("capability.internal.atelier",))
        ),
        linear_project_id=overrides.get("linear_project_id"),
        github_repository=overrides.get("github_repository"),
    )
    result = apply_bootstrap(
        root,
        resolve_toolkit_root(TOOLKIT_ROOT),
        pipe_version="0.1.0",
        options=options,
    )
    return result.manifest
