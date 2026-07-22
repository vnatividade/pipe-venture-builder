from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.adapters.hermes import HermesRunContext, HermesRuntimeEvent
from pipe_venture_builder.control_plane.model import ControlPlaneContractError
from tests.control_plane.helpers import create_plan
from tests.hermes.helpers import BEGIN_AT, SESSION_ONE, product_root


class HermesModelTests(TestCase):
    def test_context_contains_references_and_no_product_root(self) -> None:
        plan = create_plan()
        with TemporaryDirectory() as directory:
            root = product_root(Path(directory))
            context = HermesRunContext.build(
                product_id="example-product",
                linear_ticket_id="PIP-713",
                workflow="adopt",
                product_root=root,
                artifact_refs=["product/prd.md", "README.md", "README.md"],
                plan=plan,
            )

        document = context.document()
        self.assertEqual(document["artifactRefs"], ["README.md", "product/prd.md"])
        self.assertNotIn("productRoot", document)
        self.assertFalse(document["constraints"]["hermesApprovalIsAuthority"])
        self.assertFalse(document["constraints"]["externalMutationAllowed"])

    def test_context_rejects_traversal_and_external_symlink(self) -> None:
        plan = create_plan()
        with TemporaryDirectory() as directory:
            base = Path(directory)
            root = product_root(base)
            outside = base / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            (root / "linked.md").symlink_to(outside)
            for ref in ("../outside.md", "linked.md"):
                with self.subTest(ref=ref), self.assertRaises(ControlPlaneContractError):
                    HermesRunContext.build(
                        product_id="example-product",
                        linear_ticket_id="PIP-713",
                        workflow="adopt",
                        product_root=root,
                        artifact_refs=[ref],
                        plan=plan,
                    )

    def test_context_requires_ticket_and_supported_workflow(self) -> None:
        plan = create_plan()
        with TemporaryDirectory() as directory:
            root = product_root(Path(directory))
            with self.assertRaises(ControlPlaneContractError):
                HermesRunContext.build(
                    product_id="example-product",
                    linear_ticket_id="idea-note",
                    workflow="adopt",
                    product_root=root,
                    artifact_refs=["README.md"],
                    plan=plan,
                )
            with self.assertRaises(ControlPlaneContractError):
                HermesRunContext.build(
                    product_id="example-product",
                    linear_ticket_id="PIP-713",
                    workflow="deploy",
                    product_root=root,
                    artifact_refs=["README.md"],
                    plan=plan,
                )

    def test_runtime_event_is_normalized_and_payload_free(self) -> None:
        event = HermesRuntimeEvent.build(
            external_event_id="evt-1",
            kind="tool.succeeded",
            session_id=SESSION_ONE,
            occurred_at=BEGIN_AT,
            tool_name="read_file",
            result_ref="artifact:prd",
            payload_fingerprint=("sha256:" + "1" * 64),
        )

        document = event.document()
        self.assertRegex(document["eventId"], r"^HE-[a-f0-9]{12}$")
        self.assertNotIn("payload", document)
        self.assertFalse(document["constraints"]["rawPayloadPersisted"])

    def test_runtime_event_rejects_unknown_kind_and_secret_shape(self) -> None:
        with self.assertRaises(ControlPlaneContractError):
            HermesRuntimeEvent.build(
                external_event_id="evt-1",
                kind="shell.executed",
                session_id=SESSION_ONE,
                occurred_at=BEGIN_AT,
            )
        with self.assertRaises(ControlPlaneContractError):
            HermesRuntimeEvent.build(
                external_event_id="evt-2",
                kind="tool.started",
                session_id=SESSION_ONE,
                occurred_at=BEGIN_AT,
                tool_name="sk-secret-value-12345678901234567890",
            )
