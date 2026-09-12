"""Deterministic Program supervisor: the loop that turns a Program's stages
into missions, one wave at a time (PIP-910).

Reuses the mission supervisor wholesale: once a stage's mission is created
and activated, ``supervisor.supervise`` runs it exactly as it would run any
other mission — worker, verification, reviewer, delivery. Nothing here
duplicates that; this module only decides *which* mission to create next and
*where its base branch comes from* (branch chaining, never a merge), and
gates each wave the same way the mission supervisor gates a cycle: a
mechanical check outside the model (``startWhen``), a human approval
(``requiresFounder``), a budget ceiling, and — once every stage is done — the
program's own ``doneWhen``.

Every stop condition opens a decision on the *program* (``PRG-`` subject,
same ``decisions`` table a mission's decisions live in) before returning, so
``supervise_program`` never leaves the program ``active`` without either
having made progress or having something pending for the founder.
"""

from __future__ import annotations

import contextlib
import copy
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from pipe_venture_builder.control_plane.model import utc_now

from . import supervisor
from .contract import build_mission
from .delivery import branch_name, child_env, commit_if_needed, worktree_path
from .program import chain_from_stage_id
from .status import default_mission_home
from .store import MissionStore
from .verify import DEFAULT_CHECK_TIMEOUT_SECONDS, verify_criteria

GIT_TIMEOUT_SECONDS = 300.0


@dataclass(frozen=True)
class ProgramStep:
    """What one ``supervise_program`` call did: the program's status
    afterwards, why, and which stage (if any) that reason concerns."""

    status: str
    reason: str
    stage: str | None = None


def supervise_program(
    program_id: str,
    *,
    store: MissionStore,
    claude_bin: str,
    gh_bin: str,
    home: str | Path | None = None,
    now: Callable[[], str] = utc_now,
    check_timeout: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
    **mission_options: Any,
) -> ProgramStep:
    """Repeat "pick the next ready stage, run it to a mission's own terminal
    state" until the program is complete, or a wave gate stops it — the same
    style as ``supervisor.supervise`` repeating ``run_once`` for one mission.

    ``mission_options`` is forwarded to ``supervisor.supervise`` for each
    stage's mission (``poll_seconds``, ``worker_timeout``, ``worker_model``,
    ``checks_poll_seconds``, ...); a stage's own ``execution`` overrides
    ``worker_model``/``reviewer_model`` when it declares them.
    """

    root = _home(home)
    while True:
        program = store.get_program(program_id)
        if program["status"] != "active":
            return ProgramStep(program["status"], "not_active")

        if store.program_cost_usd(program_id) > program["constraints"]["maxBudgetUsd"]:
            return _budget_block(store, program, at=now())

        states = _stage_states(store, program)
        if all(state == "completed" for state in states.values()):
            return _finish_program(store, program, home=root, check_timeout=check_timeout, at=now())

        stage = _select_ready_stage(program, states)
        if stage is None:
            return ProgramStep("active", "waiting_on_dependencies")

        if not _stage_founder_gate_open(store, program, stage, at=now()):
            return ProgramStep(store.get_program(program_id)["status"], "requires_founder", stage=stage["id"])

        ready, blocked_step = _check_start_when(
            store, program, stage, home=root, check_timeout=check_timeout, at=now()
        )
        if not ready:
            return blocked_step

        mission_id = store.stage_mission(program_id, stage["id"])
        if mission_id is None:
            base_ref = _resolve_stage_base(store, program, stage)
            mission_document = _build_stage_mission(program, stage, base_ref)
            mission_id = store.create(mission_document, at=now())
            store.activate(mission_id, at=now())
            store.record_stage_mission(program_id, stage["id"], mission_id, at=now())

        mission_kwargs = dict(mission_options)
        execution = stage["execution"]
        if execution.get("workerModel"):
            mission_kwargs["worker_model"] = execution["workerModel"]
        if execution.get("reviewerModel"):
            mission_kwargs["reviewer_model"] = execution["reviewerModel"]
        supervisor.supervise(
            mission_id, store=store, claude_bin=claude_bin, gh_bin=gh_bin, home=root, **mission_kwargs
        )
        mission = store.get(mission_id)
        if mission["status"] != "completed":
            return _follow_mission(store, program, stage, mission, at=now())
        # The stage completed: persist whatever it left uncommitted onto its
        # own branch — never a merge, just this one mission's own history —
        # so the next wave's ``git worktree add`` (branch chaining) and the
        # ``startWhen``/``doneWhen`` checks below actually see it. A
        # ``pull_request`` delivery already committed everything, so this is
        # a no-op then; a ``none`` delivery (every stage in the PIP-910
        # contract's examples) never commits on its own.
        commit_if_needed(
            worktree_path(mission_id, root),
            f"{program_id}: onda {stage['id']} concluida (commit do supervisor de programa)",
        )
        # loop again and pick the next ready stage


# -- wave selection --------------------------------------------------------------


def _stage_states(store: MissionStore, program: Mapping[str, Any]) -> dict[str, str]:
    states: dict[str, str] = {}
    for stage in program["stages"]:
        mission_id = store.stage_mission(program["programId"], stage["id"])
        states[stage["id"]] = store.get(mission_id)["status"] if mission_id else "pending"
    return states


def _select_ready_stage(
    program: Mapping[str, Any], states: Mapping[str, str]
) -> dict[str, Any] | None:
    for stage in program["stages"]:
        state = states[stage["id"]]
        if state == "completed":
            continue
        if state != "pending":
            # A mission already exists for this stage but did not finish
            # ``completed`` last time (a rare "active" straggler — every
            # ending the mission supervisor reports as paused/blocked already
            # returns before the loop gets back here): resume the same one,
            # never a new mission for the same stage.
            return stage
        if all(states.get(dependency) == "completed" for dependency in stage["dependsOn"]):
            return stage
    return None


# -- gates -------------------------------------------------------------------


def _find_decision(store: MissionStore, subject_id: str, *, kind: str, context: Mapping[str, Any]) -> dict[str, Any] | None:
    """A decision already opened for *subject_id* with this exact kind and
    context, pending or resolved — so a gate is asked once, not on every
    call, and a resolved approval is honoured instead of re-opened."""

    for decision in store.list_decisions(subject_id):
        if decision["kind"] == kind and decision["context"] == dict(context):
            return decision
    return None


def _stage_founder_gate_open(
    store: MissionStore, program: Mapping[str, Any], stage: Mapping[str, Any], *, at: str
) -> bool:
    """True once the stage may proceed: it never required founder approval,
    or a founder already resolved the gate's decision with ``approve``."""

    if not stage["requiresFounder"]:
        return True
    program_id = program["programId"]
    context = {"reason": "requires_founder", "stage": stage["id"]}
    existing = _find_decision(store, program_id, kind="approval", context=context)
    if existing is None:
        store.open_decision(
            program_id, kind="approval", context=context, options=["approve", "stop"],
            safe_default="stop", blocked_scope="stage", deadline=None, at=at,
        )
        _pause_if_active(store, program_id, at=at)
        return False
    if existing["status"] == "pending":
        _pause_if_active(store, program_id, at=at)
        return False
    if existing["decidedOption"] != "approve":
        _pause_if_active(store, program_id, at=at)
        return False
    return True


def _check_start_when(
    store: MissionStore,
    program: Mapping[str, Any],
    stage: Mapping[str, Any],
    *,
    home: Path,
    check_timeout: float,
    at: str,
) -> tuple[bool, ProgramStep | None]:
    """``startWhen`` evaluated from outside, in a throwaway worktree per
    dependency branch — the same ``check``/``artifact`` primitives a
    mission's own verification uses (``verify.verify_criteria``), never the
    stage mission's own worktree: this is the independent confirmation that
    the wave(s) it depends on actually delivered, before anything is built on
    top of them. A criterion is satisfied if satisfied against *any* one
    dependency's branch (a stage with two dependencies checks each of its
    ``startWhen`` criteria against whichever of the two produced it)."""

    criteria = stage["startWhen"]
    if not criteria or _evaluate_criteria_across_refs(
        program["workspace"]["repo"],
        _stage_base_candidates(store, program, stage),
        criteria,
        check_timeout=check_timeout,
        home=home,
    ):
        return True, None
    program_id = program["programId"]
    context = {"reason": "start_when_unsatisfied", "stage": stage["id"]}
    if _find_decision(store, program_id, kind="escalation", context=context) is None:
        store.open_decision(
            program_id, kind="escalation", context=context, options=["stop", "revise_stage"],
            safe_default="stop", blocked_scope="stage", deadline=None, at=at,
        )
    if store.get_program(program_id)["status"] == "active":
        store.block_program(program_id, reason_code="start_when_unsatisfied", at=at)
    return False, ProgramStep("blocked", "start_when_unsatisfied", stage=stage["id"])


def _follow_mission(
    store: MissionStore,
    program: Mapping[str, Any],
    stage: Mapping[str, Any],
    mission: Mapping[str, Any],
    *,
    at: str,
) -> ProgramStep:
    """A stage's mission ended without completing: the program follows it
    into ``paused``/``blocked`` with its own decision (never starting another
    wave), instead of silently waiting."""

    program_id = program["programId"]
    status = mission["status"]
    context = {"reason": f"stage_mission_{status}", "stage": stage["id"], "missionId": mission["missionId"]}
    kind = "escalation"
    if _find_decision(store, program_id, kind=kind, context=context) is None:
        store.open_decision(
            program_id, kind=kind, context=context, options=["stop", "resume_stage"],
            safe_default="stop", blocked_scope="stage", deadline=None, at=at,
        )
    if status == "paused":
        _pause_if_active(store, program_id, at=at)
    elif store.get_program(program_id)["status"] == "active":
        store.block_program(program_id, reason_code="stage_mission_blocked", at=at)
    return ProgramStep(store.get_program(program_id)["status"], f"stage_mission_{status}", stage=stage["id"])


def _budget_block(store: MissionStore, program: Mapping[str, Any], *, at: str) -> ProgramStep:
    program_id = program["programId"]
    context = {"reason": "budget_reached"}
    if _find_decision(store, program_id, kind="budget", context=context) is None:
        store.open_decision(
            program_id, kind="budget", context=context, options=["stop", "revise_program"],
            safe_default="stop", blocked_scope="program", deadline=None, at=at,
        )
    if store.get_program(program_id)["status"] == "active":
        store.block_program(program_id, reason_code="budget_reached", at=at)
    return ProgramStep(store.get_program(program_id)["status"], "budget_reached")


def _finish_program(
    store: MissionStore, program: Mapping[str, Any], *, home: Path, check_timeout: float, at: str
) -> ProgramStep:
    """Every stage is ``completed``: check the program's own ``doneWhen`` —
    against the final stage's branch, which (branch chaining, no merge)
    already carries every prior stage's delivered content."""

    program_id = program["programId"]
    criteria = program["doneWhen"]
    satisfied = True
    if criteria:
        final_stage = program["stages"][-1]
        mission_id = store.stage_mission(program_id, final_stage["id"])
        ref = branch_name(store.get(mission_id))
        satisfied = _evaluate_criteria_across_refs(
            program["workspace"]["repo"], [ref], criteria, check_timeout=check_timeout, home=home
        )
    if satisfied:
        store.complete_program(program_id, at=at)
        return ProgramStep("completed", "done_when_satisfied")
    context = {"reason": "done_when_unsatisfied"}
    if _find_decision(store, program_id, kind="escalation", context=context) is None:
        store.open_decision(
            program_id, kind="escalation", context=context, options=["stop", "revise_program"],
            safe_default="stop", blocked_scope="program", deadline=None, at=at,
        )
    store.block_program(program_id, reason_code="done_when_unsatisfied", at=at)
    return ProgramStep("blocked", "done_when_unsatisfied")


def _pause_if_active(store: MissionStore, program_id: str, *, at: str) -> None:
    if store.get_program(program_id)["status"] == "active":
        store.pause_program(program_id, at=at)


# -- branch chaining -----------------------------------------------------------


def _resolve_stage_base(store: MissionStore, program: Mapping[str, Any], stage: Mapping[str, Any]) -> str:
    """Wave 1 branches from the program's own ``baseRef``; a dependent wave
    branches from the *branch* of its ``chainFrom`` dependency's mission — the
    program never merges, so this is how each wave sees the previous one's
    delivered content."""

    dependency = chain_from_stage_id(stage)
    if dependency is None:
        return program["workspace"]["baseRef"]
    dependency_mission_id = store.stage_mission(program["programId"], dependency)
    return branch_name(store.get(dependency_mission_id))


def _stage_base_candidates(
    store: MissionStore, program: Mapping[str, Any], stage: Mapping[str, Any]
) -> list[str]:
    """Every branch a stage's ``startWhen`` may confirm delivery against: one
    per dependency (each may have produced a different criterion), or the
    program's own base for a first-wave stage."""

    depends_on = stage["dependsOn"]
    if not depends_on:
        return [program["workspace"]["baseRef"]]
    refs = []
    for dependency in depends_on:
        dependency_mission_id = store.stage_mission(program["programId"], dependency)
        refs.append(branch_name(store.get(dependency_mission_id)))
    return refs


def _build_stage_mission(
    program: Mapping[str, Any], stage: Mapping[str, Any], base_ref: str
) -> dict[str, Any]:
    draft = copy.deepcopy(stage["missionDraft"])
    draft["workspace"] = {
        "repo": program["workspace"]["repo"],
        "baseRef": base_ref,
        "writeSet": draft["workspace"]["writeSet"],
    }
    draft["program"] = {"programId": program["programId"], "stage": stage["id"]}
    return build_mission(draft)


# -- startWhen/doneWhen: check/artifact against a throwaway worktree -----------


def _evaluate_criteria_across_refs(
    repo: str, refs: list[str], criteria: list[Mapping[str, Any]], *, check_timeout: float, home: Path
) -> bool:
    """Every criterion satisfied in *some* ref's throwaway worktree (a single
    ref for the common case — one dependency, or the final stage's
    ``doneWhen`` — degrades to a plain "all satisfied here")."""

    if not criteria:
        return True
    satisfied = [False] * len(criteria)
    fake_mission = {"successCriteria": criteria}
    for ref in refs:
        with _throwaway_worktree(repo, ref, home=home) as path:
            results = verify_criteria(fake_mission, path, check_timeout=check_timeout)
        for index, result in enumerate(results):
            satisfied[index] = satisfied[index] or result.satisfied
    return all(satisfied)


@contextlib.contextmanager
def _throwaway_worktree(repo: str, ref: str, *, home: Path) -> Iterator[Path]:
    """A detached, disposable ``git worktree`` at *ref* — never the branch a
    stage's own mission worktree has checked out, so this coexists with it —
    removed on the way out. Nothing here is written back to *repo*."""

    checks_root = home / "programs" / "checks"
    checks_root.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(dir=checks_root, prefix="startwhen-"))
    path.rmdir()  # ``git worktree add`` must create the directory itself
    try:
        _git(repo, "worktree", "add", "--detach", str(path), ref)
        yield path
    finally:
        _git(repo, "worktree", "remove", "--force", str(path), check=False)
        _git(repo, "worktree", "prune", check=False)
        shutil.rmtree(path, ignore_errors=True)


def _git(repo: str, *args: str, check: bool = True) -> None:
    subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, timeout=GIT_TIMEOUT_SECONDS, check=check, env=child_env(),
    )


def _home(home: str | Path | None) -> Path:
    return Path(home).expanduser() if home is not None else default_mission_home()
