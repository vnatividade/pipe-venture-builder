from __future__ import annotations

from dataclasses import replace
from typing import Any
from unittest import TestCase

from pipe_venture_builder.adapters.deepseek_harness import SessionBinding, SessionRegistry
from tests.deepseek_harness.helpers import (
    CONSUMER_ID,
    CONTEXT_FINGERPRINT,
    DSH_VERSION,
    FINGERPRINT,
    MODEL_ID,
    OTHER_CONSUMER_ID,
    OTHER_MODEL_ID,
    OTHER_ROUTE_ID,
    OTHER_RUN_ID,
    PLUGIN_TREE_FINGERPRINT,
    PROFILE_ID,
    PROTOCOL_VERSION,
    ROUTE_ID,
    RUN_ID,
    SECRET_SENTINEL,
    SESSION_ONE,
    SESSION_THREE,
    SESSION_TWO,
    TEXT_SENTINEL,
    WORKSPACE_FINGERPRINT,
    assert_blocked,
    assert_metadata_only,
    binding_fields,
    build_binding,
    build_context,
    fixture_base,
    make_fixture_root,
)


INVALID_IDENTIFIERS = ("", None, 42, "has space", "/absolute", SECRET_SENTINEL, f"raw {TEXT_SENTINEL}")
INVALID_FINGERPRINTS = (
    "",
    None,
    1,
    "sha256:abc",
    "sha256:" + "A" * 64,
    "md5:" + "1" * 32,
    "1" * 64,
    SECRET_SENTINEL,
)


class SessionBindingTests(TestCase):
    """C1 binding contract: every ADR-004 D3 element, named per element."""

    def assert_element_is_bound(self, **changes: Any) -> None:
        """The element is covered by the binding fingerprint and never rewritten.

        A change on the bound attempt is refused; the same change is accepted
        only as a new attempt with a new session, leaving the original intact.
        """

        original = build_binding()
        changed = build_binding(**changes)
        self.assertNotEqual(changed.binding_fingerprint, original.binding_fingerprint)

        registry = SessionRegistry()
        registry.bind(original)
        assert_blocked(self, "binding_immutable", registry.bind, changed)
        self.assertEqual(registry.lineage(RUN_ID), (original,))

        successor = build_binding(session_id=SESSION_TWO, attempt=2, **changes)
        self.assertEqual(registry.bind(successor), successor)
        self.assertEqual(registry.lineage(RUN_ID), (original, successor))
        self.assertEqual(registry.lineage(RUN_ID)[0], build_binding())

    def assert_field_rejects(self, field: str, code: str, values: tuple[Any, ...]) -> None:
        for value in values:
            with self.subTest(field=field, value=value):
                assert_blocked(self, code, build_binding, **{field: value})

    def test_binding_document_carries_every_d3_element_as_metadata_only(self) -> None:
        binding = build_binding()
        document = binding.document()
        expected = {
            "pipeRunId": RUN_ID,
            "sessionId": SESSION_ONE,
            "attempt": 1,
            "dshVersion": DSH_VERSION,
            "protocolVersion": PROTOCOL_VERSION,
            "profileId": PROFILE_ID,
            "pluginTreeFingerprint": PLUGIN_TREE_FINGERPRINT,
            "routeId": ROUTE_ID,
            "modelId": MODEL_ID,
            "workspaceFingerprint": WORKSPACE_FINGERPRINT,
            "contextFingerprint": CONTEXT_FINGERPRINT,
            "consumerId": CONSUMER_ID,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(document[key], value)
        self.assertEqual(document["bindingFingerprint"], binding.binding_fingerprint)
        self.assertRegex(binding.binding_fingerprint, FINGERPRINT)
        assert_metadata_only(self, document)

    def test_binding_fingerprint_is_deterministic(self) -> None:
        self.assertEqual(build_binding(), build_binding())
        self.assertEqual(
            build_binding().binding_fingerprint, build_binding().binding_fingerprint
        )

    def test_binding_element_pipe_run_session_and_attempt(self) -> None:
        binding = build_binding()
        self.assertEqual(
            (binding.pipe_run_id, binding.session_id, binding.attempt),
            (RUN_ID, SESSION_ONE, 1),
        )
        for changes in (
            {"pipe_run_id": OTHER_RUN_ID},
            {"session_id": SESSION_TWO},
            {"attempt": 2},
        ):
            with self.subTest(changes=changes):
                self.assertNotEqual(
                    build_binding(**changes).binding_fingerprint,
                    binding.binding_fingerprint,
                )
        self.assert_field_rejects(
            "pipe_run_id",
            "binding_field_invalid",
            ("run-0123456789ab", "RUN-XYZ", "RUN-0123456789abc", "RP-0123456789ab", "", None),
        )
        self.assert_field_rejects("session_id", "binding_field_invalid", INVALID_IDENTIFIERS)
        self.assert_field_rejects(
            "attempt", "binding_field_invalid", (0, -1, True, False, "1", 1.0, None)
        )

        registry = SessionRegistry()
        registry.bind(binding)
        with self.subTest(case="new session on the bound attempt"):
            assert_blocked(
                self, "binding_immutable", registry.bind, build_binding(session_id=SESSION_TWO)
            )
        with self.subTest(case="bound session reused by the next attempt"):
            assert_blocked(self, "binding_immutable", registry.bind, build_binding(attempt=2))
        with self.subTest(case="bound session reused by another run"):
            assert_blocked(
                self,
                "binding_immutable",
                registry.bind,
                build_binding(pipe_run_id=OTHER_RUN_ID),
            )
        self.assertEqual(registry.lineage(RUN_ID), (binding,))
        self.assertEqual(registry.lineage(OTHER_RUN_ID), ())

    def test_binding_element_dsh_and_protocol_versions(self) -> None:
        self.assert_field_rejects("dsh_version", "binding_field_invalid", INVALID_IDENTIFIERS)
        self.assert_field_rejects(
            "protocol_version", "binding_field_invalid", INVALID_IDENTIFIERS
        )
        for changes in (
            {"dsh_version": "dsh-v0.1.2-alpha.6"},
            {"protocol_version": "dsh-protocol-next"},
        ):
            with self.subTest(changes=changes):
                self.assert_element_is_bound(**changes)

    def test_binding_element_profile_and_plugin_tree_hash(self) -> None:
        self.assert_field_rejects("profile_id", "binding_field_invalid", INVALID_IDENTIFIERS)
        self.assert_field_rejects(
            "plugin_tree_fingerprint", "fingerprint_invalid", INVALID_FINGERPRINTS
        )
        # ADR-004 D9: sdk-minimal exposes danger-full-access, shell and editor.
        self.assert_field_rejects(
            "profile_id",
            "profile_forbidden",
            ("sdk-minimal", "SDK-Minimal", "danger-full-access"),
        )
        for changes in (
            {"profile_id": "pipe-readonly-check"},
            {"plugin_tree_fingerprint": "sha256:" + "9" * 64},
        ):
            with self.subTest(changes=changes):
                self.assert_element_is_bound(**changes)

    def test_binding_element_route_and_model_are_synthetic_allowlisted(self) -> None:
        real_looking = (
            "deepseek-chat",
            "deepseek-reasoner",
            "deepseek/deepseek-v3",
            "ollama/gpt-oss:20b",
            "gpt-oss-20b",
            "openai-compatible",
            "",
            None,
            SECRET_SENTINEL,
        )
        self.assert_field_rejects(
            "route_id", "route_not_allowlisted", (*real_looking, "synthetic-route-c", MODEL_ID)
        )
        self.assert_field_rejects(
            "model_id", "model_not_allowlisted", (*real_looking, "synthetic-model-c", ROUTE_ID)
        )
        for changes in ({"route_id": OTHER_ROUTE_ID}, {"model_id": OTHER_MODEL_ID}):
            with self.subTest(changes=changes):
                self.assert_element_is_bound(**changes)

    def test_binding_element_workspace_and_context_hashes(self) -> None:
        self.assert_field_rejects(
            "workspace_fingerprint", "fingerprint_invalid", INVALID_FINGERPRINTS
        )
        self.assert_field_rejects(
            "context_fingerprint", "fingerprint_invalid", INVALID_FINGERPRINTS
        )
        for changes in (
            {"workspace_fingerprint": "sha256:" + "7" * 64},
            {"context_fingerprint": "sha256:" + "8" * 64},
        ):
            with self.subTest(changes=changes):
                self.assert_element_is_bound(**changes)

    def test_binding_element_single_consumer(self) -> None:
        self.assert_field_rejects("consumer_id", "binding_field_invalid", INVALID_IDENTIFIERS)
        original = build_binding()
        self.assertNotEqual(
            build_binding(consumer_id=OTHER_CONSUMER_ID).binding_fingerprint,
            original.binding_fingerprint,
        )

        registry = SessionRegistry()
        registry.bind(original)
        for case, candidate in (
            ("same binding", build_binding(consumer_id=OTHER_CONSUMER_ID)),
            ("same session, next attempt", build_binding(consumer_id=OTHER_CONSUMER_ID, attempt=2)),
            (
                "same attempt, new session",
                build_binding(consumer_id=OTHER_CONSUMER_ID, session_id=SESSION_TWO),
            ),
        ):
            with self.subTest(case=case):
                assert_blocked(self, "consumer_conflict", registry.bind, candidate)
        self.assertEqual(registry.lineage(RUN_ID), (original,))

    def test_binding_element_forward_only_lineage(self) -> None:
        registry = SessionRegistry()
        with self.subTest(case="lineage starts at attempt one"):
            assert_blocked(self, "lineage_invalid", registry.bind, build_binding(attempt=2))
        self.assertEqual(registry.lineage(RUN_ID), ())

        first = registry.bind(build_binding())
        with self.subTest(case="attempts are contiguous"):
            assert_blocked(
                self,
                "lineage_invalid",
                registry.bind,
                build_binding(session_id=SESSION_THREE, attempt=3),
            )
        second = registry.bind(build_binding(session_id=SESSION_TWO, attempt=2))
        with self.subTest(case="an attempt already in the lineage is never bound again"):
            assert_blocked(
                self,
                "binding_immutable",
                registry.bind,
                build_binding(session_id=SESSION_THREE, attempt=1),
            )
        self.assertEqual(registry.lineage(RUN_ID), (first, second))
        self.assertIsInstance(registry.lineage(RUN_ID), tuple)

        other = registry.bind(build_binding(pipe_run_id=OTHER_RUN_ID, session_id=SESSION_THREE))
        self.assertEqual(registry.lineage(OTHER_RUN_ID), (other,))
        self.assertEqual(registry.lineage(RUN_ID), (first, second))

    def test_binding_is_immutable_and_document_is_a_copy(self) -> None:
        binding = build_binding()
        with self.assertRaises(AttributeError):
            binding.attempt = 5  # type: ignore[misc]
        document = binding.document()
        document["attempt"] = 9
        document["routeId"] = "deepseek-chat"
        self.assertEqual(binding.document()["attempt"], 1)
        self.assertEqual(binding.document()["routeId"], ROUTE_ID)

    def test_direct_constructor_and_replace_are_validated_without_echo(self) -> None:
        for code, changes in (
            ("route_not_allowlisted", {"route_id": "deepseek-chat"}),
            ("route_not_allowlisted", {"route_id": SECRET_SENTINEL}),
            ("binding_field_invalid", {"attempt": 0}),
            ("binding_field_invalid", {"attempt": True}),
        ):
            with self.subTest(path="constructor", changes=changes):
                assert_blocked(self, code, SessionBinding, **binding_fields(**changes))
            with self.subTest(path="replace", changes=changes):
                assert_blocked(self, code, replace, build_binding(), **changes)

    def test_build_requires_every_element(self) -> None:
        for field in binding_fields():
            with self.subTest(missing=field):
                fields = binding_fields()
                del fields[field]
                with self.assertRaises(TypeError):
                    SessionBinding.build(**fields)


class SessionRegistryTests(TestCase):
    """Registry is in-memory, per instance, and the only way to bind a session."""

    def test_bind_returns_binding_and_records_lineage(self) -> None:
        registry = SessionRegistry()
        binding = build_binding()
        self.assertEqual(registry.bind(binding), binding)
        self.assertEqual(registry.lineage(RUN_ID), (binding,))
        self.assertEqual(registry.lineage(OTHER_RUN_ID), ())

    def test_registries_do_not_share_state(self) -> None:
        first = SessionRegistry()
        first.bind(build_binding())
        second = SessionRegistry()
        self.assertEqual(second.lineage(RUN_ID), ())
        self.assertEqual(second.bind(build_binding()), build_binding())

    def test_identical_rebind_is_rejected(self) -> None:
        registry = SessionRegistry()
        binding = registry.bind(build_binding())
        assert_blocked(self, "binding_immutable", registry.bind, build_binding())
        self.assertEqual(registry.lineage(RUN_ID), (binding,))

    def test_bind_rejects_values_that_are_not_bindings(self) -> None:
        registry = SessionRegistry()
        for value in (None, binding_fields(), build_binding().document()):
            with self.subTest(value=type(value).__name__):
                assert_blocked(self, "binding_field_invalid", registry.bind, value)
        self.assertEqual(registry.lineage(RUN_ID), ())

    def test_resolve_accepts_only_latest_attempt_same_consumer_and_context(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            context = build_context(root)
            divergent = build_context(root, workflow="check")
            bound = {
                "workspace_fingerprint": context.workspace_fingerprint,
                "context_fingerprint": context.context_fingerprint,
            }
            registry = SessionRegistry()
            first = registry.bind(build_binding(**bound))
            request = {
                "pipe_run_id": RUN_ID,
                "session_id": SESSION_ONE,
                "attempt": 1,
                "consumer_id": CONSUMER_ID,
                "context": context,
            }
            self.assertEqual(registry.resolve(**request), first)

            for case, code, changes in (
                ("divergent context", "context_mismatch", {"context": divergent}),
                ("second consumer", "consumer_conflict", {"consumer_id": OTHER_CONSUMER_ID}),
                ("unknown session", "binding_unknown", {"session_id": SESSION_TWO}),
                ("wrong attempt", "binding_unknown", {"attempt": 2}),
                ("wrong run", "binding_unknown", {"pipe_run_id": OTHER_RUN_ID}),
            ):
                with self.subTest(case=case):
                    assert_blocked(
                        self,
                        code,
                        registry.resolve,
                        forbidden=(str(base),),
                        **{**request, **changes},
                    )

            second = registry.bind(build_binding(session_id=SESSION_TWO, attempt=2, **bound))
            with self.subTest(case="superseded attempt"):
                assert_blocked(self, "binding_superseded", registry.resolve, **request)
            self.assertEqual(
                registry.resolve(**{**request, "session_id": SESSION_TWO, "attempt": 2}),
                second,
            )
