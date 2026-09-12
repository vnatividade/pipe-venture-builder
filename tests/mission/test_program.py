"""PIP-910: Program contract and wave loop — a mission per test, not shared.

Each rule the founder's design doc (§2, §5) states for the Program loop gets
its own test here (never only the hidden acceptance suite): choosing the next
ready wave, branch chaining (never a merge), the external ``startWhen`` gate,
the human ``requiresFounder`` gate, a stage mission that stops on its own
decision, the program's budget ceiling, ``doneWhen`` evaluated only once every
wave is done, and idempotent stage-mission recording across a resumed loop.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipe_venture_builder.control_plane.model import ControlPlaneContractError, ControlPlaneStateError
from pipe_venture_builder.mission.program import PROGRAM_ID_PREFIX, build_program
from pipe_venture_builder.mission.program_supervisor import supervise_program
from pipe_venture_builder.mission.status import build_program_status
from pipe_venture_builder.mission.store import MissionStore

from tests.helpers import REPOSITORY_ROOT
from tests.mission.helpers import mission_input
from tests.mission.loop_helpers import FakeBinaries, git, make_repo
from tests.mission.test_supervisor import SupervisorTestCase


# -- fixtures shared by both the contract and the loop tests -------------------


def stage_draft(stage_id: str, **overrides: Any) -> dict[str, Any]:
    document = mission_input()
    document["title"] = f"Onda {stage_id}"
    document["successCriteria"] = [{
        "id": "C1", "text": f"docs/{stage_id}.md existe", "kind": "check",
        "command": f"test -f docs/{stage_id}.md", "cwd": ".",
    }]
    document["delivery"] = {"kind": "none", "requireChecks": False}
    document["workspace"] = {"writeSet": [f"docs/{stage_id}.md"]}
    document["linearTicketIds"] = ["PIP-910"]
    document.pop("missionId", None)
    document.pop("status", None)
    document.update(overrides)
    return document


def stage(stage_id: str, *, depends: list[str] | None = None, founder: bool = False,
          start_when: list[dict[str, Any]] | None = None, **extra: Any) -> dict[str, Any]:
    body = {
        "id": stage_id,
        "missionDraft": stage_draft(stage_id),
        "dependsOn": depends or [],
        "startWhen": start_when if start_when is not None else [],
        "requiresFounder": founder,
        "execution": {},
    }
    body.update(extra)
    return body


def delivered(stage_id: str) -> list[dict[str, Any]]:
    return [{"id": "G1", "text": f"docs/{stage_id}.md entregue", "kind": "check",
             "command": f"test -f docs/{stage_id}.md", "cwd": "."}]


def program_document(repo: Path, stages: list[dict[str, Any]], **overrides: Any) -> dict[str, Any]:
    document = {
        "schemaVersion": "0.1.0", "version": 1, "supersedes": None,
        "objective": "a planilha vira um sistema web",
        "doneWhen": [],
        "workspace": {"repo": str(repo), "baseRef": "main"},
        "constraints": {"maxBudgetUsd": 20},
        "stages": stages,
    }
    document.update(overrides)
    return document


def writes(stage_id: str) -> dict[str, Any]:
    return {"write_files": {f"docs/{stage_id}.md": f"# onda {stage_id}\n"},
            "worker_output": {"done": True, "summary": f"onda {stage_id}", "filesChanged": [f"docs/{stage_id}.md"],
                               "criteriaSelfAssessment": [{"id": "C1", "met": True, "note": "escrito"}],
                               "blockers": []}}


def satisfied() -> dict[str, Any]:
    return {"structured_output": {"verdict": "satisfied",
                                  "criteria": [{"id": "C1", "met": True, "evidence": "arquivo presente"}],
                                  "reasons": ["entrega dentro do write set"]}}


class ProgramHarness:
    """A validated, created and activated Program over a temporary repo, with fakes."""

    def __init__(self, root: Path, stages: list[dict[str, Any]], **overrides: Any) -> None:
        self.root = root
        self.repo = make_repo(root)
        (self.repo / "docs").mkdir(exist_ok=True)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "docs dir", "--allow-empty")
        self.home = root / "home"
        self.store = MissionStore(root / "mission.sqlite3")
        self.document = build_program(program_document(self.repo, stages, **overrides))
        self.program_id = self.store.create_program(self.document)
        self.store.activate_program(self.program_id)
        self.fakes = FakeBinaries(root)

    def run(self, **extra: Any) -> Any:
        options = dict(store=self.store, claude_bin=self.fakes.claude_bin, gh_bin=self.fakes.gh_bin,
                       home=self.home, poll_seconds=0.05, checks_poll_seconds=0.01, checks_max_polls=20)
        options.update(extra)
        return supervise_program(self.program_id, **options)

    def status(self) -> dict[str, Any]:
        return build_program_status(self.store, self.program_id, home=self.home)

    def stage_status(self) -> dict[str, str]:
        return {item["id"]: item["status"] for item in self.status()["stages"]}

    def missions(self) -> dict[str, str | None]:
        return {item["id"]: item.get("missionId") for item in self.status()["stages"]}

    def worker_calls(self) -> int:
        return len([call for call in self.fakes.claude_calls() if call["role"] == "worker"])

    def close(self) -> None:
        self.store.close()


class ProgramTestCase(SupervisorTestCase):
    def program_harness(self, stages: list[dict[str, Any]], **overrides: Any) -> ProgramHarness:
        harness = ProgramHarness(self.root, stages, **overrides)
        self.addCleanup(harness.close)
        harness.fakes.__enter__()
        self.addCleanup(lambda: harness.fakes.__exit__(None, None, None))
        return harness


# -- contract -------------------------------------------------------------------


class ProgramContractTests(ProgramTestCase):
    def test_program_id_is_stable_and_prefixed(self) -> None:
        repo = make_repo(self.root)
        document = program_document(repo, [stage("a")])
        first = build_program(json.loads(json.dumps(document)))
        second = build_program(json.loads(json.dumps(document)))
        self.assertTrue(first["programId"].startswith(PROGRAM_ID_PREFIX))
        self.assertEqual(first["programId"], second["programId"])
        self.assertEqual(first["fingerprint"], second["fingerprint"])

    def test_no_stages_is_refused(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, []))

    def test_a_stage_depending_on_an_undeclared_id_is_refused(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, [stage("a", depends=["zzz"])]))

    def test_a_dependency_cycle_is_refused(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, [stage("a", depends=["b"]), stage("b", depends=["a"])]))

    def test_two_dependencies_without_chain_from_is_refused(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(
                repo, [stage("a"), stage("b"), stage("c", depends=["a", "b"])]
            ))

    def test_a_mission_draft_with_a_base_ref_is_refused(self) -> None:
        repo = make_repo(self.root)
        draft = stage_draft("a", workspace={"writeSet": ["docs/a.md"], "baseRef": "main"})
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, [stage("a", missionDraft=draft)]))

    def test_an_unknown_top_level_field_is_refused(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, [stage("a")], surprise="nope"))

    def test_a_valid_two_stage_program_builds(self) -> None:
        repo = make_repo(self.root)
        build_program(program_document(repo, [
            stage("a"), stage("b", depends=["a"], start_when=delivered("a")),
        ]))


def rubric_stage(stage_id: str, *, executor: str | None = None) -> dict[str, Any]:
    """A wave whose own success criterion is a ``rubric`` — the shape PIP-911
    ties to the executor policy below."""

    draft = stage_draft(stage_id, successCriteria=[{
        "id": "C1", "text": "a onda cumpriu a intencao", "kind": "rubric",
        "question": "A onda cumpriu a intencao declarada?",
    }])
    execution: dict[str, Any] = {} if executor is None else {"executor": executor}
    return stage(stage_id, missionDraft=draft, execution=execution)


class ExecutorPolicyTests(ProgramTestCase):
    """PIP-911: ``execution.executor`` (claude/local) is a schema-level
    enum (see ``schemas/Program.schema.json`` and the wave-2 gate script),
    and the deterministic policy lives in ``program._validate_execution`` —
    never a prompt: a wave with a ``rubric`` success criterion can never
    declare a local executor, because a rubric is judged by the reviewer,
    and the reviewer is never local either (it has no executor field of its
    own at all — see ``supervisor._review``/``_answer_blockers``)."""

    def test_a_rubric_wave_refuses_a_local_executor(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, [rubric_stage("a", executor="local")]))

    def test_a_rubric_wave_allows_the_claude_executor(self) -> None:
        repo = make_repo(self.root)
        build_program(program_document(repo, [rubric_stage("a", executor="claude")]))

    def test_a_rubric_wave_with_no_declared_executor_is_allowed(self) -> None:
        repo = make_repo(self.root)
        build_program(program_document(repo, [rubric_stage("a")]))

    def test_a_non_rubric_wave_allows_a_local_executor(self) -> None:
        repo = make_repo(self.root)
        build_program(program_document(repo, [stage("a", execution={"executor": "local"})]))

    def test_an_unknown_executor_value_is_refused(self) -> None:
        repo = make_repo(self.root)
        with self.assertRaises(ControlPlaneContractError):
            build_program(program_document(repo, [stage("a", execution={"executor": "gpt5"})]))

    def test_schema_declares_the_same_executor_enum_the_code_enforces(self) -> None:
        schema = json.loads((REPOSITORY_ROOT / "schemas/Program.schema.json").read_text())
        executor = schema["$defs"]["execution"]["properties"]["executor"]
        self.assertEqual(set(executor["enum"]), {"claude", "local"})


# -- the loop --------------------------------------------------------------------


class NextReadyWaveTests(ProgramTestCase):
    """Rule: the next wave picked is the first whose dependencies are all
    ``completed`` — never one still waiting on a sibling. A direct unit test
    of ``_select_ready_stage`` (no git, no fakes): removing the dependency
    check from it would make this fail immediately."""

    def test_a_stage_with_an_unfinished_dependency_is_not_picked(self) -> None:
        from pipe_venture_builder.mission.program_supervisor import _select_ready_stage

        program = {"stages": [stage("a"), stage("b", depends=["a"])]}
        states = {"a": "active", "b": "pending"}
        selected = _select_ready_stage(program, states)
        self.assertEqual(selected["id"], "a", "a onda com dependência pendente nunca é escolhida")

    def test_a_completed_stage_is_skipped_in_favour_of_the_next_ready_one(self) -> None:
        from pipe_venture_builder.mission.program_supervisor import _select_ready_stage

        program = {"stages": [stage("a"), stage("b", depends=["a"]), stage("c", depends=["a"])]}
        states = {"a": "completed", "b": "pending", "c": "pending"}
        selected = _select_ready_stage(program, states)
        self.assertEqual(selected["id"], "b")

    def test_nothing_ready_returns_none(self) -> None:
        from pipe_venture_builder.mission.program_supervisor import _select_ready_stage

        program = {"stages": [stage("b", depends=["a"])]}
        states = {"b": "pending"}  # "a" has no recorded mission at all yet
        self.assertIsNone(_select_ready_stage(program, states))


class BranchChainingTests(ProgramTestCase):
    """Rule: wave 1 branches from the program's own ``baseRef``; a dependent
    wave branches from its dependency's mission branch — never a merge."""

    def test_wave_one_branches_from_the_program_base_and_wave_two_from_wave_ones_branch(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a")),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        step = h.run()
        self.assertEqual(step.status, "completed", step)
        first, second = h.missions()["a"], h.missions()["b"]
        self.assertEqual(h.store.get(first)["workspace"]["baseRef"], "main")
        self.assertIn(first, h.store.get(second)["workspace"]["baseRef"])
        self.assertEqual(h.store.get(second)["program"], {"programId": h.program_id, "stage": "b"})


class StartWhenGateTests(ProgramTestCase):
    """Rule: an unsatisfied ``startWhen`` blocks the program and creates no
    mission for the gated wave — the mechanical control the founder's design
    calls out as answering the "did the previous wave really deliver" doubt."""

    def test_unsatisfied_start_when_blocks_without_creating_a_mission(self) -> None:
        h = self.program_harness([
            stage("a"),
            stage("b", depends=["a"], start_when=[{
                "id": "G1", "text": "nunca existe", "kind": "check",
                "command": "test -f docs/nunca-existe.md", "cwd": "."}]),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        step = h.run()
        self.assertEqual(step.status, "blocked", step)
        self.assertEqual(h.stage_status()["b"], "pending")
        self.assertIsNone(h.missions()["b"])
        self.assertEqual(len(h.status()["pendingDecisions"]), 1)

    def test_satisfied_start_when_lets_the_next_wave_start(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a")),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        step = h.run()
        self.assertEqual(step.status, "completed", step)


class FounderGateTests(ProgramTestCase):
    """Rule: ``requiresFounder`` opens an ``approval`` decision (options
    ``approve``/``stop``, safe default ``stop``) and pauses the program before
    any mission for that wave exists; approving and resuming lets it proceed."""

    def test_requires_founder_pauses_and_creates_no_mission(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a"), founder=True),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        step = h.run()
        self.assertEqual(step.status, "paused", step)
        self.assertIsNone(h.missions()["b"])
        [decision] = h.store.pending_decisions(h.program_id)
        self.assertEqual(decision["kind"], "approval")
        self.assertEqual(set(decision["options"]), {"approve", "stop"})
        self.assertEqual(decision["safeDefault"], "stop")

    def test_approving_and_resuming_creates_the_mission(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a"), founder=True),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        h.run()
        [decision] = h.store.pending_decisions(h.program_id)
        h.store.resolve_decision(decision["decisionId"], option="approve", decided_by="human:cli:vitor")
        h.store.resume_program(h.program_id)
        step = h.run()
        self.assertEqual(step.status, "completed", step)
        self.assertIsNotNone(h.missions()["b"])


class StageMissionStopsTests(ProgramTestCase):
    """Rule: a stage mission that ends ``paused``/``blocked`` with its own
    pending decision follows the program into ``paused``/``blocked`` too —
    the next wave never starts underneath it."""

    def test_a_blocked_worker_pauses_the_program_without_starting_the_next_wave(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a")),
        ])
        blocked_worker = {"write_files": {}, "worker_output": {
            "done": False, "summary": "preciso de ajuda", "filesChanged": [],
            "criteriaSelfAssessment": [{"id": "C1", "met": False, "note": "parado"}],
            "blockers": ["Qual arquivo recebe o conteudo?"]}}
        h.fakes.scenario(worker=[blocked_worker], reviewer=[satisfied()])
        step = h.run()
        self.assertEqual(step.status, "paused")
        self.assertEqual(step.reason, "stage_mission_paused")
        self.assertIsNone(h.missions()["b"])
        self.assertGreaterEqual(len(h.status()["pendingDecisions"]), 1)


class BudgetCapTests(ProgramTestCase):
    """Rule: cost above ``constraints.maxBudgetUsd`` BLOCKS the program with a
    decision, without starting the next wave.

    Blocked, not paused, and the test pins that: ``resume_program`` refuses a
    blocked program until its decisions are resolved, so the founder cannot
    resume straight back into the same overspend. Accepting either status left
    the rule undecided — the looser assertion was the defect.
    """

    def test_cost_above_the_cap_blocks_before_the_next_wave(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a")),
        ], constraints={"maxBudgetUsd": 0.5})
        expensive = dict(writes("a"))
        expensive["result"] = {"total_cost_usd": 0.9}
        h.fakes.scenario(worker=[expensive, writes("b")], reviewer=[satisfied(), satisfied()])
        step = h.run()
        self.assertEqual(step.status, "blocked")
        self.assertEqual(step.reason, "budget_reached")
        self.assertIsNone(h.missions()["b"])
        self.assertGreater(h.store.program_cost_usd(h.program_id), 0.5)
        self.assertGreaterEqual(len(h.status()["pendingDecisions"]), 1)
        with self.assertRaises(ControlPlaneStateError):
            h.store.resume_program(h.program_id)


class DoneWhenTests(ProgramTestCase):
    """Rule: ``doneWhen`` is only evaluated once every wave is ``completed`` —
    satisfied completes the program, unsatisfied blocks it instead."""

    def test_done_when_satisfied_completes_the_program(self) -> None:
        h = self.program_harness([stage("a")], doneWhen=delivered("a"))
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        self.assertEqual(h.run().status, "completed")

    def test_done_when_unsatisfied_blocks_instead_of_completing(self) -> None:
        h = self.program_harness([stage("a")], doneWhen=[{
            "id": "D1", "text": "objetivo nunca cumprido", "kind": "check",
            "command": "test -f docs/objetivo-final.md", "cwd": "."}])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        step = h.run()
        self.assertEqual(step.status, "blocked", step)
        self.assertEqual(h.stage_status()["a"], "completed")
        self.assertGreaterEqual(len(h.status()["pendingDecisions"]), 1)


class IdempotencyTests(ProgramTestCase):
    """Rule: resuming the loop never recreates a mission for a stage that
    already has one, whether it finished or is still in flight; recording the
    same stage/mission pair twice is a no-op, a different one is refused."""

    def test_resuming_the_loop_does_not_duplicate_a_finished_stage(self) -> None:
        h = self.program_harness([
            stage("a"), stage("b", depends=["a"], start_when=delivered("a")),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        h.run()
        before = h.missions()
        calls_before = h.worker_calls()
        h.run()
        self.assertEqual(h.missions(), before)
        self.assertEqual(h.worker_calls(), calls_before)

    def test_record_stage_mission_is_idempotent_and_refuses_a_different_mission(self) -> None:
        h = self.program_harness([stage("a")])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run()
        mission_id = h.missions()["a"]
        # Recording the same pair again is a no-op (no error, no new event).
        events_before = len(h.store.list_program_events(h.program_id))
        h.store.record_stage_mission(h.program_id, "a", mission_id)
        self.assertEqual(len(h.store.list_program_events(h.program_id)), events_before)
        with self.assertRaises(ControlPlaneStateError):
            h.store.record_stage_mission(h.program_id, "a", "MSN-000000000000")


class AuditChainTests(ProgramTestCase):
    def test_the_program_event_chain_verifies_and_never_carries_the_objective_text(self) -> None:
        h = self.program_harness([stage("a")])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run()
        self.assertTrue(h.store.verify_program_chain(h.program_id))
        for event in h.store.list_program_events(h.program_id):
            self.assertNotIn("planilha", json.dumps(event.get("payload", {}), ensure_ascii=False))
