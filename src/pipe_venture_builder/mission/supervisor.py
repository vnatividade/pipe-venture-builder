"""Deterministic Mission supervisor: one cycle per ``run_once``; no LLM here.

Order of a cycle (desenho D4/D6/D7/D10/D11 and the anti-loop guards):

1. the audit chain must verify, and no other live supervisor may own the
   mission (single writer); otherwise refuse;
2. reconcile: a worker left alive by a dead supervisor is killed (only if its
   pid still runs ``claude -p`` as a session leader); a ``running`` run
   becomes ``unknown`` with an ``escalation`` decision, and the mission
   becomes ``unknown`` — nothing is re-executed;
3. the mission must be ``active`` with no pending decision;
4. budget: worker budget = ``maxBudgetUsd`` − cost so far − reviewer reserve,
   never below ``MIN_RUN_BUDGET_USD``; otherwise ``budget.reached``;
5. worktree → worker (``claude -p``, isolated from the user's settings)
   while the store is polled every ``poll_seconds``: ``paused``/``cancelled``
   → SIGTERM to the group → ``run.interrupted``; the repository git config is
   compared before/after the run (changed → ``blocked``
   ``git_config_tampered``); permission denials are not a verdict;
6. verify: HEAD on the mission branch, circuit breaker (same diff fingerprint
   as the previous cycle → ``blocked``), write set without rename detection
   (outside → ``needs_revision`` without the reviewer), ``check``/``artifact``
   evidence (failing → ``needs_revision`` without the reviewer);
7. clean-context reviewer; route ``satisfied`` → delivery (branch and write
   set re-checked before the commit and before the push of ``HEAD``) →
   ``complete``; ``needs_revision`` → next cycle (limit → ``blocked`` +
   decision); ``out_of_mission`` → ``paused`` + decision (safe default
   ``pause``); ``blocked`` → ``blocked`` + decision.

Only ids, hashes, counts and reason codes reach SQLite and the log. The next
cycle's revision instructions (reviewer text, file names, tool names) live in
``<home>/<missionId>/revisions/cycle-<n>.md`` (0600), never in the store.
"""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    safe_identifier,
    utc_now,
)

from .delivery import (
    base_branch,
    branch_name,
    checks_status,
    commit_if_needed,
    current_branch,
    ensure_worktree,
    git_config_snapshot,
    mission_home,
    open_pr,
    pr_body,
    pr_title,
    push_branch,
)
from .reviewer import (
    DEFAULT_REVIEW_TIMEOUT_SECONDS,
    REVIEWER_OUTPUT_INVALID,
    REVIEWER_RUN_FAILED,
    run_review,
)
from .status import SUPERVISOR_PID_FILE, default_mission_home, pid_is_alive
from .store import DELEGATED_ORCHESTRATOR_SOURCE, UNKNOWN_SOURCES, MissionStore
from .verify import (
    DEFAULT_CHECK_TIMEOUT_SECONDS,
    changed_files,
    diff_fingerprint,
    diff_text,
    outside_write_set,
    verify_criteria,
)
from .worker import (
    DEFAULT_MODEL,
    DEFAULT_POLL_SECONDS,
    DEFAULT_WORKER_TIMEOUT_SECONDS,
    MIN_RUN_BUDGET_USD,
    ClaudeProcess,
    allowed_tools,
    run_worker,
)


SUPERVISOR_LOG_FILE = "supervisor.log"
WORKER_PID_FILE = "worker.pid"
REVISIONS_DIR = "revisions"
WORKER_EXECUTOR = "worker"
REVIEWER_EXECUTOR = "reviewer"
REVIEWER_ROLE = "reviewer"
REVIEW_RESERVE_USD = MIN_RUN_BUDGET_USD
DEFAULT_CHECKS_POLL_SECONDS = 30.0
DEFAULT_CHECKS_MAX_POLLS = 60
GRANT_CYCLE_OPTION = "grant_cycle"
# The only reason codes a mission's own ``delegation.grantCycle`` rule may
# cover: hitting the cycle limit. Every other ``_block`` reason (a legitimate
# reviewer verdict, the circuit breaker, an infrastructure failure escalating,
# a failed delivery check…) always waits on the founder, whatever the rule says.
DELEGABLE_REASONS = frozenset({"max_cycles", "needs_revision_limit"})
# A reviewer infrastructure failure (the CLI crashed, or its output was not a
# valid verdict) is not a judgement: it earns one automatic retry, with no new
# worker. A verdict the model itself returned as ``blocked`` is never retried.
REVIEWER_INFRA_FAILURES = frozenset({REVIEWER_RUN_FAILED, REVIEWER_OUTPUT_INVALID})
MAX_REVIEWER_ATTEMPTS = 2
# The worktree is not what was verified: a human inspects it, then resumes.
WORKSPACE_OPTIONS = ["stop", "fix_and_resume"]
# ``active`` results that end ``supervise`` instead of starting another cycle.
STOPPING_REASONS = frozenset({"pending_decisions", "interrupted"})
# Signals that request a stop: SIGHUP too, since a foreground ``supervise``
# receives it when its terminal closes (the worker lives in its own session).
STOP_SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
RECONCILE_KILL_GRACE_SECONDS = 5.0

REVISION_NO_JSON = (
    "O ciclo anterior terminou sem o JSON final pedido no brief (ou com JSON inválido). "
    "Termine SEMPRE respondendo somente com o JSON {\"done\": ..., \"summary\": ..., "
    "\"filesChanged\": [...], \"criteriaSelfAssessment\": [...], \"blockers\": [...]}."
)
REVISION_BLOCKERS = (
    "No ciclo anterior você reportou bloqueios e o fundador foi consultado. Retome a missão; "
    "se o bloqueio persistir, responda done=false com blockers objetivos."
)
REVISION_OUT_OF_MISSION = (
    "O revisor julgou que o diff anterior saiu da intenção da missão. Desfaça o que não "
    "serve à intenção e aos critérios e restrinja-se a eles."
)
REVISION_REVIEW_DEFAULT = (
    "O revisor pediu revisão sem instruções detalhadas. Reveja cada critério contra o diff "
    "e corrija o que não estiver sustentado."
)
REVISION_CHECKS_FAILED = (
    "Os checks do CI falharam no PR aberto pelo supervisor. Rode localmente os comandos de "
    "verificação dos critérios e a suíte do repositório e corrija a causa, dentro do write set."
)


class SupervisorRefusal(ControlPlaneStateError):
    """The supervisor refuses to act (invalid chain, another live supervisor)."""


@dataclass(frozen=True)
class Step:
    """What one ``run_once`` did: the mission status afterwards and why."""

    status: str
    reason: str
    cycle: int = 0


# -- public API ----------------------------------------------------------------


def reconcile(
    mission_id: str,
    *,
    store: MissionStore,
    now: Callable[[], str] = utc_now,
    home: str | Path | None = None,
    claude_bin: str | None = None,
    kill_grace_seconds: float = RECONCILE_KILL_GRACE_SECONDS,
) -> list[str]:
    """Runs left ``running`` without a live supervisor become ``unknown``.

    A worker the dead supervisor left running (its own session, so it
    survives the supervisor) is killed first — but only when ``worker.pid``
    still names a session leader running ``claude_bin -p``: a reused pid is
    left alone. Then one ``escalation`` decision is opened and the mission is
    marked ``unknown`` (terminal): a run whose outcome is unknown is never
    re-executed. Returns the reconciled run ids.
    """

    root = _home(home)
    orphans = [run for run in store.list_runs(mission_id) if run["status"] == "running"]
    if not orphans:
        return []
    _require_single_writer(root, mission_id)
    worker_pid = _worker_pid(root, mission_id)
    worker_alive = worker_pid is not None and pid_is_alive(worker_pid)
    worker_killed = False
    if worker_alive and claude_bin and _is_orphan_worker(worker_pid, claude_bin):
        worker_killed = _kill_session(worker_pid, grace_seconds=kill_grace_seconds)
    for run in orphans:
        store.collect_run(
            run["run_id"],
            session_id=None,
            cost_usd=0,
            num_turns=0,
            result_ref=None,
            result_fingerprint=None,
            status="unknown",
            at=now(),
            extra={"reason": "orphaned", "workerAlive": worker_alive, "workerKilled": worker_killed},
        )
    if store.get(mission_id)["status"] in UNKNOWN_SOURCES:
        store.open_decision(
            mission_id,
            kind="escalation",
            context={"reason": "run_unknown", "runs": len(orphans), "workerAlive": worker_alive},
            options=["stop", "revise_mission"],
            safe_default="stop",
            blocked_scope="mission",
            deadline=None,
            at=now(),
        )
        store.mark_unknown(mission_id, at=now())
    ids = [run["run_id"] for run in orphans]
    _log(root, mission_id, "reconcile", runs=len(ids), workerAlive=worker_alive, workerKilled=worker_killed)
    return ids


def run_once(
    mission_id: str,
    *,
    store: MissionStore,
    claude_bin: str,
    gh_bin: str,
    home: str | Path | None = None,
    worker_model: str = DEFAULT_MODEL,
    reviewer_model: str = DEFAULT_MODEL,
    now: Callable[[], str] = utc_now,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    worker_timeout: float = DEFAULT_WORKER_TIMEOUT_SECONDS,
    review_timeout: float = DEFAULT_REVIEW_TIMEOUT_SECONDS,
    check_timeout: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
    checks_poll_seconds: float = DEFAULT_CHECKS_POLL_SECONDS,
    checks_max_polls: int = DEFAULT_CHECKS_MAX_POLLS,
    sleep: Callable[[float], None] = time.sleep,
    stop_event: threading.Event | None = None,
) -> Step:
    """Execute one full cycle (or resume the open one) and return the next state."""

    cycle = _Cycle(
        mission_id,
        store=store,
        claude_bin=claude_bin,
        gh_bin=gh_bin,
        home=_home(home),
        worker_model=worker_model,
        reviewer_model=reviewer_model,
        now=now,
        poll_seconds=poll_seconds,
        worker_timeout=worker_timeout,
        review_timeout=review_timeout,
        check_timeout=check_timeout,
        checks_poll_seconds=checks_poll_seconds,
        checks_max_polls=checks_max_polls,
        sleep=sleep,
        stop_event=stop_event or threading.Event(),
    )
    step = cycle.run()
    _log(cycle.home, mission_id, "step", status=step.status, reason=step.reason, cycle=step.cycle)
    return step


def supervise(
    mission_id: str,
    *,
    store: MissionStore,
    claude_bin: str,
    gh_bin: str,
    home: str | Path | None = None,
    stop_event: threading.Event | None = None,
    **options: Any,
) -> Step:
    """Repeat ``run_once`` until the mission is terminal, paused, blocked or
    cancelled, or a cycle ends waiting on a decision or a stop request.

    Writes ``<home>/<missionId>/supervisor.pid`` (kept after exit, so
    ``status`` reports ``alive: false``). SIGTERM/SIGINT/SIGHUP request a
    stop: the running worker is terminated and its run recorded as
    ``interrupted``.
    """

    root = _home(home)
    _require_chain(store, mission_id)
    claim_supervisor(root, mission_id)
    _log(root, mission_id, "supervise.start", pid=os.getpid())
    step = Step(store.get(mission_id)["status"], "not_started")
    try:
        with stop_on_signals(stop_event) as stop:
            while True:
                step = run_once(
                    mission_id,
                    store=store,
                    claude_bin=claude_bin,
                    gh_bin=gh_bin,
                    home=root,
                    stop_event=stop,
                    **options,
                )
                if step.status != "active" or step.reason in STOPPING_REASONS or stop.is_set():
                    return step
    except BaseException as exc:
        _log(root, mission_id, "supervise.error", error=type(exc).__name__)
        raise
    finally:
        _log(root, mission_id, "supervise.end", status=step.status, reason=step.reason)


@contextmanager
def stop_on_signals(stop_event: threading.Event | None = None) -> Iterator[threading.Event]:
    """An event set by SIGTERM/SIGINT/SIGHUP while the block runs (main
    thread only); the previous handlers are restored afterwards."""

    stop = stop_event or threading.Event()
    previous = _install_stop_handlers(stop)
    try:
        yield stop
    finally:
        _restore_stop_handlers(previous)


def claim_supervisor(home: str | Path | None, mission_id: str) -> Path:
    """Refuse when another live process owns the mission; record our pid."""

    root = _home(home)
    _require_single_writer(root, mission_id)
    directory = _mission_dir(root, mission_id)
    pid_file = directory / SUPERVISOR_PID_FILE
    _write_private(pid_file, f"{os.getpid()}\n")
    return pid_file


def supervisor_log_path(home: str | Path | None, mission_id: str) -> Path:
    return mission_home(mission_id, _home(home)) / SUPERVISOR_LOG_FILE


def supervisor_pid_path(home: str | Path | None, mission_id: str) -> Path:
    return mission_home(mission_id, _home(home)) / SUPERVISOR_PID_FILE


def live_supervisor_pid(home: str | Path | None, mission_id: str) -> int | None:
    """The pid in the pid file when that process is alive, else ``None``."""

    try:
        pid = int(supervisor_pid_path(home, mission_id).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    return pid if pid_is_alive(pid) else None


# -- the cycle -----------------------------------------------------------------


class _Cycle:
    def __init__(self, mission_id: str, **options: Any) -> None:
        self.mission_id = mission_id
        self.store: MissionStore = options["store"]
        self.claude_bin: str = options["claude_bin"]
        self.gh_bin: str = options["gh_bin"]
        self.home: Path = options["home"]
        self.worker_model: str = options["worker_model"]
        self.reviewer_model: str = options["reviewer_model"]
        self.now: Callable[[], str] = options["now"]
        self.poll_seconds: float = options["poll_seconds"]
        self.worker_timeout: float = options["worker_timeout"]
        self.review_timeout: float = options["review_timeout"]
        self.check_timeout: float = options["check_timeout"]
        self.checks_poll_seconds: float = options["checks_poll_seconds"]
        self.checks_max_polls: int = options["checks_max_polls"]
        self.sleep: Callable[[float], None] = options["sleep"]
        self.stop: threading.Event = options["stop_event"]
        self.mission: dict[str, Any] = {}
        self._process: ClaudeProcess | None = None
        # Denied worker calls of this cycle (in memory only; see ``_revise``).
        self._denials: str | None = None

    # -- entry --------------------------------------------------------------

    def run(self) -> Step:
        _require_chain(self.store, self.mission_id)
        _require_single_writer(self.home, self.mission_id)
        if reconcile(
            self.mission_id, store=self.store, now=self.now, home=self.home, claude_bin=self.claude_bin
        ):
            return Step(self._status(), "run_unknown")
        self.mission = self.store.get(self.mission_id)
        if self.mission["status"] != "active":
            return Step(self.mission["status"], "not_active")
        if self.store.pending_decisions(self.mission_id):
            return Step("active", "pending_decisions")
        stage, cycle, attempt, worker_run = self._plan()
        if stage == "dispatch":
            return self._dispatch(cycle, attempt)
        worktree = ensure_worktree(self.mission, home=self.home)
        if stage == "review":
            return self._verify_and_review(cycle, worker_run, worktree)
        return self._deliver(cycle, worker_run, worktree)

    def _plan(self) -> tuple[str, int, int, str | None]:
        """Where the durable state says the mission is: dispatch, review or deliver."""

        workers = [
            run for run in self.store.list_runs(self.mission_id)
            if run["executor"].split(":", 1)[0] == WORKER_EXECUTOR
        ]
        if not workers:
            return "dispatch", 1, 1, None
        last = workers[-1]
        if last["status"] == "interrupted":
            return "dispatch", last["cycle"], last["attempt"] + 1, None
        if last["status"] != "collected":
            return "dispatch", last["cycle"] + 1, 1, None
        verdict = self._cycle_verdict(last["cycle"])
        if verdict is None:
            return "review", last["cycle"], last["attempt"], last["run_id"]
        if verdict == "satisfied":
            return "deliver", last["cycle"], last["attempt"], last["run_id"]
        return "dispatch", last["cycle"] + 1, 1, None

    # -- worker -------------------------------------------------------------

    def _dispatch(self, cycle: int, attempt: int) -> Step:
        if cycle > self._max_cycles():
            return self._block("max_cycles", cycle, None)
        worker_budget = self._budget_left() - REVIEW_RESERVE_USD
        if worker_budget < MIN_RUN_BUDGET_USD:
            return self._budget_reached(cycle)
        worktree = ensure_worktree(self.mission, home=self.home)
        revision = _load_revision(self.home, self.mission_id, cycle - 1)
        repo = self.mission["workspace"]["repo"]
        config_before = git_config_snapshot(repo, worktree)
        run_id = self.store.open_run(
            self.mission_id,
            cycle=cycle,
            attempt=attempt,
            executor=f"{WORKER_EXECUTOR}:{self.worker_model}",
            at=self.now(),
        )
        _log(self.home, self.mission_id, "worker.dispatched", run=run_id, cycle=cycle, attempt=attempt)
        try:
            result = run_worker(
                self.mission,
                run_id,
                worktree,
                self.claude_bin,
                worker_budget,
                cycle=cycle,
                revision_instructions=revision,
                model=self.worker_model,
                timeout=self.worker_timeout,
                poll_seconds=self.poll_seconds,
                should_stop=self._should_stop,
                on_start=self._worker_started,
            )
        except BaseException:
            self._terminate_worker()
            self._close_run_on_error(run_id)
            raise
        finally:
            self._process = None
            _remove(self.home / self.mission_id / WORKER_PID_FILE)

        status, reason = result.status, result.reason
        if status == "collected" and result.output is None:
            status, reason = "failed", "worker_output_invalid"
        self.store.collect_run(
            run_id,
            session_id=result.session_id,
            cost_usd=result.cost_usd,
            num_turns=result.num_turns,
            result_ref=None,
            result_fingerprint=result.result_fingerprint,
            status=status,
            at=self.now(),
            extra={
                "reason": _code(reason),
                "subtype": _code(result.subtype),
                "model": _code(self.worker_model),
                "permissionDenials": result.permission_denials,
            },
        )
        _log(self.home, self.mission_id, "worker.closed", run=run_id, status=status, reason=reason)
        tampered = [
            key for key, value in git_config_snapshot(repo, worktree).items()
            if config_before.get(key) != value
        ]
        if tampered:
            return self._config_tampered(cycle, run_id, status, len(tampered))
        if status == "interrupted":
            return Step(self._status(), "interrupted", cycle)
        if status == "failed":
            _save_revision(self.home, self.mission_id, cycle, REVISION_NO_JSON)
            if cycle >= self._max_cycles():
                return self._block("run_failed", cycle, run_id)
            return Step("active", "run_failed", cycle)

        output = result.output or {}
        if not output.get("done") and output.get("blockers"):
            self.store.record_verdict(run_id, verdict="blocked", at=self.now())
            _save_revision(self.home, self.mission_id, cycle, REVISION_BLOCKERS)
            return self._pause_with_decision(
                "clarification",
                cycle,
                run_id,
                reason="worker_blockers",
                options=["pause", "retry"],
                extra={"blockers": len(output["blockers"])},
            )
        if result.permission_denials:
            # A denial is not a verdict: the diff may already satisfy every
            # criterion. It only reaches the next brief if this cycle ends in
            # ``needs_revision`` (see ``_revise``); the count is in the event.
            denied = "\n".join(f"- {call}" for call in sorted(set(result.denied_calls))) or "- (não identificada)"
            self._denials = (
                "Estas chamadas foram negadas pelas permissões da missão; não as repita:\n"
                f"{denied}\n"
                f"Ferramentas permitidas: {allowed_tools(self.mission)}. "
                "Cumpra os critérios só com elas."
            )
        return self._verify_and_review(cycle, run_id, worktree)

    # -- verify + review ----------------------------------------------------

    def _verify_and_review(self, cycle: int, worker_run: str, worktree: Path) -> Step:
        if self._status() != "active":
            return Step(self._status(), "not_active", cycle)
        if not self._on_mission_branch(worktree):
            return self._block("branch_mismatch", cycle, worker_run, options=WORKSPACE_OPTIONS)
        base_ref = self.mission["workspace"]["baseRef"]
        files = changed_files(worktree, base_ref)
        outside = outside_write_set(files, self.mission["workspace"]["writeSet"])
        fingerprint_now = diff_fingerprint(worktree, base_ref)
        facts = {
            "diffFingerprint": fingerprint_now,
            "changedFiles": len(files),
            "outsideWriteSet": len(outside),
        }
        if self._previous_fingerprint(cycle) == fingerprint_now:
            self.store.record_verification(
                worker_run, passed=False, at=self.now(), extra={**facts, "noProgress": True}
            )
            self.store.record_verdict(worker_run, verdict="blocked", at=self.now())
            return self._block("no_progress", cycle, worker_run)
        if outside:
            self.store.record_verification(worker_run, passed=False, at=self.now(), extra=facts)
            self.store.record_verdict(worker_run, verdict="needs_revision", at=self.now())
            listed = "\n".join(f"- {path}" for path in outside)
            self._revise(
                cycle,
                "O diff anterior alterou arquivos fora do write set. Reverta estas mudanças "
                f"(inclusive commits) e mexa só no write set:\n{listed}",
            )
            return self._needs_revision(cycle, worker_run, "outside_write_set")

        results = verify_criteria(self.mission, worktree, check_timeout=self.check_timeout)
        for item in results:
            self.store.record_evidence(
                self.mission_id,
                criterion_id=item.id,
                run_id=worker_run,
                satisfied=item.satisfied,
                evidence_ref=item.evidence_ref,
                evidence_fingerprint=item.evidence_fingerprint,
                at=self.now(),
            )
        failed = [item for item in results if not item.satisfied]
        self.store.record_verification(
            worker_run,
            passed=not failed,
            at=self.now(),
            extra={**facts, "criteriaChecked": len(results), "criteriaFailed": len(failed)},
        )
        if failed:
            self.store.record_verdict(worker_run, verdict="needs_revision", at=self.now())
            lines = []
            for item in failed:
                criterion = self._criterion(item.id)
                detail = (
                    f"`{criterion['command']}` saiu com {item.evidence_ref.rsplit(':', 1)[-1]}"
                    if criterion["kind"] == "check"
                    else f"`{criterion['path']}` ausente ou sem casar o padrão"
                )
                lines.append(f"- {item.id}: {detail}")
            self._revise(
                cycle, "A verificação determinística reprovou estes critérios:\n" + "\n".join(lines)
            )
            return self._needs_revision(cycle, worker_run, "criteria_failed")
        return self._review(cycle, worker_run, worktree)

    def _review(self, cycle: int, worker_run: str, worktree: Path) -> Step:
        budget = self._budget_left()
        if budget < MIN_RUN_BUDGET_USD:
            return self._budget_reached(cycle)
        if self._status() != "active":
            return Step(self._status(), "not_active", cycle)
        attempt = 1 + sum(
            1 for run in self.store.list_runs(self.mission_id)
            if run["cycle"] == cycle and run["executor"].split(":", 1)[0] == REVIEWER_EXECUTOR
        )
        review_run = self.store.open_run(
            self.mission_id,
            cycle=cycle,
            attempt=attempt,
            executor=f"{REVIEWER_EXECUTOR}:{self.reviewer_model}",
            role=REVIEWER_ROLE,
            at=self.now(),
        )
        _log(self.home, self.mission_id, "review.dispatched", run=review_run, cycle=cycle)
        try:
            review = run_review(
                self.mission,
                diff_text(worktree, self.mission["workspace"]["baseRef"]),
                claude_bin=self.claude_bin,
                cwd=worktree,
                budget_left=budget,
                model=self.reviewer_model,
                timeout=self.review_timeout,
                poll_seconds=self.poll_seconds,
                should_stop=self._should_stop,
                on_start=self._reviewer_started,
            )
        except BaseException:
            self._terminate_worker()
            self._close_run_on_error(review_run)
            raise
        finally:
            self._process = None
        claude = review.claude
        self.store.collect_run(
            review_run,
            session_id=claude.session_id,
            cost_usd=claude.cost_usd,
            num_turns=claude.num_turns,
            result_ref=None,
            result_fingerprint=claude.result_fingerprint,
            status=claude.status,
            at=self.now(),
            extra={
                "reason": _code(review.reason or claude.reason),
                "subtype": _code(claude.subtype),
                "model": _code(self.reviewer_model),
                "verdictValid": review.valid,
            },
        )
        if claude.status == "interrupted":
            return Step(self._status(), "interrupted", cycle)

        if (
            not review.valid
            and review.reason in REVIEWER_INFRA_FAILURES
            and attempt < MAX_REVIEWER_ATTEMPTS
        ):
            _log(self.home, self.mission_id, "review.retry", run=review_run, reason=review.reason)
            return self._review(cycle, worker_run, worktree)

        if review.valid:
            for criterion in self.mission["successCriteria"]:
                if criterion["kind"] == "rubric":
                    self.store.record_evidence(
                        self.mission_id,
                        criterion_id=criterion["id"],
                        run_id=review_run,
                        satisfied=review.criteria_met.get(criterion["id"]) is True,
                        evidence_ref=f"review:{criterion['id']}",
                        evidence_fingerprint=None,
                        at=self.now(),
                    )
        verdict = review.verdict
        if verdict == "satisfied" and not self._all_criteria_satisfied():
            verdict = "blocked"  # a "satisfied" without evidence for every criterion
        self.store.record_verdict(review_run, verdict=verdict, at=self.now())
        _log(self.home, self.mission_id, "review.closed", run=review_run, verdict=verdict)

        if verdict == "satisfied":
            return self._deliver(cycle, worker_run, worktree)
        if verdict == "needs_revision":
            self._revise(cycle, review.revision_instructions or REVISION_REVIEW_DEFAULT)
            return self._needs_revision(cycle, review_run, "review_needs_revision")
        if verdict == "out_of_mission":
            _save_revision(
                self.home,
                self.mission_id,
                cycle,
                review.revision_instructions or REVISION_OUT_OF_MISSION,
            )
            return self._pause_with_decision(
                "out_of_mission",
                cycle,
                review_run,
                reason="out_of_mission",
                options=["pause", "retry_within_mission"],
            )
        return self._block("review_blocked", cycle, review_run)

    # -- delivery -----------------------------------------------------------

    def _deliver(self, cycle: int, worker_run: str | None, worktree: Path) -> Step:
        delivery = self.mission["delivery"]
        if delivery["kind"] != "pull_request":
            return self._complete(cycle)
        if self._status() != "active":
            return Step(self._status(), "not_active", cycle)
        # What gets committed and published is re-checked right before each
        # step: the reviewer ran on this tree, but a resume at the ``deliver``
        # stage (or anything that ran since) may have changed it.
        refused = self._delivery_guard(cycle, worker_run, worktree)
        if refused is not None:
            return refused
        commit_if_needed(worktree, f"{self.mission_id}: ciclo {cycle} (commit do supervisor)")
        refused = self._delivery_guard(cycle, worker_run, worktree)
        if refused is not None:
            return refused
        branch = branch_name(self.mission)
        push_branch(worktree, branch)
        body = pr_body(
            self.mission,
            criteria=self.store.criteria_status(self.mission_id),
            cost_usd=self.store.total_cost_usd(self.mission_id),
            cycles=cycle,
        )
        pull = open_pr(
            worktree, self.gh_bin, pr_title(self.mission), body,
            branch=branch, base=base_branch(self.mission),
        )
        if not self._pr_recorded(pull.url):
            self.store.record_delivery(
                self.mission_id, event_type="delivery.pr_opened", ref=pull.url, at=self.now()
            )
        _log(self.home, self.mission_id, "delivery.pr", created=pull.created, number=pull.number)
        if not delivery["requireChecks"]:
            return self._complete(cycle)

        for _ in range(self.checks_max_polls):
            if not self._wait(self.checks_poll_seconds):
                return Step(self._status(), "interrupted", cycle)
            state = checks_status(self.gh_bin, branch, cwd=worktree)
            _log(self.home, self.mission_id, "delivery.checks", state=state)
            if state == "passed":
                self.store.record_delivery(
                    self.mission_id, event_type="delivery.checks_passed", ref=pull.url, at=self.now()
                )
                return self._complete(cycle)
            if state == "failed":
                self.store.record_delivery(
                    self.mission_id, event_type="delivery.checks_failed", ref=pull.url, at=self.now()
                )
                if worker_run is not None:
                    self.store.record_verdict(worker_run, verdict="needs_revision", at=self.now())
                self._revise(cycle, REVISION_CHECKS_FAILED)
                if cycle >= self._max_cycles():
                    return self._block("delivery_checks_failed", cycle, worker_run)
                return Step("active", "checks_failed", cycle)
        return self._block(
            "delivery_checks_timeout",
            cycle,
            worker_run,
            options=["stop", "keep_waiting"],
            scope="delivery",
        )

    def _config_tampered(self, cycle: int, run_id: str, run_status: str, locations: int) -> Step:
        """The repository git config changed during the worker run: nothing
        else runs (no verification, no reviewer, no commit, no push) and a
        human decides. The run's cycle is closed so a resume never delivers it."""

        _log(self.home, self.mission_id, "git_config.tampered", run=run_id, locations=locations)
        if run_status == "collected":
            self.store.record_verdict(run_id, verdict="blocked", at=self.now())
        status = self._status()
        if status == "active":
            return self._block(
                "git_config_tampered", cycle, run_id, options=["stop", "restore_and_resume"]
            )
        if status in ("paused", "blocked"):
            self.store.open_decision(
                self.mission_id,
                kind="escalation",
                context={"reason": "git_config_tampered", "cycle": cycle, "runId": run_id},
                options=["stop", "restore_and_resume"],
                safe_default="stop",
                blocked_scope="mission",
                deadline=None,
                at=self.now(),
            )
        return Step(status, "git_config_tampered", cycle)

    def _on_mission_branch(self, worktree: Path) -> bool:
        return current_branch(worktree) == branch_name(self.mission)

    def _delivery_guard(self, cycle: int, worker_run: str | None, worktree: Path) -> Step | None:
        """``blocked`` + decision when HEAD left the mission branch or the tree
        now holds changes outside the write set; ``None`` when delivery may go on."""

        if not self._on_mission_branch(worktree):
            return self._block("branch_mismatch", cycle, worker_run, options=WORKSPACE_OPTIONS)
        files = changed_files(worktree, self.mission["workspace"]["baseRef"])
        outside = outside_write_set(files, self.mission["workspace"]["writeSet"])
        if outside:
            _log(self.home, self.mission_id, "delivery.outside_write_set", files=len(outside))
            return self._block(
                "delivery_outside_write_set", cycle, worker_run, options=WORKSPACE_OPTIONS
            )
        return None

    def _complete(self, cycle: int) -> Step:
        self.store.complete(self.mission_id, at=self.now())
        return Step("completed", "completed", cycle)

    # -- routing helpers ----------------------------------------------------

    def _revise(self, cycle: int, instructions: str) -> None:
        """The next cycle's instructions; this cycle's denied calls go after them."""

        text = instructions.strip()
        if self._denials:
            text += "\n\n" + self._denials
        _save_revision(self.home, self.mission_id, cycle, text)

    def _needs_revision(self, cycle: int, run_id: str, reason: str) -> Step:
        if cycle >= self._max_cycles():
            return self._block("needs_revision_limit", cycle, run_id)
        return Step("active", reason, cycle)

    def _block(
        self,
        reason_code: str,
        cycle: int,
        run_id: str | None,
        *,
        options: list[str] | None = None,
        scope: str = "cycles",
    ) -> Step:
        self.store.block(self.mission_id, reason_code=reason_code, at=self.now())
        delegable = options is None and reason_code in DELEGABLE_REASONS
        choices = options or ["stop", GRANT_CYCLE_OPTION]
        decision_id = self.store.open_decision(
            self.mission_id,
            kind="escalation",
            context={"reason": reason_code, "cycle": cycle, "runId": run_id},
            options=choices,
            safe_default="stop",
            blocked_scope=scope,
            deadline=None,
            at=self.now(),
        )
        if delegable and self._delegate_grant_cycle(decision_id, cycle):
            return Step("active", reason_code, cycle)
        return Step("blocked", reason_code, cycle)

    def _delegate_grant_cycle(self, decision_id: str, cycle: int) -> bool:
        """Grant the cycle without asking the founder, only when the mission's
        own ``delegation.grantCycle`` rule covers it: the store still enforces
        ``maxTimes`` and the accumulated-cost fraction, so this only adds the
        cycle-shaped ``requireProgress`` check the store cannot see."""

        rule = (self.mission.get("delegation") or {}).get("grantCycle")
        if rule is None:
            return False
        if rule["requireProgress"] and not self._progressed(cycle):
            return False
        try:
            self.store.resolve_decision(
                decision_id,
                option=GRANT_CYCLE_OPTION,
                decided_by=DELEGATED_ORCHESTRATOR_SOURCE,
                at=self.now(),
            )
        except (ControlPlaneContractError, ControlPlaneStateError):
            return False
        self.store.resume(self.mission_id, at=self.now())
        _log(self.home, self.mission_id, "decision.delegated", decision=decision_id, cycle=cycle)
        return True

    def _progressed(self, cycle: int) -> bool:
        """More criteria satisfied at the end of *cycle* than at the end of
        the previous one; the first cycle compares against zero."""

        def satisfied(up_to: int) -> int:
            return sum(1 for item in self.store.criteria_status(self.mission_id, up_to_cycle=up_to) if item["satisfied"])

        previous = satisfied(cycle - 1) if cycle > 1 else 0
        return satisfied(cycle) > previous

    def _budget_reached(self, cycle: int) -> Step:
        self.store.block(self.mission_id, reason_code="budget_reached", at=self.now())
        self.store.open_decision(
            self.mission_id,
            kind="budget",
            context={
                "reason": "budget_reached",
                "cycle": cycle,
                "costUsd": round(self.store.total_cost_usd(self.mission_id), 4),
            },
            options=["stop", "revise_mission"],
            safe_default="stop",
            blocked_scope="budget",
            deadline=None,
            at=self.now(),
        )
        return Step("blocked", "budget_reached", cycle)

    def _pause_with_decision(
        self,
        kind: str,
        cycle: int,
        run_id: str,
        *,
        reason: str,
        options: list[str],
        extra: Mapping[str, Any] | None = None,
    ) -> Step:
        self.store.pause(self.mission_id, at=self.now())
        self.store.open_decision(
            self.mission_id,
            kind=kind,
            context={"reason": reason, "cycle": cycle, "runId": run_id, **dict(extra or {})},
            options=options,
            safe_default="pause",
            blocked_scope="mission",
            deadline=None,
            at=self.now(),
        )
        return Step("paused", reason, cycle)

    # -- state readers ------------------------------------------------------

    def _status(self) -> str:
        return self.store.get(self.mission_id)["status"]

    def _should_stop(self) -> bool:
        return self.stop.is_set() or self._status() != "active"

    def _wait(self, seconds: float) -> bool:
        """Sleep ``seconds`` in ``poll_seconds`` slices; False when a stop was requested."""

        deadline = time.monotonic() + seconds
        while True:
            if self._should_stop():
                return False
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return True
            self.sleep(min(self.poll_seconds, remaining))

    def _budget_left(self) -> float:
        return float(self.mission["constraints"]["maxBudgetUsd"]) - self.store.total_cost_usd(
            self.mission_id
        )

    def _max_cycles(self) -> int:
        granted = sum(
            1
            for decision in self.store.list_decisions(self.mission_id)
            if decision["status"] == "resolved" and decision["decidedOption"] == GRANT_CYCLE_OPTION
        )
        return int(self.mission["constraints"]["maxCycles"]) + granted

    def _cycle_verdict(self, cycle: int) -> str | None:
        verdict = None
        for event in self.store.list_events(self.mission_id):
            if event["eventType"].startswith("review.") and event["payload"].get("cycle") == cycle:
                verdict = event["eventType"].split(".", 1)[1]
        return verdict

    def _previous_fingerprint(self, cycle: int) -> str | None:
        previous = None
        for event in self.store.list_events(self.mission_id):
            if event["eventType"].startswith("verify.") and event["payload"].get("cycle") == cycle - 1:
                previous = event["payload"].get("diffFingerprint", previous)
        return previous

    def _pr_recorded(self, url: str) -> bool:
        return any(
            event["eventType"] == "delivery.pr_opened" and event["payload"].get("ref") == url
            for event in self.store.list_events(self.mission_id)
        )

    def _all_criteria_satisfied(self) -> bool:
        return all(item["satisfied"] for item in self.store.criteria_status(self.mission_id))

    def _criterion(self, criterion_id: str) -> dict[str, Any]:
        return next(item for item in self.mission["successCriteria"] if item["id"] == criterion_id)

    def _worker_started(self, process: ClaudeProcess) -> None:
        self._process = process
        if process.pid is not None:
            _write_private(self.home / self.mission_id / WORKER_PID_FILE, f"{process.pid}\n")

    def _reviewer_started(self, process: ClaudeProcess) -> None:
        self._process = process

    def _terminate_worker(self) -> None:
        """Never leave a ghost writer in the worktree when the supervisor fails."""

        process = self._process
        if process is not None:
            try:
                process.terminate(grace_seconds=2.0)
            except OSError:
                pass

    def _close_run_on_error(self, run_id: str) -> None:
        """A supervisor error must not leave a ``running`` run behind (it would
        be reconciled to ``unknown``): close it as ``failed``."""

        try:
            self.store.collect_run(
                run_id, session_id=None, cost_usd=0, num_turns=0, result_ref=None,
                result_fingerprint=None, status="failed", at=self.now(),
                extra={"reason": "supervisor_error"},
            )
        except ControlPlaneStateError:
            pass


# -- module helpers ------------------------------------------------------------


def _home(home: str | Path | None) -> Path:
    return Path(home).expanduser() if home is not None else default_mission_home()


def _mission_dir(home: Path, mission_id: str) -> Path:
    directory = mission_home(mission_id, home)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(directory, 0o700)
    except OSError:
        pass
    return directory


def _require_chain(store: MissionStore, mission_id: str) -> None:
    if not store.verify_chain(mission_id):
        raise SupervisorRefusal("mission audit chain is invalid; the supervisor refuses to continue")


def _require_single_writer(home: Path, mission_id: str) -> None:
    pid = live_supervisor_pid(home, mission_id)
    if pid is not None and pid != os.getpid():
        raise SupervisorRefusal("another supervisor is alive for this mission")


def _worker_pid(home: Path, mission_id: str) -> int | None:
    try:
        pid = int((home / mission_id / WORKER_PID_FILE).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    return pid if pid > 0 else None


def _process_state(pid: int) -> tuple[str, str] | None:
    """``(stat, command line)`` of ``pid`` from ``ps``, or ``None`` if gone."""

    try:
        completed = subprocess.run(
            ["ps", "-ww", "-o", "stat=", "-o", "command=", "-p", str(pid)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = completed.stdout.strip()
    if completed.returncode != 0 or not output:
        return None
    stat, _, command = output.partition(" ")
    return stat, command.strip()


def _running(pid: int) -> bool:
    state = _process_state(pid)
    return state is not None and not state[0].startswith("Z")


def _is_orphan_worker(pid: int, claude_bin: str) -> bool:
    """Guard against pid reuse: the worker was started with
    ``start_new_session`` (so it leads its session) as ``<claude_bin> -p …``
    (a script shows up as ``<interpreter> <claude_bin> -p …``)."""

    try:
        if os.getsid(pid) != pid:
            return False
    except OSError:
        return False
    state = _process_state(pid)
    if state is None or state[0].startswith("Z"):
        return False
    command = state[1]
    candidates = {claude_bin}
    if os.sep in claude_bin:
        candidates.add(os.path.realpath(claude_bin))
    else:
        found = shutil.which(claude_bin)
        if found:
            candidates.update({found, os.path.realpath(found)})
    for candidate in candidates:
        pattern = r"^(?:\S+\s+)?" + re.escape(candidate) + r"\s+-p(?:\s|$)"
        if re.match(pattern, command):
            return True
    return False


def _kill_session(pid: int, *, grace_seconds: float) -> bool:
    """SIGTERM the worker's process group, SIGKILL it after the grace period
    (always, like ``ClaudeProcess.terminate``). True once the leader is gone."""

    try:
        os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    deadline = time.monotonic() + grace_seconds
    while _running(pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    deadline = time.monotonic() + grace_seconds
    while _running(pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    return not _running(pid)


def _revision_path(home: Path, mission_id: str, cycle: int) -> Path:
    return home / mission_id / REVISIONS_DIR / f"cycle-{cycle}.md"


def _save_revision(home: Path, mission_id: str, cycle: int, text: str) -> None:
    path = _revision_path(home, mission_id, cycle)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_private(path, text.strip() + "\n")


def _load_revision(home: Path, mission_id: str, cycle: int) -> str | None:
    if cycle < 1:
        return None
    try:
        return _revision_path(home, mission_id, cycle).read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def _write_private(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.chmod(path, 0o600)


def _remove(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def _code(value: Any) -> str | None:
    """A reason/model code safe for an event payload, or ``None``."""

    if not isinstance(value, str) or not value:
        return None
    try:
        return safe_identifier(value, limit=128)
    except ControlPlaneContractError:
        return None


def _log(home: Path, mission_id: str, event: str, **fields: Any) -> None:
    """One line per supervisor event: timestamp, event, ids/codes/counts only."""

    parts = [utc_now(), event]
    for key, value in fields.items():
        if isinstance(value, bool) or value is None or isinstance(value, (int, float)):
            rendered = str(value).lower() if isinstance(value, bool) else str(value)
        else:
            rendered = _code(str(value)) or "-"
        parts.append(f"{key}={rendered}")
    try:
        path = _mission_dir(home, mission_id) / SUPERVISOR_LOG_FILE
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
            handle.write(" ".join(parts) + "\n")
    except OSError:
        pass


def _install_stop_handlers(stop: threading.Event) -> dict[int, Any]:
    if threading.current_thread() is not threading.main_thread():
        return {}
    previous: dict[int, Any] = {}

    def request_stop(_signum: int, _frame: Any) -> None:
        stop.set()

    for signum in STOP_SIGNALS:
        previous[signum] = signal.signal(signum, request_stop)
    return previous


def _restore_stop_handlers(previous: dict[int, Any]) -> None:
    for signum, handler in previous.items():
        signal.signal(signum, handler)
