from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.adapters.hermes.checkpoint import HermesCheckpointStore
from pipe_venture_builder.control_plane.model import (
    ControlPlaneStateError,
    fingerprint,
    stable_id,
)
from tests.hermes.helpers import BEGIN_AT, SESSION_ONE


def checkpoint_document() -> dict[str, object]:
    run_id = stable_id("RUN", "hermes-test")
    plan_id = stable_id("RP", "hermes-plan")
    request_fingerprint = fingerprint({"request": "safe"})
    return {
        "schemaVersion": "0.1.0",
        "runId": run_id,
        "planId": plan_id,
        "productId": "example-product",
        "linearTicketId": "PIP-713",
        "workflow": "adopt",
        "artifactRefs": ["README.md"],
        "requestFingerprint": request_fingerprint,
        "dispatchToken": stable_id(
            "HD", {"runId": run_id, "requestFingerprint": request_fingerprint}
        ),
        "sessionId": SESSION_ONE,
        "sessionLineage": [SESSION_ONE],
        "state": "running",
        "attempt": 1,
        "pendingActionId": None,
        "blockerCode": None,
        "processedEvents": [],
        "updatedAt": BEGIN_AT,
        "constraints": {
            "rawPayloadPersisted": False,
            "credentialsPersisted": False,
            "customerDataPersisted": False,
            "productionDataPersisted": False,
            "hermesApprovalIsAuthority": False,
            "externalMutationAllowed": False,
        },
    }


class HermesCheckpointStoreTests(TestCase):
    def test_checkpoint_is_atomic_private_and_reopenable(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state"
            store = HermesCheckpointStore(path)
            saved = store.save(checkpoint_document())
            checkpoint_path = path / f"{saved['runId']}.json"

            self.assertEqual(os.stat(path).st_mode & 0o777, 0o700)
            self.assertEqual(os.stat(checkpoint_path).st_mode & 0o777, 0o600)
            self.assertEqual(store.load(saved["runId"]), saved)

    def test_tampered_checkpoint_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            store = HermesCheckpointStore(directory)
            saved = store.save(checkpoint_document())
            path = Path(directory) / f"{saved['runId']}.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            document["state"] = "completed"
            path.write_text(json.dumps(document), encoding="utf-8")

            with self.assertRaises(ControlPlaneStateError):
                store.load(saved["runId"])

    def test_checkpoint_directory_symlink_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / "target"
            target.mkdir()
            link = base / "link"
            link.symlink_to(target, target_is_directory=True)

            with self.assertRaises(ControlPlaneStateError):
                HermesCheckpointStore(link)
