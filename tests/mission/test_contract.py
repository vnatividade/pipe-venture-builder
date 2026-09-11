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

    def test_delegation_defaults_to_none_and_requires_schema_0_2_0(self) -> None:
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        self.assertIsNone(mission["delegation"])

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
