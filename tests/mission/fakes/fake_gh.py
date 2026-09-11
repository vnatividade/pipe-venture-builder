#!/usr/bin/env python3
"""A stand-in for ``gh`` covering ``pr list``, ``pr create`` and ``pr checks``.

State lives in FAKE_GH_STATE_DIR:
  prs.json      list of {"number", "url", "headRefName", "title", "state"}
  checks.json   list of per-call bucket lists, e.g. [["pending"], ["pass", "pass"]];
                consumed in order by ``pr checks`` (last entry reused)
  checks.count  call counter for ``pr checks``
  pr-<n>-body.md  the body handed to ``pr create``
  gh.log        one JSON line (argv) per invocation
Exit codes mirror gh: ``pr checks`` exits 8 while pending and 1 when something failed.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _flag(argv: list[str], name: str) -> str | None:
    if name in argv:
        index = argv.index(name)
        if index + 1 < len(argv):
            return argv[index + 1]
    return None


def main(argv: list[str]) -> int:
    state = Path(os.environ.get("FAKE_GH_STATE_DIR", "."))
    state.mkdir(parents=True, exist_ok=True)
    with open(state / "gh.log", "a", encoding="utf-8") as handle:
        handle.write(json.dumps(argv) + "\n")
    prs_path = state / "prs.json"
    prs = json.loads(prs_path.read_text(encoding="utf-8")) if prs_path.exists() else []

    if argv[:2] == ["pr", "list"]:
        head = _flag(argv, "--head")
        wanted_state = _flag(argv, "--state") or "open"
        matching = [
            pr for pr in prs
            if (head is None or pr["headRefName"] == head)
            and (wanted_state == "all" or pr["state"] == wanted_state)
        ]
        fields = (_flag(argv, "--json") or "number,url").split(",")
        sys.stdout.write(json.dumps([{key: pr[key] for key in fields if key in pr} for pr in matching]))
        return 0

    if argv[:2] == ["pr", "create"]:
        number = len(prs) + 1
        body_file = _flag(argv, "--body-file")
        body = Path(body_file).read_text(encoding="utf-8") if body_file else (_flag(argv, "--body") or "")
        (state / f"pr-{number}-body.md").write_text(body, encoding="utf-8")
        pr = {
            "number": number,
            "url": f"https://github.example/owner/repo/pull/{number}",
            "headRefName": _flag(argv, "--head") or "",
            "baseRefName": _flag(argv, "--base") or "",
            "title": _flag(argv, "--title") or "",
            "state": "open",
        }
        prs.append(pr)
        prs_path.write_text(json.dumps(prs), encoding="utf-8")
        sys.stdout.write(pr["url"] + "\n")
        return 0

    if argv[:2] == ["pr", "checks"]:
        checks_path = state / "checks.json"
        sequence = json.loads(checks_path.read_text(encoding="utf-8")) if checks_path.exists() else [[]]
        counter = state / "checks.count"
        index = int(counter.read_text()) if counter.exists() else 0
        counter.write_text(str(index + 1))
        buckets = sequence[min(index, len(sequence) - 1)] if sequence else []
        checks = [
            {"name": f"check-{position}", "bucket": bucket, "state": bucket.upper()}
            for position, bucket in enumerate(buckets, start=1)
        ]
        sys.stdout.write(json.dumps(checks))
        if any(bucket in ("fail", "cancel") for bucket in buckets):
            return 1
        if any(bucket == "pending" for bucket in buckets):
            return 8
        return 0

    sys.stderr.write("fake gh: unsupported command\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
