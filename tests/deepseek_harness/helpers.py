"""Synthetic fixtures and host-access guards for the DeepSeek Harness spike.

Every value here is authored for the tests; nothing is captured from a real
DeepSeek Harness process, provider, model, host environment, or credential.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import MutableMapping
from contextlib import ExitStack, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterator
from unittest import TestCase, mock

from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessContractError,
    DeepSeekHarnessRunContext,
    SessionBinding,
)


TICKET_ID = "PIP-899"
RUN_ID = "RUN-0123456789ab"
OTHER_RUN_ID = "RUN-ba9876543210"
SESSION_ONE = "dsh-session-0001"
SESSION_TWO = "dsh-session-0002"
SESSION_THREE = "dsh-session-0003"
DSH_VERSION = "dsh-v0.1.2-alpha.5"
PROTOCOL_VERSION = "dsh-protocol-49a606bc"
PROFILE_ID = "pipe-readonly-review"
PLUGIN_TREE_FINGERPRINT = "sha256:" + "1" * 64
ROUTE_ID = "synthetic-route-a"
OTHER_ROUTE_ID = "synthetic-route-b"
MODEL_ID = "synthetic-model-a"
OTHER_MODEL_ID = "synthetic-model-b"
WORKSPACE_FINGERPRINT = "sha256:" + "2" * 64
CONTEXT_FINGERPRINT = "sha256:" + "3" * 64
CONSUMER_ID = "pipe-consumer-a"
OTHER_CONSUMER_ID = "pipe-consumer-b"
DEFAULT_REFS = ("README.md", "review/notes.md")

# Secret-shaped (matches the repository sensitive-value detector) and textual
# sentinels. Neither may ever be echoed by a document or an error.
SECRET_SENTINEL = "sk-dshsentinel0000000000000000000"
TEXT_SENTINEL = "DSH-RAW-TEXT-SENTINEL"

FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")
METADATA_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+=_-]*$")
RAW_CONTENT_KEYS = frozenset(
    {
        "args",
        "arguments",
        "content",
        "env",
        "environment",
        "frame",
        "message",
        "messages",
        "output",
        "payload",
        "prompt",
        "reasoning",
        "result",
        "stderr",
        "stdout",
        "text",
    }
)


REGISTERED_AT = "2026-09-10T11:59:00Z"
BEGIN_AT = "2026-09-10T12:00:00Z"
READ_TOOL = "read_file"


def event_at(sequence: int) -> str:
    return f"2026-09-10T12:{sequence:02d}:00Z"


def event_metadata(sequence: int = 1, **overrides: Any) -> dict[str, Any]:
    """Synthetic, payload-free DSH event metadata authored for the tests."""

    fields: dict[str, Any] = {
        "externalEventId": f"dsh-evt-{sequence:04d}",
        "sessionId": SESSION_ONE,
        "sequence": sequence,
        "kind": "turn.started",
        "occurredAt": event_at(sequence),
    }
    fields.update(overrides)
    return fields


@contextmanager
def fixture_base() -> Iterator[Path]:
    """Yield a resolved temporary base so platform temp symlinks stay outside."""

    with TemporaryDirectory() as directory:
        yield Path(directory).resolve()


def make_fixture_root(base: Path, name: str = "fixture") -> Path:
    root = base / name
    (root / "review").mkdir(parents=True)
    (root / "README.md").write_text("# Synthetic fixture\n", encoding="utf-8")
    (root / "review" / "notes.md").write_text(
        "# Synthetic review notes\n", encoding="utf-8"
    )
    return root


def context_fields(root: Path, **overrides: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "linear_ticket_id": TICKET_ID,
        "workflow": "review",
        "fixture_root": root,
        "workspace_refs": list(DEFAULT_REFS),
    }
    fields.update(overrides)
    return fields


def build_context(root: Path, **overrides: Any) -> DeepSeekHarnessRunContext:
    return DeepSeekHarnessRunContext.build(**context_fields(root, **overrides))


def binding_fields(**overrides: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "pipe_run_id": RUN_ID,
        "session_id": SESSION_ONE,
        "attempt": 1,
        "dsh_version": DSH_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "profile_id": PROFILE_ID,
        "plugin_tree_fingerprint": PLUGIN_TREE_FINGERPRINT,
        "route_id": ROUTE_ID,
        "model_id": MODEL_ID,
        "workspace_fingerprint": WORKSPACE_FINGERPRINT,
        "context_fingerprint": CONTEXT_FINGERPRINT,
        "consumer_id": CONSUMER_ID,
    }
    fields.update(overrides)
    return fields


def build_binding(**overrides: Any) -> SessionBinding:
    return SessionBinding.build(**binding_fields(**overrides))


def rendered_error(error: BaseException) -> str:
    """Render an error and every chained cause/context a traceback would show."""

    parts: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        parts.extend((str(current), repr(current), repr(current.args)))
        for attribute in ("filename", "filename2"):
            value = getattr(current, attribute, None)
            if value is not None:
                parts.append(str(value))
        if current.__cause__ is not None:
            current = current.__cause__
        elif not current.__suppress_context__:
            current = current.__context__
        else:
            current = None
    return "\n".join(parts)


def assert_blocked(
    test: TestCase,
    code: str,
    function: Callable[..., Any],
    *args: Any,
    forbidden: tuple[str, ...] = (),
    **kwargs: Any,
) -> DeepSeekHarnessContractError:
    """Assert a stable blocker code and a fixed, payload/path-free error."""

    with test.assertRaises(DeepSeekHarnessContractError) as caught:
        function(*args, **kwargs)
    error = caught.exception
    test.assertEqual(error.code, code)
    rendered = rendered_error(error)
    for text in (SECRET_SENTINEL, TEXT_SENTINEL, *forbidden):
        test.assertNotIn(text, rendered)
    return error


def assert_block_marker(
    test: TestCase, before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> None:
    """The only audit change is one payload-free ``DHD-*:blocked`` marker."""

    test.assertEqual(after[: len(before)], before)
    test.assertEqual(len(after), len(before) + 1)
    marker = after[-1]
    test.assertEqual(marker["eventType"], "run.interrupted")
    test.assertEqual(marker["status"], "blocked")
    test.assertEqual(marker["reasonCode"], "adapter_conflict")
    test.assertRegex(marker["references"]["idempotencyKey"], r"^DHD-[a-f0-9]+:blocked$")
    test.assertIsNone(marker["references"]["resultRef"])
    test.assertIsNone(marker["fingerprints"]["result"])
    rendered = json.dumps(marker)
    for sentinel in (TEXT_SENTINEL, SECRET_SENTINEL):
        test.assertNotIn(sentinel, rendered)


def assert_metadata_only(test: TestCase, value: Any, *, path: str = "$") -> None:
    """Documents carry only identifiers, hashes, counts, and boolean states."""

    if isinstance(value, dict):
        for key, item in value.items():
            test.assertIsInstance(key, str, path)
            test.assertRegex(key, METADATA_TOKEN, path)
            test.assertNotIn(key.lower(), RAW_CONTENT_KEYS, f"{path}.{key}")
            assert_metadata_only(test, item, path=f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_metadata_only(test, item, path=f"{path}[{index}]")
    elif isinstance(value, str):
        test.assertRegex(value, METADATA_TOKEN, path)
        test.assertNotIn(SECRET_SENTINEL, value, path)
        test.assertNotIn(TEXT_SENTINEL, value, path)
    else:
        test.assertTrue(
            value is None or isinstance(value, (bool, int)),
            f"{path} carries a non-metadata value",
        )


class _ForbiddenEnviron(MutableMapping):
    """Stand-in for ``os.environ`` that records and refuses every access."""

    def __init__(self, log: list[str]) -> None:
        self._log = log

    def _deny(self, operation: str) -> Any:
        self._log.append(f"os.environ.{operation}")
        raise AssertionError("host environment access is forbidden")

    def __getitem__(self, key: Any) -> Any:
        return self._deny("getitem")

    def __setitem__(self, key: Any, value: Any) -> None:
        self._deny("setitem")

    def __delitem__(self, key: Any) -> None:
        self._deny("delitem")

    def __iter__(self) -> Iterator[Any]:
        return self._deny("iter")

    def __len__(self) -> int:
        return self._deny("len")

    def __contains__(self, key: object) -> bool:
        return self._deny("contains")

    def get(self, key: Any, default: Any = None) -> Any:
        return self._deny("get")

    def keys(self) -> Any:
        return self._deny("keys")

    def items(self) -> Any:
        return self._deny("items")

    def values(self) -> Any:
        return self._deny("values")

    def copy(self) -> Any:
        return self._deny("copy")


@contextmanager
def forbid_host_access(*, filesystem: bool = True) -> Iterator[list[str]]:
    """Record and refuse host environment, process, network and file access.

    The yielded list must stay empty; implementations that swallow the
    refusal are still caught because every attempt is recorded first.
    """

    log: list[str] = []

    def deny(name: str) -> Callable[..., Any]:
        def denied(*args: Any, **kwargs: Any) -> Any:
            log.append(name)
            raise AssertionError("host access is forbidden in this test")

        return denied

    targets: dict[str, Any] = {
        "os.environ": _ForbiddenEnviron(log),
        "os.getenv": deny("os.getenv"),
        "os.putenv": deny("os.putenv"),
        "os.path.expanduser": deny("os.path.expanduser"),
        "os.path.expandvars": deny("os.path.expandvars"),
        "pathlib.Path.home": deny("Path.home"),
        "pathlib.Path.expanduser": deny("Path.expanduser"),
        "os.system": deny("os.system"),
        "os.popen": deny("os.popen"),
        "subprocess.Popen": deny("subprocess.Popen"),
        "subprocess.run": deny("subprocess.run"),
        "socket.socket": deny("socket.socket"),
        "socket.create_connection": deny("socket.create_connection"),
    }
    if hasattr(os, "environb"):
        targets["os.environb"] = _ForbiddenEnviron(log)
    for name in ("fork", "posix_spawn", "posix_spawnp"):
        if hasattr(os, name):
            targets[f"os.{name}"] = deny(f"os.{name}")
    if filesystem:
        targets.update(
            {
                "builtins.open": deny("open"),
                "io.open": deny("io.open"),
                "os.open": deny("os.open"),
                "os.listdir": deny("os.listdir"),
                "os.scandir": deny("os.scandir"),
                "os.walk": deny("os.walk"),
            }
        )
    with ExitStack() as stack:
        for target, replacement in targets.items():
            stack.enter_context(mock.patch(target, new=replacement))
        yield log
