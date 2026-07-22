from __future__ import annotations

import copy
import json
import os
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.control_plane import LocalControlPlaneStore
from pipe_venture_builder.control_plane.model import ControlPlaneContractError
from tests.control_plane.helpers import DECIDED_AT, approval_for, create_plan


class LocalControlPlaneStoreTests(TestCase):
    def test_secret_shaped_plan_is_rejected_before_persistence(self) -> None:
        plan = copy.deepcopy(create_plan())
        plan["secret"] = "sk-never-persist-this-value-1234567890"

        with LocalControlPlaneStore(":memory:") as store:
            with self.assertRaises(ControlPlaneContractError):
                store.register_plan(plan, at=DECIDED_AT)

    def test_plan_approval_and_events_persist_across_reopen(self) -> None:
        plan = create_plan()
        approval = approval_for(plan)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state" / "control-plane.sqlite3"
            with LocalControlPlaneStore(path) as store:
                run_id = store.register_plan(plan, at=DECIDED_AT)
                self.assertTrue(store.record_approval(approval, at=DECIDED_AT))
                self.assertFalse(store.record_approval(approval, at=DECIDED_AT))
                self.assertTrue(store.verify_audit_chain(run_id))
                for suffix in ("", "-wal", "-shm"):
                    sidecar = Path(f"{path}{suffix}")
                    if sidecar.exists():
                        self.assertEqual(os.stat(sidecar).st_mode & 0o777, 0o600)

            with LocalControlPlaneStore(path) as reopened:
                self.assertEqual(reopened.get_run(run_id)["plan_id"], plan["planId"])
                self.assertEqual(len(reopened.list_events(run_id)), 3)
                self.assertTrue(reopened.verify_audit_chain(run_id))
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)

    def test_tampered_event_breaks_hash_chain(self) -> None:
        plan = create_plan()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "control-plane.sqlite3"
            with LocalControlPlaneStore(path) as store:
                run_id = store.register_plan(plan, at=DECIDED_AT)
            connection = sqlite3.connect(path)
            event = json.loads(
                connection.execute(
                    "SELECT event_json FROM events WHERE run_id = ? AND sequence = 1",
                    (run_id,),
                ).fetchone()[0]
            )
            event["status"] = "failed"
            connection.execute(
                "UPDATE events SET event_json = ? WHERE run_id = ? AND sequence = 1",
                (json.dumps(event), run_id),
            )
            connection.commit()
            connection.close()

            with LocalControlPlaneStore(path) as store:
                self.assertFalse(store.verify_audit_chain(run_id))

    def test_tampered_checkpoint_fails_closed(self) -> None:
        plan = create_plan()
        action = plan["actions"][0]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "control-plane.sqlite3"
            with LocalControlPlaneStore(path) as store:
                run_id = store.register_plan(plan, at=DECIDED_AT)
                store.upsert_checkpoint(
                    run_id=run_id,
                    action_id=action["actionId"],
                    idempotency_key=action["idempotencyKey"],
                    state="pending",
                    attempt=1,
                    approval_id=None,
                    source_fingerprint=plan["baseline"]["fingerprint"],
                    target_fingerprint=action["targetFingerprint"],
                    result_fingerprint=None,
                    result_ref=None,
                    at=DECIDED_AT,
                )
            connection = sqlite3.connect(path)
            connection.execute(
                "UPDATE checkpoints SET state = 'verified' WHERE run_id = ?",
                (run_id,),
            )
            connection.commit()
            connection.close()

            with LocalControlPlaneStore(path) as store:
                with self.assertRaises(RuntimeError):
                    store.get_checkpoint(run_id, action["actionId"])

    def test_symlink_database_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.sqlite3"
            target.touch()
            link = root / "state.sqlite3"
            link.symlink_to(target)

            with self.assertRaises(RuntimeError):
                LocalControlPlaneStore(link)
