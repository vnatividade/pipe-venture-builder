#!/usr/bin/env python3
"""A stand-in for the ``claude`` binary, driven by a JSON scenario file.

Environment:
  FAKE_CLAUDE_SCENARIO  path to a JSON file: {"worker": [call, ...], "reviewer": [call, ...]}
                        A call is a mapping with optional keys:
                          sleep (s), on_sigterm ("exit"|"ignore"), mode ("json"|"garbage"|"silent"),
                          exit_code, result (overrides for the Claude result JSON),
                          worker_output (dict rendered inside ``result``), wrap ("none"|"text"|"fence"),
                          structured_output (reviewer verdict), write_files ({relpath: content}),
                          git_mv ([source, destination]), git_commit (message),
                          git_config ({key: value}, run as ``git config`` in cwd),
                          git_checkout (new branch name, ``git checkout -b`` in cwd),
                          spawn_grandchild ({"pid_file": path, "ignore_term": bool}: start a
                          sleeping child in the fake's process group and write its pid)
                        The reviewer role is detected by ``--json-schema`` in argv. When a role's
                        list is exhausted the last call is reused.
  FAKE_CLAUDE_STATE_DIR where per-role call counters live (defaults to the scenario's directory).
  FAKE_CLAUDE_LOG       JSON-lines file receiving one record per invocation (argv, cwd, stdin).

Never talks to a network. Never reads a secret.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def _stdin_is_devnull() -> bool:
    try:
        return os.fstat(0).st_rdev == os.stat(os.devnull).st_rdev
    except OSError:
        return False


def _next_call(role: str) -> dict:
    scenario_path = os.environ.get("FAKE_CLAUDE_SCENARIO")
    if not scenario_path:
        return {}
    scenario = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
    calls = scenario.get(role) or [{}]
    state_dir = Path(os.environ.get("FAKE_CLAUDE_STATE_DIR") or Path(scenario_path).parent)
    counter = state_dir / f"{role}.count"
    index = int(counter.read_text()) if counter.exists() else 0
    counter.write_text(str(index + 1))
    return calls[min(index, len(calls) - 1)]


def main(argv: list[str]) -> int:
    role = "reviewer" if "--json-schema" in argv else "worker"
    call = _next_call(role)

    log_path = os.environ.get("FAKE_CLAUDE_LOG")
    if log_path:
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "role": role,
                        "argv": argv,
                        "cwd": os.getcwd(),
                        "stdinIsDevNull": _stdin_is_devnull(),
                    }
                )
                + "\n"
            )

    on_sigterm = call.get("on_sigterm", "exit")

    def handle_term(_signum, _frame):
        if on_sigterm == "exit":
            sys.exit(143)

    signal.signal(signal.SIGTERM, handle_term)

    grandchild = call.get("spawn_grandchild")
    if grandchild:
        # A child of the fake (a grandchild of the supervisor), like a shell
        # the real CLI starts for a Bash tool call. Same process group.
        code = "import signal, time\n"
        if grandchild.get("ignore_term"):
            code += "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        code += "time.sleep(60)\n"
        child = subprocess.Popen(
            [sys.executable, "-c", code],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        Path(grandchild["pid_file"]).write_text(str(child.pid), encoding="utf-8")

    for relative, content in (call.get("write_files") or {}).items():
        target = Path(os.getcwd()) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    for key, value in (call.get("git_config") or {}).items():
        subprocess.run(["git", "config", key, value], check=True, capture_output=True)
    if call.get("git_checkout"):
        subprocess.run(["git", "checkout", "-q", "-b", str(call["git_checkout"])],
                       check=True, capture_output=True)
    if call.get("git_mv"):
        source, destination = call["git_mv"]
        subprocess.run(["git", "mv", source, destination], check=True, capture_output=True)
    if call.get("git_commit"):
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=fake", "-c", "user.email=fake@example.invalid",
             "commit", "-q", "-m", str(call["git_commit"])],
            check=True, capture_output=True,
        )

    deadline = time.monotonic() + float(call.get("sleep", 0))
    while time.monotonic() < deadline:
        time.sleep(0.02)

    mode = call.get("mode", "json")
    exit_code = int(call.get("exit_code", 0))
    if mode == "silent":
        return exit_code
    if mode == "garbage":
        sys.stdout.write("this is not json at all\n{broken")
        return exit_code

    result = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "num_turns": 3,
        "duration_ms": 1234,
        "total_cost_usd": 0.5,
        "session_id": f"11111111-2222-3333-4444-{role[:5]:0>12}",
        "stop_reason": "end_turn",
        "permission_denials": [],
        "structured_output": call.get("structured_output"),
        "result": "",
    }
    result.update(call.get("result") or {})
    if "worker_output" in call:
        body = json.dumps(call["worker_output"])
        wrap = call.get("wrap", "none")
        if wrap == "text":
            body = "Here is what I did.\n" + body + "\nDone."
        elif wrap == "fence":
            body = "```json\n" + body + "\n```"
        result["result"] = body
    if call.get("noise"):
        sys.stdout.write("warning: something on stdout first\n")
    sys.stdout.write(json.dumps(result) + "\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
