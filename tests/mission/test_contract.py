from __future__ import annotations

import copy
from unittest import TestCase

from jsonschema import Draft202012Validator, FormatChecker

from pipe_venture_builder.control_plane.model import ControlPlaneContractError
from pipe_venture_builder.mission.contract import (
    FINGERPRINT_EXCLUDED_FIELDS,
    SCHEMA_VERSION,
    build_mission,
    mission_fingerprint,
    validate_mission,
)
from tests.mission.helpers import (
    CREATED_AT,
    LATER,
    load_mission_schema,
    mission_input,
    mission_variant,
)


def schema_findings(document: dict) -> list[str]:
    contract = load_mission_schema()
    Draft202012Validator.check_schema(contract)
    validator = Draft202012Validator(contract, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(document)]


class MissionContractTests(TestCase):
    def test_build_mission_produces_valid_document_with_stable_id(self) -> None:
        mission = build_mission(mission_input(), created_at=CREATED_AT)

        self.assertEqual(mission["schemaVersion"], SCHEMA_VERSION)
        self.assertRegex(mission["missionId"], r"^MSN-[a-f0-9]{12}$")
        self.assertEqual(mission["status"], "draft")
        self.assertEqual(mission["createdAt"], CREATED_AT)
        self.assertEqual(mission["updatedAt"], CREATED_AT)
        self.assertRegex(mission["fingerprint"], r"^sha256:[a-f0-9]{64}$")
        self.assertEqual(validate_mission(mission), mission)

    def test_fingerprint_is_stable_and_excludes_status_and_timestamps(self) -> None:
        first = build_mission(mission_input(), created_at=CREATED_AT)
        second = build_mission(mission_input(), created_at=CREATED_AT)
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertEqual(first["missionId"], second["missionId"])
        later = build_mission(mission_input(), created_at="2026-09-11T00:00:00Z")
        self.assertEqual(later["missionId"], first["missionId"], "id is content-only")
        bumped = build_mission(mission_variant(version=2), created_at=CREATED_AT)
        self.assertNotEqual(bumped["missionId"], first["missionId"])

        mutated = copy.deepcopy(first)
        mutated["status"] = "active"
        mutated["updatedAt"] = "2026-09-11T00:00:00Z"
        self.assertEqual(mission_fingerprint(mutated), first["fingerprint"])
        self.assertEqual(
            FINGERPRINT_EXCLUDED_FIELDS,
            frozenset({"status", "createdAt", "updatedAt", "fingerprint"}),
        )

        changed = copy.deepcopy(first)
        changed["title"] = "outro titulo"
        self.assertNotEqual(mission_fingerprint(changed), first["fingerprint"])
        with self.assertRaises(ControlPlaneContractError):
            validate_mission(changed)

    def test_schema_and_contract_agree_on_good_document(self) -> None:
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        self.assertEqual(schema_findings(mission), [])

        schema = load_mission_schema()
        self.assertFalse(schema["additionalProperties"])
        example = schema["examples"][0]
        self.assertEqual(schema_findings(example), [])
        self.assertEqual(validate_mission(example), example)
        flags = schema["properties"]["constraints"]["properties"]
        for name in (
            "productionAllowed",
            "secretsAllowed",
            "externalCommsAllowed",
            "billingAllowed",
        ):
            self.assertFalse(flags[name]["const"])

    def test_schema_and_contract_agree_on_bad_documents(self) -> None:
        good = build_mission(mission_input(), created_at=CREATED_AT)
        # (document overrides, contract message). The fingerprint is recomputed
        # for every case so each one fails for the rule under test, never for
        # "fingerprint does not match content".
        bad_documents = {
            "unknown top-level key": (
                {"extra": 1},
                "mission document has unknown fields",
            ),
            "bad schemaVersion": (
                {"schemaVersion": "9.9.9"},
                "unsupported mission schema version",
            ),
            "empty writeSet": (
                {"workspace": {**good["workspace"], "writeSet": []}},
                "workspace writeSet must be a non-empty list",
            ),
            "bad delivery kind": (
                {"delivery": {"kind": "merge", "requireChecks": True}},
                "invalid delivery kind",
            ),
            "bad status": ({"status": "done"}, "invalid mission status"),
            "flag true": (
                {"constraints": {**good["constraints"], "secretsAllowed": True}},
                "absolute gates cannot be opened by a mission",
            ),
            "criterion without kind": (
                {"successCriteria": [{"id": "C1", "text": "x"}]},
                "success criterion has no verifiable kind",
            ),
        }
        for label, (overrides, message) in bad_documents.items():
            with self.subTest(label):
                document = {**good, **overrides}
                document["fingerprint"] = mission_fingerprint(document)
                self.assertNotEqual(schema_findings(document), [])
                with self.assertRaisesRegex(ControlPlaneContractError, message):
                    validate_mission(document)

    def test_criterion_without_verifiable_shape_is_rejected(self) -> None:
        shapes = {
            "no kind": {"id": "C1", "text": "x"},
            "unknown kind": {"id": "C1", "text": "x", "kind": "vibe"},
            "check without command": {"id": "C1", "text": "x", "kind": "check"},
            "artifact without path": {"id": "C1", "text": "x", "kind": "artifact"},
            "rubric without question": {"id": "C1", "text": "x", "kind": "rubric"},
            "check with artifact field": {
                "id": "C1",
                "text": "x",
                "kind": "check",
                "command": "true",
                "path": "a.md",
            },
            "artifact with bad regex": {
                "id": "C1",
                "text": "x",
                "kind": "artifact",
                "path": "a.md",
                "mustMatch": "(",
            },
            "artifact escaping repo": {
                "id": "C1",
                "text": "x",
                "kind": "artifact",
                "path": "../a.md",
            },
            "check with absolute cwd": {
                "id": "C1",
                "text": "x",
                "kind": "check",
                "command": "true",
                "cwd": "/etc",
            },
        }
        for label, criterion in shapes.items():
            with self.subTest(label):
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(
                        mission_variant(successCriteria=[criterion]),
                        created_at=CREATED_AT,
                    )
        with self.assertRaises(ControlPlaneContractError):
            build_mission(mission_variant(successCriteria=[]), created_at=CREATED_AT)
        duplicate = mission_input()
        duplicate["successCriteria"][1]["id"] = "C1"
        with self.assertRaises(ControlPlaneContractError):
            build_mission(duplicate, created_at=CREATED_AT)

    def test_absolute_gate_flags_set_to_true_are_rejected(self) -> None:
        for flag in (
            "productionAllowed",
            "secretsAllowed",
            "externalCommsAllowed",
            "billingAllowed",
        ):
            with self.subTest(flag):
                document = mission_input()
                document["constraints"][flag] = True
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(document, created_at=CREATED_AT)
        missing = mission_input()
        del missing["constraints"]["billingAllowed"]
        with self.assertRaises(ControlPlaneContractError):
            build_mission(missing, created_at=CREATED_AT)

    def test_constraint_limits_must_be_positive_numbers(self) -> None:
        for key, value in (
            ("maxCycles", 0),
            ("maxCycles", True),
            ("maxCycles", 1.5),
            ("maxBudgetUsd", 0),
            ("maxBudgetUsd", -1),
            ("maxBudgetUsd", "15"),
            ("maxTurnsPerRun", 0),
        ):
            with self.subTest(f"{key}={value!r}"):
                document = mission_input()
                document["constraints"][key] = value
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(document, created_at=CREATED_AT)

    def test_write_set_with_parent_traversal_is_rejected(self) -> None:
        for entry in ("../secrets", "docs/../../etc", "/abs/path", "", ".", "a\\b"):
            with self.subTest(entry):
                document = mission_input()
                document["workspace"]["writeSet"] = ["README.md", entry]
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(document, created_at=CREATED_AT)
        relative_repo = mission_input()
        relative_repo["workspace"]["repo"] = "relative/repo"
        with self.assertRaises(ControlPlaneContractError):
            build_mission(relative_repo, created_at=CREATED_AT)

    def test_secret_shaped_sentinel_is_rejected(self) -> None:
        sentinel = "sk-never-persist-this-value-1234567890"
        cases = {
            "in intent": mission_variant(intent=f"use {sentinel} para autenticar"),
            "in criterion command": mission_variant(
                successCriteria=[
                    {
                        "id": "C1",
                        "text": "x",
                        "kind": "check",
                        "command": f"curl -H 'Authorization: {sentinel}' https://x",
                    }
                ]
            ),
            "forbidden key": mission_variant(token="not-even-secret-shaped"),
        }
        for label, document in cases.items():
            with self.subTest(label):
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(document, created_at=CREATED_AT)

    def test_supplied_ids_and_fingerprint_are_checked_not_trusted(self) -> None:
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        wrong_fingerprint = mission_variant(fingerprint="sha256:" + "0" * 64)
        with self.assertRaises(ControlPlaneContractError):
            build_mission(wrong_fingerprint, created_at=CREATED_AT)
        bad_id = mission_variant(missionId="MSN-not-hex")
        with self.assertRaises(ControlPlaneContractError):
            build_mission(bad_id, created_at=CREATED_AT)
        rebuilt = build_mission(copy.deepcopy(mission), created_at=CREATED_AT)
        self.assertEqual(rebuilt, mission)
        with self.assertRaises(ControlPlaneContractError):
            build_mission(mission_variant(linearTicketIds=["pip 901"]), created_at=CREATED_AT)

    def test_delegation_is_absent_for_v0_1_0_and_optional_null_for_v0_2_0(self) -> None:
        # v0.1.0 (mission_input()'s default): the key never enters the
        # document, so it never enters the fingerprint either — see
        # test_v0_1_0_document_without_delegation_key_is_stable below.
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        self.assertNotIn("delegation", mission)
        self.assertEqual(schema_findings(mission), [])

        rule = {"grantCycle": {"maxTimes": 1, "maxCostFraction": 0.5, "requireProgress": True}}
        with self.assertRaisesRegex(ControlPlaneContractError, "requires schema 0.2.0"):
            build_mission(
                mission_variant(schemaVersion="0.1.0", delegation=rule), created_at=CREATED_AT
            )
        with_delegation = build_mission(
            mission_variant(schemaVersion="0.2.0", delegation=rule), created_at=CREATED_AT
        )
        self.assertEqual(with_delegation["delegation"], rule)
        self.assertEqual(schema_findings(with_delegation), [])

        without_delegation = build_mission(
            mission_variant(schemaVersion="0.2.0"), created_at=CREATED_AT
        )
        self.assertIsNone(without_delegation["delegation"])
        self.assertEqual(schema_findings(without_delegation), [])

    def test_v0_1_0_document_without_delegation_key_is_stable(self) -> None:
        """The mutation this guards against: reintroducing an unconditional
        ``setdefault("delegation", None)`` would change the fingerprint (and
        so the ``missionId``) of every v0.1.0 document already on disk."""

        first = build_mission(mission_input(), created_at=CREATED_AT)
        second = build_mission(mission_variant(), created_at=CREATED_AT)
        self.assertNotIn("delegation", first)
        self.assertNotIn("delegation", second)
        self.assertEqual(first["missionId"], second["missionId"])

    def test_v0_1_0_identity_is_pinned_to_the_value_before_pip_903(self) -> None:
        # Valores calculados com o código de main antes do PIP-903 (927625a).
        # Comparar dois ids do mesmo código não pega mudança de identidade;
        # o literal pega (revisão 2 do PIP-903, achado #4 / mutação M35).
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        self.assertEqual(mission["missionId"], "MSN-ad14c130266c")
        self.assertEqual(
            mission["fingerprint"],
            "sha256:a76cf3a5bd9c001a04f882e46047d2b4cf459a9e1ab6515fa31d9caf69d4b475",
        )

    def test_legacy_v0_1_0_document_without_delegation_key_still_validates(self) -> None:
        """A document written to disk before the delegation key existed at
        all (no ``delegation`` key, whatever the code once defaulted): the
        contract must accept it exactly as it would have pre-PIP-903."""

        legacy = build_mission(mission_input(), created_at=CREATED_AT)
        self.assertNotIn("delegation", legacy)
        self.assertEqual(validate_mission(legacy), legacy)

        mutated = copy.deepcopy(legacy)
        mutated["status"] = "active"
        mutated["updatedAt"] = LATER
        mutated["fingerprint"] = mission_fingerprint(mutated)
        revalidated = validate_mission(mutated)
        self.assertNotIn("delegation", revalidated)
        self.assertEqual(revalidated["status"], "active")

    def test_delegation_key_present_but_unknown_top_level_fields_still_refused(self) -> None:
        legacy = build_mission(mission_input(), created_at=CREATED_AT)
        with_extra = {**legacy, "extra": 1}
        with_extra["fingerprint"] = mission_fingerprint(with_extra)
        with self.assertRaisesRegex(ControlPlaneContractError, "unknown fields"):
            validate_mission(with_extra)

        missing_required = dict(legacy)
        del missing_required["title"]
        with self.assertRaisesRegex(ControlPlaneContractError, "missing required fields"):
            validate_mission(missing_required)

    def test_grant_cycle_rejects_every_boundary_violation(self) -> None:
        good = {"maxTimes": 1, "maxCostFraction": 0.5, "requireProgress": True}
        bad_grant_cycles = {
            "maxTimes 0": {**good, "maxTimes": 0},
            "maxTimes 4": {**good, "maxTimes": 4},
            "maxTimes bool": {**good, "maxTimes": True},
            "maxTimes non-integer": {**good, "maxTimes": 1.5},
            "maxCostFraction 0": {**good, "maxCostFraction": 0},
            "maxCostFraction negative": {**good, "maxCostFraction": -0.1},
            "maxCostFraction above cap": {**good, "maxCostFraction": 0.9},
            "maxCostFraction bool": {**good, "maxCostFraction": True},
            "requireProgress non-bool": {**good, "requireProgress": "yes"},
            "extra key inside grantCycle": {**good, "extra": 1},
        }
        for label, grant_cycle in bad_grant_cycles.items():
            with self.subTest(label):
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(
                        mission_variant(schemaVersion="0.2.0", delegation={"grantCycle": grant_cycle}),
                        created_at=CREATED_AT,
                    )
        # The boundaries this guards must be accepted, not just anything
        # nearby: maxTimes at 1 and 3, and maxCostFraction at 0.8.
        for grant_cycle in (
            {**good, "maxTimes": 1},
            {**good, "maxTimes": 3},
            {**good, "maxCostFraction": 0.8},
        ):
            build_mission(
                mission_variant(schemaVersion="0.2.0", delegation={"grantCycle": grant_cycle}),
                created_at=CREATED_AT,
            )
        with self.assertRaises(ControlPlaneContractError):
            build_mission(
                mission_variant(schemaVersion="0.2.0", delegation={"grantCycle": good, "extra": 1}),
                created_at=CREATED_AT,
            )

    def test_answer_blockers_rejects_every_boundary_violation(self) -> None:
        # PIP-906: mirrors test_grant_cycle_rejects_every_boundary_violation
        # for the second delegation rule — if the schema-0.2.0-only check, the
        # exact-key-set check, or the maxTimes bounds check is loosened, this
        # is the test that notices.
        bad_answer_blockers = {
            "maxTimes 0": {"maxTimes": 0},
            "maxTimes 4": {"maxTimes": 4},
            "maxTimes bool": {"maxTimes": True},
            "maxTimes non-integer": {"maxTimes": 1.5},
            "empty": {},
            "extra key": {"maxTimes": 1, "extra": 1},
            "unknown key instead": {"limit": 1},
        }
        for label, rule in bad_answer_blockers.items():
            with self.subTest(label):
                with self.assertRaises(ControlPlaneContractError):
                    build_mission(
                        mission_variant(schemaVersion="0.2.0", delegation={"answerBlockers": rule}),
                        created_at=CREATED_AT,
                    )
        # The boundaries themselves (1 and 3) must be accepted.
        for max_times in (1, 3):
            build_mission(
                mission_variant(
                    schemaVersion="0.2.0", delegation={"answerBlockers": {"maxTimes": max_times}}
                ),
                created_at=CREATED_AT,
            )
        with self.assertRaisesRegex(ControlPlaneContractError, "requires schema 0.2.0"):
            build_mission(
                mission_variant(
                    schemaVersion="0.1.0", delegation={"answerBlockers": {"maxTimes": 1}}
                ),
                created_at=CREATED_AT,
            )

    def test_delegation_accepts_grant_cycle_and_answer_blockers_together_or_alone(self) -> None:
        grant_cycle = {"maxTimes": 1, "maxCostFraction": 0.5, "requireProgress": True}
        answer_blockers = {"maxTimes": 2}
        only_answer = build_mission(
            mission_variant(schemaVersion="0.2.0", delegation={"answerBlockers": answer_blockers}),
            created_at=CREATED_AT,
        )
        self.assertEqual(only_answer["delegation"], {"answerBlockers": answer_blockers})
        both = build_mission(
            mission_variant(
                schemaVersion="0.2.0",
                delegation={"grantCycle": grant_cycle, "answerBlockers": answer_blockers},
            ),
            created_at=CREATED_AT,
        )
        self.assertEqual(both["delegation"], {"grantCycle": grant_cycle, "answerBlockers": answer_blockers})
        with self.assertRaises(ControlPlaneContractError):
            build_mission(
                mission_variant(schemaVersion="0.2.0", delegation={}), created_at=CREATED_AT
            )
