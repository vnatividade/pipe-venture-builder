from __future__ import annotations

import json
import os
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from unittest import TestCase, mock

from pipe_venture_builder.adapters.deepseek_harness import DeepSeekHarnessCheckpointStore
from pipe_venture_builder.control_plane.model import canonical_json, fingerprint
from tests.deepseek_harness.helpers import (
    BEGIN_AT,
    CONTEXT_FINGERPRINT,
    RUN_ID,
    SECRET_SENTINEL,
    SESSION_ONE,
    SESSION_TWO,
    TEXT_SENTINEL,
    TICKET_ID,
    WORKSPACE_FINGERPRINT,
    assert_blocked,
    assert_metadata_only,
    fixture_base,
    forbid_host_access,
)


CONSTRAINTS = {
    "rawPayloadPersisted": False,
    "credentialsPersisted": False,
    "runtimeApprovalIsAuthority": False,
    "runtimeCompletionIsAuthority": False,
    "externalMutationAllowed": False,
}


def processed(sequence: int, kind: str = "turn.started") -> dict[str, Any]:
    return {
        "eventId": f"DHE-{sequence:012x}",
        "sequence": sequence,
        "fingerprint": "sha256:" + f"{sequence:x}" * 64,
        "kind": kind,
    }


def checkpoint_document(**overrides: Any) -> dict[str, Any]:
    """A synthetic, metadata-only checkpoint authored for the tests."""

    document: dict[str, Any] = {
        "schemaVersion": "0.1.0",
        "runId": RUN_ID,
        "planId": "RP-0123456789ab",
        "planFingerprint": "sha256:" + "5" * 64,
        "linearTicketId": TICKET_ID,
        "workflow": "review",
        "contextFingerprint": CONTEXT_FINGERPRINT,
        "workspaceFingerprint": WORKSPACE_FINGERPRINT,
        "sessionId": SESSION_ONE,
        "attempt": 1,
        "bindingFingerprint": "sha256:" + "6" * 64,
        "dispatchId": "DHD-0123456789ab",
        "sessionLineage": [SESSION_ONE],
        "state": "running",
        "expectedSequence": 2,
        "processedEvents": [processed(1)],
        "pendingEvent": None,
        "blockerCode": None,
        "proposalFingerprint": None,
        "updatedAt": BEGIN_AT,
        "constraints": dict(CONSTRAINTS),
    }
    document.update(overrides)
    return document


def mode_of(path: Path) -> int:
    return stat.S_IMODE(os.lstat(path).st_mode)


@contextmanager
def umask(value: int) -> Iterator[None]:
    previous = os.umask(value)
    try:
        yield
    finally:
        os.umask(previous)


class CheckpointStoreTests(TestCase):
    """ADR-004 D5/D7: own atomic, fingerprinted checkpoint; never follow a symlink."""

    def test_round_trip_is_fingerprinted_canonical_and_metadata_only(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            self.assertIsNone(store.load(RUN_ID))
            saved = store.save(checkpoint_document())
            self.assertRegex(saved["checkpointFingerprint"], r"^sha256:[a-f0-9]{64}$")
            unsigned = {k: v for k, v in saved.items() if k != "checkpointFingerprint"}
            self.assertEqual(saved["checkpointFingerprint"], fingerprint(unsigned))
            self.assertEqual(store.load(RUN_ID), saved)
            assert_metadata_only(self, saved)
            raw = (base / "checkpoints" / f"{RUN_ID}.json").read_text(encoding="utf-8")
            self.assertEqual(raw, canonical_json(saved) + "\n")
            self.assertNotIn(str(base), raw)

            # Saving again re-signs; a stale supplied fingerprint is ignored.
            again = store.save({**saved, "expectedSequence": 3, "processedEvents": [processed(1), processed(2)]})
            self.assertNotEqual(again["checkpointFingerprint"], saved["checkpointFingerprint"])
            self.assertEqual(store.load(RUN_ID), again)

    def test_directory_is_0700_and_file_is_0600_regardless_of_umask(self) -> None:
        with fixture_base() as base, umask(0):
            store = DeepSeekHarnessCheckpointStore(base / "fresh")
            self.assertEqual(mode_of(base / "fresh"), 0o700)
            store.save(checkpoint_document())
            path = base / "fresh" / f"{RUN_ID}.json"
            self.assertEqual(mode_of(path), 0o600)
            store.save(checkpoint_document(updatedAt="2026-09-10T12:05:00Z"))
            self.assertEqual(mode_of(path), 0o600)

            loose = base / "loose"
            loose.mkdir(mode=0o755)
            os.chmod(loose, 0o755)
            DeepSeekHarnessCheckpointStore(loose)
            self.assertEqual(mode_of(loose), 0o700)

    def test_checkpoint_directory_path_must_be_absolute_and_canonical(self) -> None:
        with fixture_base() as base:
            for value in ("relative/checkpoints", str(base / ".." / "x"), "", None, 7, "/"):
                with self.subTest(value=repr(value)[:24]):
                    assert_blocked(
                        self, "checkpoint_path_invalid", DeepSeekHarnessCheckpointStore, value,
                        forbidden=(str(base),),
                    )
            (base / "file").write_text("x", encoding="utf-8")
            assert_blocked(
                self, "checkpoint_path_invalid", DeepSeekHarnessCheckpointStore, base / "file",
                forbidden=(str(base),),
            )
            assert_blocked(
                self, "checkpoint_path_invalid", DeepSeekHarnessCheckpointStore,
                base / "missing-parent" / "checkpoints", forbidden=(str(base),),
            )

    def test_symlinked_directory_or_ancestor_is_refused_even_with_internal_target(self) -> None:
        with fixture_base() as base:
            real = base / "real"
            (real / "checkpoints").mkdir(parents=True)
            (base / "link").symlink_to(real / "checkpoints", target_is_directory=True)
            (base / "alias").symlink_to(real, target_is_directory=True)
            for path in (base / "link", base / "alias" / "checkpoints", base / "alias" / "new"):
                with self.subTest(path=path.name):
                    assert_blocked(
                        self, "symlink_forbidden", DeepSeekHarnessCheckpointStore, path,
                        forbidden=(str(base),),
                    )
            self.assertFalse((real / "new").exists())
            self.assertEqual(list((real / "checkpoints").iterdir()), [])

    def test_symlinked_checkpoint_file_is_refused_without_following(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            saved = store.save(checkpoint_document())
            path = base / "checkpoints" / f"{RUN_ID}.json"
            internal = base / "checkpoints" / "internal-copy.json"
            path.rename(internal)
            path.symlink_to(internal.name)
            before = internal.read_bytes()
            assert_blocked(self, "symlink_forbidden", store.load, RUN_ID, forbidden=(str(base),))
            assert_blocked(
                self, "symlink_forbidden", store.save, checkpoint_document(state="running"),
                forbidden=(str(base),),
            )
            self.assertTrue(path.is_symlink())
            self.assertEqual(internal.read_bytes(), before)
            self.assertEqual(json.loads(before), saved)

    def test_directory_swapped_after_construction_is_refused(self) -> None:
        with fixture_base() as base:
            directory = base / "checkpoints"
            store = DeepSeekHarnessCheckpointStore(directory)
            store.save(checkpoint_document())
            directory.rename(base / "moved")
            directory.symlink_to(base / "moved", target_is_directory=True)
            assert_blocked(self, "symlink_forbidden", store.load, RUN_ID, forbidden=(str(base),))
            directory.unlink()
            directory.mkdir(mode=0o700)
            for operation, args in ((store.load, (RUN_ID,)), (store.save, (checkpoint_document(),))):
                with self.subTest(operation=operation.__name__):
                    assert_blocked(
                        self, "checkpoint_path_changed", operation, *args, forbidden=(str(base),)
                    )
            self.assertEqual(list(directory.iterdir()), [])

    def test_tampered_or_malformed_file_is_refused(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            saved = store.save(checkpoint_document())
            path = base / "checkpoints" / f"{RUN_ID}.json"
            changed = {**saved, "expectedSequence": 9}
            reshaped = {k: v for k, v in saved.items() if k != "checkpointFingerprint"}
            reshaped["prompt"] = TEXT_SENTINEL
            reshaped["checkpointFingerprint"] = fingerprint(reshaped)
            cases = {
                "field changed, fingerprint kept": ("checkpoint_tampered", canonical_json(changed) + "\n"),
                "raw key with recomputed fingerprint": (
                    "checkpoint_invalid", canonical_json(reshaped) + "\n",
                ),
                "non-canonical encoding": ("checkpoint_invalid", json.dumps(saved, indent=2)),
                "not json": ("checkpoint_invalid", "{" + SECRET_SENTINEL),
                "empty": ("checkpoint_invalid", ""),
                "json list": ("checkpoint_invalid", "[]\n"),
            }
            for name, (code, content) in cases.items():
                with self.subTest(case=name):
                    path.write_text(content, encoding="utf-8")
                    os.chmod(path, 0o600)
                    assert_blocked(self, code, store.load, RUN_ID, forbidden=(str(base),))

    def test_file_mode_type_and_link_count_are_validated(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            store.save(checkpoint_document())
            path = base / "checkpoints" / f"{RUN_ID}.json"
            for mode in (0o644, 0o640, 0o400, 0o700):
                with self.subTest(mode=oct(mode)):
                    os.chmod(path, mode)
                    assert_blocked(
                        self, "checkpoint_mode_invalid", store.load, RUN_ID, forbidden=(str(base),)
                    )
            os.chmod(path, 0o600)
            os.link(path, base / "hardlink.json")
            assert_blocked(self, "checkpoint_invalid", store.load, RUN_ID, forbidden=(str(base),))
            (base / "hardlink.json").unlink()
            path.unlink()
            path.mkdir()
            assert_blocked(self, "checkpoint_invalid", store.load, RUN_ID, forbidden=(str(base),))

    def test_invalid_document_is_refused_before_anything_is_written(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            bad = {
                "raw prompt key": checkpoint_document(prompt=TEXT_SENTINEL),
                "missing field": {
                    k: v for k, v in checkpoint_document().items() if k != "dispatchId"
                },
                "secret-shaped session": checkpoint_document(
                    sessionId=SECRET_SENTINEL, sessionLineage=[SECRET_SENTINEL]
                ),
                "lineage does not end at session": checkpoint_document(
                    sessionLineage=[SESSION_TWO]
                ),
                "lineage length differs from attempt": checkpoint_document(
                    attempt=2, sessionLineage=[SESSION_ONE]
                ),
                "sequence gap in processed events": checkpoint_document(
                    expectedSequence=3, processedEvents=[processed(1), processed(3)]
                ),
                "expected sequence inconsistent": checkpoint_document(expectedSequence=5),
                "duplicate event identity": checkpoint_document(
                    expectedSequence=3,
                    processedEvents=[processed(1), {**processed(2), "eventId": processed(1)["eventId"]}],
                ),
                "unknown event kind": checkpoint_document(
                    processedEvents=[processed(1, kind="message.delta")]
                ),
                "pending event out of sequence": checkpoint_document(pendingEvent=processed(4)),
                "unknown state": checkpoint_document(state="approved"),
                "blocked without blocker": checkpoint_document(state="blocked"),
                "blocker outside the code set": checkpoint_document(
                    state="blocked", blockerCode=TEXT_SENTINEL
                ),
                "completed without a proposal": checkpoint_document(state="completed"),
                "malformed proposal fingerprint": checkpoint_document(proposalFingerprint="sha256:x"),
                "authority constraint flipped": checkpoint_document(
                    constraints={**CONSTRAINTS, "runtimeApprovalIsAuthority": True}
                ),
                "absolute path leaked": checkpoint_document(dispatchId=str(base)),
                "not a mapping": [checkpoint_document()],
            }
            for name, document in bad.items():
                with self.subTest(case=name):
                    assert_blocked(
                        self, "checkpoint_invalid", store.save, document, forbidden=(str(base),)
                    )
                    self.assertEqual(list((base / "checkpoints").iterdir()), [])

    def test_interrupted_write_never_replaces_the_valid_checkpoint(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            valid = store.save(checkpoint_document())
            path = base / "checkpoints" / f"{RUN_ID}.json"
            before = path.read_bytes()
            newer = checkpoint_document(
                expectedSequence=3, processedEvents=[processed(1), processed(2)]
            )
            real_write = os.write

            def partial_write(fd: int, data: bytes) -> int:
                real_write(fd, bytes(data)[: len(data) // 2])
                raise OSError("disk full")

            for name, target, effect in (
                ("partial write", "os.write", partial_write),
                ("fsync failure", "os.fsync", OSError("io error")),
                ("rename failure", "os.replace", OSError("io error")),
            ):
                with self.subTest(case=name):
                    with mock.patch(target, side_effect=effect):
                        assert_blocked(
                            self, "checkpoint_write_failed", store.save, newer,
                            forbidden=(str(base),),
                        )
                    self.assertEqual(path.read_bytes(), before)
                    self.assertEqual(store.load(RUN_ID), valid)
                    self.assertEqual(
                        sorted(item.name for item in (base / "checkpoints").iterdir()),
                        [path.name],
                    )

    def test_run_identifier_is_validated_before_any_path_is_built(self) -> None:
        with fixture_base() as base:
            store = DeepSeekHarnessCheckpointStore(base / "checkpoints")
            for value in ("../RUN-0123456789ab", "RUN-XYZ", "", None, f"{RUN_ID}/x"):
                with self.subTest(value=repr(value)[:24]):
                    assert_blocked(self, "checkpoint_invalid", store.load, value)
            assert_blocked(
                self, "checkpoint_invalid", store.save, checkpoint_document(runId="../x")
            )

    def test_store_never_touches_host_environment_or_processes(self) -> None:
        with fixture_base() as base:
            directory = base / "checkpoints"
            with forbid_host_access(filesystem=False) as log:
                store = DeepSeekHarnessCheckpointStore(directory)
                store.save(checkpoint_document())
                store.load(RUN_ID)
            self.assertEqual(log, [])
