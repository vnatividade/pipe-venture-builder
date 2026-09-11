"""Read-only run context over a disposable synthetic fixture root.

ADR-004 D2 limits the spike to ``review``/``check``. D7 requires a disposable
fixture workspace outside the Pipe worktree, without ``.git``, ``.env``,
special files, or any symlink regardless of its target. The filesystem is
inspected with no-follow, descriptor-relative primitives: symlinks are refused
from ``lstat`` data and never followed, the whole fixture tree is validated
before any file is read, and every directory/file opened afterwards must keep
the identity recorded during the scan. File content is only hashed in memory;
nothing read here is retained or persisted (D13).
"""

from __future__ import annotations

import errno
import hashlib
import os
import re
import stat
from dataclasses import dataclass, field
from pathlib import PurePath, PurePosixPath
from typing import Any

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import FINGERPRINT_PATTERN, fingerprint

from .errors import DeepSeekHarnessContractError


SCHEMA_VERSION = "0.1.0"
WORKFLOW_KINDS = frozenset({"review", "check"})
MAX_WORKSPACE_REFS = 128
MAX_REF_LENGTH = 512
MAX_ROOT_DEPTH = 64
MAX_TREE_DEPTH = 32
MAX_TREE_ENTRIES = 4096
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_WORKSPACE_BYTES = 64 * 1024 * 1024
_READ_CHUNK = 64 * 1024

_TICKET = re.compile(r"PIP-[0-9]{1,9}")
_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+=/-]*")
_REF_PART = re.compile(r"[A-Za-z0-9._+=-]{1,255}")
_FORBIDDEN_NAMES = frozenset(
    {".aws", ".docker", ".env", ".git", ".gnupg", ".netrc", ".npmrc", ".pypirc", ".ssh"}
)
_FORBIDDEN_PREFIXES = (".env.",)
_CONSTRAINTS = {
    "repositoryCanonical": True,
    "runtimeApprovalIsAuthority": False,
    "externalMutationAllowed": False,
    "rawPayloadPersisted": False,
    "credentialsAllowed": False,
    "networkAllowed": False,
    "hostEnvironmentInherited": False,
}

_Catalog = dict[str, tuple[str, tuple[int, int]]]


class _WorkspaceSeal:
    """Ties a context to the refs/fingerprint produced by an actual scan."""

    __slots__ = ("_refs", "_fingerprint")

    def __init__(self, refs: tuple[str, ...], workspace_fingerprint: str) -> None:
        self._refs = refs
        self._fingerprint = workspace_fingerprint

    def matches(self, refs: tuple[str, ...], workspace_fingerprint: str) -> bool:
        return self._refs == refs and self._fingerprint == workspace_fingerprint

    def __repr__(self) -> str:
        return "<workspace-seal>"


@dataclass(frozen=True)
class DeepSeekHarnessRunContext:
    """Metadata-only context a DeepSeek Harness session may be bound to.

    Use ``build``: direct construction without a scan seal is refused. The
    fixture root is deliberately not retained, so no absolute path can leak
    through the object, its ``repr``, or its document.
    """

    linear_ticket_id: str
    workflow: str
    workspace_refs: tuple[str, ...]
    workspace_fingerprint: str
    _seal: _WorkspaceSeal = field(repr=False, compare=False)
    context_fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        _require_workflow(self.workflow)
        _require_ticket(self.linear_ticket_id)
        if type(self.workspace_refs) is not tuple:
            raise DeepSeekHarnessContractError("context_invalid") from None
        if self.workspace_refs != _normalize_refs(self.workspace_refs):
            raise DeepSeekHarnessContractError("context_invalid") from None
        if (
            type(self.workspace_fingerprint) is not str
            or FINGERPRINT_PATTERN.fullmatch(self.workspace_fingerprint) is None
        ):
            raise DeepSeekHarnessContractError("context_invalid") from None
        seal = self._seal
        if type(seal) is not _WorkspaceSeal or not seal.matches(
            self.workspace_refs, self.workspace_fingerprint
        ):
            raise DeepSeekHarnessContractError("context_invalid") from None
        object.__setattr__(self, "context_fingerprint", fingerprint(self._core()))

    @classmethod
    def build(
        cls,
        *,
        linear_ticket_id: Any,
        workflow: Any,
        fixture_root: Any,
        workspace_refs: Any,
    ) -> DeepSeekHarnessRunContext:
        _require_workflow(workflow)
        _require_ticket(linear_ticket_id)
        # Lexical ref validation happens before the filesystem is touched.
        refs = _normalize_refs(workspace_refs)
        workspace_fingerprint = _workspace_fingerprint(fixture_root, refs)
        return cls(
            linear_ticket_id=linear_ticket_id,
            workflow=workflow,
            workspace_refs=refs,
            workspace_fingerprint=workspace_fingerprint,
            _seal=_WorkspaceSeal(refs, workspace_fingerprint),
        )

    def document(self) -> dict[str, Any]:
        """Return a fresh, relative, metadata-only document."""

        document = self._core()
        document["contextFingerprint"] = self.context_fingerprint
        return document

    def _core(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "linearTicketId": self.linear_ticket_id,
            "workflow": self.workflow,
            "workspaceRefs": list(self.workspace_refs),
            "workspaceFingerprint": self.workspace_fingerprint,
            "constraints": dict(_CONSTRAINTS),
        }


def _require_workflow(value: Any) -> None:
    if type(value) is not str or value not in WORKFLOW_KINDS:
        raise DeepSeekHarnessContractError("workflow_unsupported") from None


def _require_ticket(value: Any) -> None:
    if type(value) is not str or _TICKET.fullmatch(value) is None:
        raise DeepSeekHarnessContractError("linear_ticket_invalid") from None


def _is_forbidden_name(name: str) -> bool:
    folded = name.casefold()
    return folded in _FORBIDDEN_NAMES or folded.startswith(_FORBIDDEN_PREFIXES)


def _normalize_refs(refs: Any) -> tuple[str, ...]:
    if type(refs) not in (list, tuple) or not refs or len(refs) > MAX_WORKSPACE_REFS:
        raise DeepSeekHarnessContractError("workspace_refs_invalid") from None
    return tuple(sorted({_lexical_ref(ref) for ref in refs}))


def _lexical_ref(ref: Any) -> str:
    if type(ref) is not str or not ref or len(ref) > MAX_REF_LENGTH:
        raise DeepSeekHarnessContractError("workspace_ref_invalid") from None
    if (
        ref.startswith("/")
        or "\\" in ref
        or any(ord(character) < 32 or ord(character) == 127 for character in ref)
    ):
        raise DeepSeekHarnessContractError("workspace_ref_invalid") from None
    parts = ref.split("/")
    if len(parts) > MAX_TREE_DEPTH or any(part in {"", ".", ".."} for part in parts):
        raise DeepSeekHarnessContractError("workspace_ref_invalid") from None
    if any(_is_forbidden_name(part) for part in parts):
        raise DeepSeekHarnessContractError("path_forbidden") from None
    if _REF.fullmatch(ref) is None or not all(
        _REF_PART.fullmatch(part) for part in parts
    ):
        raise DeepSeekHarnessContractError("workspace_ref_invalid") from None
    if not payload_is_safe(ref):
        raise DeepSeekHarnessContractError("workspace_ref_invalid") from None
    return ref


def _workspace_fingerprint(fixture_root: Any, refs: tuple[str, ...]) -> str:
    root_components = _root_components(fixture_root)
    directory_flags, file_flags = _no_follow_flags()
    root_fd = _open_fixture_root(root_components, directory_flags)
    try:
        catalog: _Catalog = {}
        _scan_directory(root_fd, "", 0, catalog, directory_flags)
        files: list[dict[str, Any]] = []
        total = 0
        for ref in refs:
            digest, size = _hash_ref(root_fd, ref, catalog, directory_flags, file_flags)
            total += size
            if total > MAX_WORKSPACE_BYTES:
                raise DeepSeekHarnessContractError("workspace_too_large") from None
            files.append({"ref": ref, "sha256": digest, "bytes": size})
    finally:
        _close_quietly(root_fd)
    return fingerprint(
        {
            "schemaVersion": SCHEMA_VERSION,
            "kind": "deepseek-harness-workspace-manifest",
            "files": files,
        }
    )


def _no_follow_flags() -> tuple[int, int]:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    if (
        no_follow is None
        or os.open not in os.supports_dir_fd
        or os.stat not in os.supports_dir_fd
        or os.stat not in os.supports_follow_symlinks
        or os.scandir not in os.supports_fd
    ):
        raise DeepSeekHarnessContractError("platform_unsupported") from None
    common = os.O_RDONLY | no_follow | getattr(os, "O_CLOEXEC", 0)
    return (
        common | getattr(os, "O_DIRECTORY", 0),
        common | getattr(os, "O_NONBLOCK", 0),
    )


def _root_components(fixture_root: Any) -> tuple[str, ...]:
    """Validate the fixture root lexically; ``~`` is never expanded."""

    if isinstance(fixture_root, PurePath):
        text = str(fixture_root)
    elif type(fixture_root) is str:
        text = fixture_root
    else:
        raise DeepSeekHarnessContractError("fixture_root_invalid") from None
    if not text or "\x00" in text:
        raise DeepSeekHarnessContractError("fixture_root_invalid") from None
    parts = PurePosixPath(text).parts
    if (
        len(parts) < 2
        or len(parts) > MAX_ROOT_DEPTH
        or parts[0] != "/"
        or ".." in parts
    ):
        raise DeepSeekHarnessContractError("fixture_root_invalid") from None
    # The same D7 path classes refused inside the tree are refused lexically
    # in the root and its ancestors, before any filesystem access.
    if any(_is_forbidden_name(name) for name in parts[1:]):
        raise DeepSeekHarnessContractError("path_forbidden") from None
    return parts[1:]


def _open_fixture_root(root_components: tuple[str, ...], directory_flags: int) -> int:
    """Walk from ``/`` one component at a time, never following a symlink.

    Every ancestor and the root itself must be a real directory, and none of
    them may contain a ``.git`` entry (the root must not be, or be inside, a
    git worktree).
    """

    try:
        current = os.open("/", directory_flags)
    except OSError:
        raise DeepSeekHarnessContractError("fixture_root_invalid") from None
    try:
        for name in root_components:
            _refuse_git_marker(current)
            entry = _lstat_at(current, name, "fixture_root_invalid")
            if stat.S_ISLNK(entry.st_mode):
                raise DeepSeekHarnessContractError("symlink_forbidden") from None
            if not stat.S_ISDIR(entry.st_mode):
                raise DeepSeekHarnessContractError("fixture_root_invalid") from None
            child = _open_directory(
                current, name, (entry.st_dev, entry.st_ino), directory_flags
            )
            _close_quietly(current)
            current = child
        _refuse_git_marker(current)
    except BaseException:
        _close_quietly(current)
        raise
    return current


def _refuse_git_marker(directory_fd: int) -> None:
    try:
        os.stat(".git", dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError:
        raise DeepSeekHarnessContractError("fixture_root_invalid") from None
    raise DeepSeekHarnessContractError("fixture_root_forbidden") from None


def _scan_directory(
    directory_fd: int,
    prefix: str,
    depth: int,
    catalog: _Catalog,
    directory_flags: int,
) -> None:
    """Validate every entry, referenced or not, before any file is read."""

    try:
        with os.scandir(directory_fd) as entries:
            names = sorted(entry.name for entry in entries)
    except OSError:
        raise DeepSeekHarnessContractError("fixture_root_invalid") from None
    for name in names:
        if len(catalog) >= MAX_TREE_ENTRIES:
            raise DeepSeekHarnessContractError("workspace_too_large") from None
        entry = _lstat_at(directory_fd, name, "workspace_changed")
        mode = entry.st_mode
        if stat.S_ISLNK(mode):
            raise DeepSeekHarnessContractError("symlink_forbidden") from None
        if _is_forbidden_name(name):
            raise DeepSeekHarnessContractError("path_forbidden") from None
        relative = prefix + name
        identity = (entry.st_dev, entry.st_ino)
        if stat.S_ISDIR(mode):
            if depth + 1 >= MAX_TREE_DEPTH:
                raise DeepSeekHarnessContractError("workspace_too_large") from None
            catalog[relative] = ("dir", identity)
            child = _open_directory(directory_fd, name, identity, directory_flags)
            try:
                _scan_directory(child, relative + "/", depth + 1, catalog, directory_flags)
            finally:
                _close_quietly(child)
        elif stat.S_ISREG(mode):
            catalog[relative] = ("file", identity)
        else:
            # FIFOs, sockets and devices are refused and never opened.
            raise DeepSeekHarnessContractError("path_forbidden") from None


def _hash_ref(
    root_fd: int,
    ref: str,
    catalog: _Catalog,
    directory_flags: int,
    file_flags: int,
) -> tuple[str, int]:
    record = catalog.get(ref)
    if record is None or record[0] != "file":
        raise DeepSeekHarnessContractError("workspace_ref_not_file") from None
    parts = ref.split("/")
    opened: list[int] = []
    current = root_fd
    try:
        for index in range(len(parts) - 1):
            directory = catalog.get("/".join(parts[: index + 1]))
            if directory is None or directory[0] != "dir":
                raise DeepSeekHarnessContractError("workspace_changed") from None
            current = _open_directory(current, parts[index], directory[1], directory_flags)
            opened.append(current)
        return _hash_file(current, parts[-1], record[1], file_flags)
    finally:
        for descriptor in opened:
            _close_quietly(descriptor)


def _hash_file(
    directory_fd: int, name: str, identity: tuple[int, int], file_flags: int
) -> tuple[str, int]:
    try:
        file_fd = os.open(name, file_flags, dir_fd=directory_fd)
    except OSError as exc:
        code = "symlink_forbidden" if exc.errno == errno.ELOOP else "workspace_changed"
        raise DeepSeekHarnessContractError(code) from None
    try:
        before = _fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise DeepSeekHarnessContractError("path_forbidden") from None
        if (before.st_dev, before.st_ino) != identity:
            raise DeepSeekHarnessContractError("workspace_changed") from None
        if before.st_size > MAX_FILE_BYTES:
            raise DeepSeekHarnessContractError("workspace_ref_too_large") from None
        digest = hashlib.sha256()
        size = 0
        while True:
            try:
                chunk = os.read(file_fd, _READ_CHUNK)
            except OSError:
                raise DeepSeekHarnessContractError("workspace_changed") from None
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_FILE_BYTES:
                raise DeepSeekHarnessContractError("workspace_ref_too_large") from None
            digest.update(chunk)
        after = _fstat(file_fd)
        if (
            size != before.st_size
            or after.st_size != before.st_size
            or after.st_mtime_ns != before.st_mtime_ns
        ):
            raise DeepSeekHarnessContractError("workspace_changed") from None
        return f"sha256:{digest.hexdigest()}", size
    finally:
        _close_quietly(file_fd)


def _open_directory(
    parent_fd: int, name: str, identity: tuple[int, int], directory_flags: int
) -> int:
    try:
        child = os.open(name, directory_flags, dir_fd=parent_fd)
    except OSError as exc:
        code = "symlink_forbidden" if exc.errno == errno.ELOOP else "fixture_root_invalid"
        raise DeepSeekHarnessContractError(code) from None
    try:
        opened = _fstat(child)
        if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino) != identity:
            raise DeepSeekHarnessContractError("workspace_changed") from None
    except BaseException:
        _close_quietly(child)
        raise
    return child


def _lstat_at(directory_fd: int, name: str, failure_code: str) -> os.stat_result:
    try:
        return os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except OSError:
        raise DeepSeekHarnessContractError(failure_code) from None


def _fstat(descriptor: int) -> os.stat_result:
    try:
        return os.fstat(descriptor)
    except OSError:
        raise DeepSeekHarnessContractError("workspace_changed") from None


def _close_quietly(descriptor: int) -> None:
    try:
        os.close(descriptor)
    except OSError:
        pass
