"""Own atomic, fingerprinted adapter checkpoint (ADR-004 D5, D7, D13).

One canonical JSON file per Pipe run, in a ``0700`` directory, written as a
``0600`` file through a temporary file, ``fsync`` and an atomic rename. Every
path component is walked from ``/`` with no-follow descriptors: a symlink is
refused and never followed, even when its target is inside the directory. An
interrupted write never replaces the last valid checkpoint.

The checkpoint holds only identifiers, sequence numbers, hashes, kinds and
states. It is distinct from any DSH transcript/session checkpoint and never
substitutes the Pipe control plane, which stays the source of truth for plan,
action, approval and verification.
"""

from __future__ import annotations

import errno
import json
import os
import re
import secrets
import stat
from pathlib import PurePath, PurePosixPath
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import (
    FINGERPRINT_PATTERN,
    ControlPlaneContractError,
    canonical_json,
    fingerprint,
    parse_datetime,
)

from .context import WORKFLOW_KINDS, _close_quietly, _no_follow_flags
from .errors import BLOCKER_CODES, DeepSeekHarnessContractError
from .events import EVENT_KINDS
from .session import MAX_ATTEMPTS


SCHEMA_VERSION = "0.1.0"
CHECKPOINT_STATES = frozenset(
    {"dispatch_pending", "running", "blocked", "outcome_unknown", "completed"}
)
BLOCKED_STATES = frozenset({"blocked", "outcome_unknown"})
CHECKPOINT_CONSTRAINTS = {
    "rawPayloadPersisted": False,
    "credentialsPersisted": False,
    "runtimeApprovalIsAuthority": False,
    "runtimeCompletionIsAuthority": False,
    "externalMutationAllowed": False,
}
MAX_PROCESSED_EVENTS = 4096
MAX_CHECKPOINT_BYTES = 4 * 1024 * 1024
MAX_DIRECTORY_DEPTH = 64
_DIRECTORY_MODE = 0o700
_FILE_MODE = 0o600
_READ_CHUNK = 64 * 1024

_FIELDS = frozenset(
    {
        "schemaVersion",
        "runId",
        "planId",
        "planFingerprint",
        "linearTicketId",
        "workflow",
        "contextFingerprint",
        "workspaceFingerprint",
        "sessionId",
        "attempt",
        "bindingFingerprint",
        "dispatchId",
        "sessionLineage",
        "state",
        "expectedSequence",
        "processedEvents",
        "pendingEvent",
        "blockerCode",
        "proposalFingerprint",
        "updatedAt",
        "constraints",
        "checkpointFingerprint",
    }
)
_RECORD_FIELDS = frozenset({"eventId", "sequence", "fingerprint", "kind"})
_RUN_ID = re.compile(r"RUN-[a-f0-9]{12}")
_PLAN_ID = re.compile(r"RP-[a-f0-9]{12}")
_DISPATCH_ID = re.compile(r"DHD-[a-f0-9]{12}")
_EVENT_ID = re.compile(r"DHE-[a-f0-9]{12}")
_TICKET = re.compile(r"PIP-[0-9]{1,9}")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+=-]{0,127}")


class DeepSeekHarnessCheckpointStore:
    """One fingerprinted checkpoint per Pipe run; symlinks are never followed."""

    __slots__ = ("_components", "_identity", "_directory_flags", "_file_flags")

    def __init__(self, directory: Any) -> None:
        self._components = _directory_components(directory)
        self._directory_flags, self._file_flags = _no_follow_flags()
        if (
            os.mkdir not in os.supports_dir_fd
            or os.unlink not in os.supports_dir_fd
            or os.rename not in os.supports_dir_fd
        ):
            raise DeepSeekHarnessContractError("platform_unsupported") from None
        descriptor = _walk(self._components, self._directory_flags, create=True)
        try:
            opened = _fstat(descriptor)
            if opened.st_uid != os.geteuid():
                raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
            if stat.S_IMODE(opened.st_mode) != _DIRECTORY_MODE:
                try:
                    os.fchmod(descriptor, _DIRECTORY_MODE)
                except OSError:
                    raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
            self._identity = (opened.st_dev, opened.st_ino)
        finally:
            _close_quietly(descriptor)

    def load(self, run_id: Any) -> dict[str, Any] | None:
        """Return the verified checkpoint, ``None`` if absent, or refuse."""

        name = _file_name(run_id)
        directory = self._open_directory()
        try:
            try:
                descriptor = os.open(name, self._file_flags, dir_fd=directory)
            except FileNotFoundError:
                return None
            except OSError as exc:
                code = "symlink_forbidden" if exc.errno == errno.ELOOP else "checkpoint_invalid"
                raise DeepSeekHarnessContractError(code) from None
            try:
                raw = _read_checkpoint(descriptor)
            finally:
                _close_quietly(descriptor)
        finally:
            _close_quietly(directory)
        return _decode(raw)

    def save(self, document: Any) -> dict[str, Any]:
        """Sign, validate and atomically replace the run checkpoint."""

        if not isinstance(document, Mapping):
            raise DeepSeekHarnessContractError("checkpoint_invalid") from None
        unsigned = {key: value for key, value in document.items() if key != "checkpointFingerprint"}
        try:
            signed = {**unsigned, "checkpointFingerprint": fingerprint(unsigned)}
        except ControlPlaneContractError:
            raise DeepSeekHarnessContractError("checkpoint_invalid") from None
        validate_checkpoint(signed)
        name = _file_name(signed["runId"])
        encoded = (canonical_json(signed) + "\n").encode("utf-8")
        directory = self._open_directory()
        try:
            _replace_atomically(directory, name, encoded)
        finally:
            _close_quietly(directory)
        return signed

    def _open_directory(self) -> int:
        descriptor = _walk(self._components, self._directory_flags, create=False)
        try:
            opened = _fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != self._identity:
                raise DeepSeekHarnessContractError("checkpoint_path_changed") from None
            if stat.S_IMODE(opened.st_mode) != _DIRECTORY_MODE:
                raise DeepSeekHarnessContractError("checkpoint_mode_invalid") from None
        except BaseException:
            _close_quietly(descriptor)
            raise
        return descriptor


def validate_checkpoint(value: Any) -> None:
    """Refuse any checkpoint outside the closed, metadata-only shape."""

    if not isinstance(value, Mapping) or set(value) != _FIELDS:
        _invalid()
    if value["schemaVersion"] != SCHEMA_VERSION:
        _invalid()
    _require_pattern(value["runId"], _RUN_ID)
    _require_pattern(value["planId"], _PLAN_ID)
    _require_pattern(value["dispatchId"], _DISPATCH_ID)
    _require_pattern(value["linearTicketId"], _TICKET)
    for key in (
        "planFingerprint",
        "contextFingerprint",
        "workspaceFingerprint",
        "bindingFingerprint",
        "checkpointFingerprint",
    ):
        _require_pattern(value[key], FINGERPRINT_PATTERN)
    if type(value["workflow"]) is not str or value["workflow"] not in WORKFLOW_KINDS:
        _invalid()
    _require_identifier(value["sessionId"])
    attempt = value["attempt"]
    if type(attempt) is not int or not 1 <= attempt <= MAX_ATTEMPTS:
        _invalid()
    lineage = value["sessionLineage"]
    if (
        type(lineage) is not list
        or len(lineage) != attempt
        or lineage[-1] != value["sessionId"]
        or len(set(map(str, lineage))) != len(lineage)
    ):
        _invalid()
    for session_id in lineage:
        _require_identifier(session_id)

    state = value["state"]
    if type(state) is not str or state not in CHECKPOINT_STATES:
        _invalid()
    processed = value["processedEvents"]
    if type(processed) is not list or len(processed) > MAX_PROCESSED_EVENTS:
        _invalid()
    identities: set[str] = set()
    for index, record in enumerate(processed, start=1):
        _require_record(record, index)
        if record["eventId"] in identities:
            _invalid()
        identities.add(record["eventId"])
    expected = value["expectedSequence"]
    if type(expected) is not int or expected != len(processed) + 1:
        _invalid()
    pending = value["pendingEvent"]
    if pending is not None:
        _require_record(pending, expected)
        if state != "running" or pending["eventId"] in identities:
            _invalid()
    if state == "dispatch_pending" and processed:
        _invalid()
    blocker = value["blockerCode"]
    if (state in BLOCKED_STATES) != (blocker is not None):
        _invalid()
    if blocker is not None and (type(blocker) is not str or blocker not in BLOCKER_CODES):
        _invalid()
    proposal = value["proposalFingerprint"]
    if proposal is not None:
        _require_pattern(proposal, FINGERPRINT_PATTERN)
    if state == "completed" and (proposal is None or pending is not None):
        _invalid()
    updated_at = value["updatedAt"]
    if type(updated_at) is not str:
        _invalid()
    try:
        parse_datetime(updated_at)
    except ControlPlaneContractError:
        _invalid()
    if value["constraints"] != CHECKPOINT_CONSTRAINTS:
        _invalid()
    if not payload_is_safe(dict(value)):
        _invalid()


def _require_record(record: Any, sequence: int) -> None:
    if not isinstance(record, Mapping) or set(record) != _RECORD_FIELDS:
        _invalid()
    _require_pattern(record["eventId"], _EVENT_ID)
    _require_pattern(record["fingerprint"], FINGERPRINT_PATTERN)
    if type(record["sequence"]) is not int or record["sequence"] != sequence:
        _invalid()
    if type(record["kind"]) is not str or record["kind"] not in EVENT_KINDS:
        _invalid()


def _require_pattern(value: Any, pattern: re.Pattern[str]) -> None:
    if type(value) is not str or pattern.fullmatch(value) is None:
        _invalid()


def _require_identifier(value: Any) -> None:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None or not payload_is_safe(value):
        _invalid()


def _invalid() -> None:
    raise DeepSeekHarnessContractError("checkpoint_invalid") from None


def _file_name(run_id: Any) -> str:
    if type(run_id) is not str or _RUN_ID.fullmatch(run_id) is None:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    return f"{run_id}.json"


def _decode(raw: bytes) -> dict[str, Any]:
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError):
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    if type(document) is not dict:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    try:
        canonical = (canonical_json(document) + "\n").encode("utf-8")
    except ControlPlaneContractError:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    if canonical != raw:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    supplied = document.get("checkpointFingerprint")
    if type(supplied) is not str or FINGERPRINT_PATTERN.fullmatch(supplied) is None:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    unsigned = {key: value for key, value in document.items() if key != "checkpointFingerprint"}
    if fingerprint(unsigned) != supplied:
        raise DeepSeekHarnessContractError("checkpoint_tampered") from None
    validate_checkpoint(document)
    return document


def _read_checkpoint(descriptor: int) -> bytes:
    opened = _fstat(descriptor)
    if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    if opened.st_uid != os.geteuid():
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    if stat.S_IMODE(opened.st_mode) != _FILE_MODE:
        raise DeepSeekHarnessContractError("checkpoint_mode_invalid") from None
    if opened.st_size > MAX_CHECKPOINT_BYTES:
        raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    chunks: list[bytes] = []
    size = 0
    while True:
        try:
            chunk = os.read(descriptor, _READ_CHUNK)
        except OSError:
            raise DeepSeekHarnessContractError("checkpoint_invalid") from None
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_CHECKPOINT_BYTES:
            raise DeepSeekHarnessContractError("checkpoint_invalid") from None
        chunks.append(chunk)
    return b"".join(chunks)


def _replace_atomically(directory: int, name: str, encoded: bytes) -> None:
    """Write a 0600 temporary file, fsync, rename over ``name`` and fsync the directory."""

    try:
        existing = os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        existing = None
    except OSError:
        raise DeepSeekHarnessContractError("checkpoint_write_failed") from None
    if existing is not None:
        if stat.S_ISLNK(existing.st_mode):
            raise DeepSeekHarnessContractError("symlink_forbidden") from None
        if not stat.S_ISREG(existing.st_mode):
            raise DeepSeekHarnessContractError("checkpoint_invalid") from None
    temporary = f".{name}.{secrets.token_hex(8)}.tmp"
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        descriptor = os.open(temporary, flags, _FILE_MODE, dir_fd=directory)
    except OSError:
        raise DeepSeekHarnessContractError("checkpoint_write_failed") from None
    replaced = False
    try:
        try:
            os.fchmod(descriptor, _FILE_MODE)
            view = memoryview(encoded)
            while view:
                view = view[os.write(descriptor, view):]
            os.fsync(descriptor)
        finally:
            _close_quietly(descriptor)
        os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
        replaced = True
        os.fsync(directory)
    except OSError:
        raise DeepSeekHarnessContractError("checkpoint_write_failed") from None
    finally:
        if not replaced:
            try:
                os.unlink(temporary, dir_fd=directory)
            except OSError:
                pass


def _directory_components(directory: Any) -> tuple[str, ...]:
    """Validate the checkpoint directory lexically; ``~`` is never expanded."""

    if isinstance(directory, PurePath):
        text = str(directory)
    elif type(directory) is str:
        text = directory
    else:
        raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
    if not text or "\x00" in text:
        raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
    parts = PurePosixPath(text).parts
    if (
        len(parts) < 2
        or len(parts) > MAX_DIRECTORY_DEPTH
        or parts[0] != "/"
        or ".." in parts
    ):
        raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
    return parts[1:]


def _walk(components: tuple[str, ...], directory_flags: int, *, create: bool) -> int:
    """Open the directory from ``/`` one no-follow component at a time."""

    try:
        current = os.open("/", directory_flags)
    except OSError:
        raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
    try:
        last = len(components) - 1
        for index, name in enumerate(components):
            entry = _lstat(current, name)
            if entry is None and create and index == last:
                try:
                    os.mkdir(name, _DIRECTORY_MODE, dir_fd=current)
                except FileExistsError:
                    pass
                except OSError:
                    raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
                entry = _lstat(current, name)
            if entry is None:
                raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
            if stat.S_ISLNK(entry.st_mode):
                raise DeepSeekHarnessContractError("symlink_forbidden") from None
            if not stat.S_ISDIR(entry.st_mode):
                raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
            try:
                child = os.open(name, directory_flags, dir_fd=current)
            except OSError as exc:
                code = "symlink_forbidden" if exc.errno == errno.ELOOP else "checkpoint_path_invalid"
                raise DeepSeekHarnessContractError(code) from None
            try:
                opened = _fstat(child)
                if (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino):
                    raise DeepSeekHarnessContractError("checkpoint_path_changed") from None
            except BaseException:
                _close_quietly(child)
                raise
            _close_quietly(current)
            current = child
    except BaseException:
        _close_quietly(current)
        raise
    return current


def _lstat(directory: int, name: str) -> os.stat_result | None:
    try:
        return os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError:
        raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None


def _fstat(descriptor: int) -> os.stat_result:
    try:
        return os.fstat(descriptor)
    except OSError:
        raise DeepSeekHarnessContractError("checkpoint_path_invalid") from None
