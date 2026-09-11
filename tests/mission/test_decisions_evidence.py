from __future__ import annotations

from unittest import TestCase

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
)
from pipe_venture_builder.mission.contract import build_mission, is_human_source
from pipe_venture_builder.mission.store import MissionStore
from tests.mission.helpers import CREATED_AT, EVEN_LATER, LATER, mission_input

FP = "sha256:" + "c" * 64


def active_mission(store: MissionStore) -> str:
    mission_id = store.create(build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT)
    store.activate(mission_id, at=LATER)
    return mission_id


def open_default_decision(store: MissionStore, mission_id: str, **overrides) -> str:
    kwargs = dict(
        kind="out_of_mission",
        context={"runId": "MRUN-000000000001", "cycle": 2, "verdict": "out_of_mission"},
        options=["pause", "continue", "cancel"],
        safe_default="pause",
        blocked_scope="mission",
        deadline=None,
        at=LATER,
    )
    kwargs.update(overrides)
    return store.open_decision(mission_id, **kwargs)


class DecisionTests(TestCase):
    def test_open_and_list_pending_decisions(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id, deadline=EVEN_LATER)
            self.assertRegex(decision_id, r"^DEC-[a-f0-9]{12}$")
            pending = store.pending_decisions(mission_id)
            self.assertEqual(len(pending), 1)
            decision = pending[0]
            self.assertEqual(decision["status"], "pending")
            self.assertEqual(decision["context"]["cycle"], 2)
            self.assertEqual(decision["options"], ["pause", "continue", "cancel"])
            self.assertEqual(decision["safeDefault"], "pause")
            self.assertEqual(decision["blockedScope"], "mission")
            self.assertEqual(decision["deadline"], EVEN_LATER)
            self.assertEqual(store.list_events(mission_id)[-1]["eventType"], "decision.opened")
            self.assertEqual(
                open_default_decision(store, mission_id, deadline=EVEN_LATER, at=EVEN_LATER),
                decision_id,
                "same pending decision must not be duplicated",
            )
            self.assertEqual(len(store.pending_decisions(mission_id)), 1)

    def test_open_decision_validates_shape(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            bad = {
                "kind": {"kind": "vibes"},
                "one option": {"options": ["pause"], "safe_default": "pause"},
                "default outside options": {"safe_default": "explode"},
                "free text context": {"context": {"note": "free text here"}},
                "secret context": {"context": {"ref": "sk-never-persist-this-value-1234567890"}},
                "bad deadline": {"deadline": "tomorrow"},
                "free text scope": {"blocked_scope": "the whole thing"},
            }
            for label, override in bad.items():
                with self.subTest(label):
                    with self.assertRaises(ControlPlaneContractError):
                        open_default_decision(store, mission_id, **override)
            self.assertEqual(store.pending_decisions(mission_id), [])
            self.assertEqual(len(store.list_events(mission_id)), 2)

    def test_decision_requires_live_mission(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = store.create(
                build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
            )
            with self.assertRaises(ControlPlaneStateError):
                open_default_decision(store, mission_id)

    def test_resolve_decision_by_human_source(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id)
            resolved = store.resolve_decision(
                decision_id, option="continue", decided_by="human:chat:vitor", at=EVEN_LATER
            )
            self.assertEqual(resolved["status"], "resolved")
            self.assertEqual(resolved["decidedOption"], "continue")
            self.assertEqual(resolved["decidedBy"], "human:chat:vitor")
            self.assertEqual(resolved["decidedAt"], EVEN_LATER)
            self.assertEqual(store.pending_decisions(mission_id), [])
            self.assertEqual(store.list_events(mission_id)[-1]["eventType"], "decision.resolved")
            with self.assertRaises(ControlPlaneStateError):
                store.resolve_decision(
                    decision_id, option="pause", decided_by="human:chat:vitor", at=EVEN_LATER
                )

    def test_decision_from_agent_source_is_refused(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id)
            for source in (
                "agent:claude-code:worker",
                "supervisor",
                "human:",
                "human:chat:",
                "human:slack:vitor",
                "",
                "human:chat:vitor with spaces",
            ):
                with self.subTest(source):
                    self.assertFalse(is_human_source(source))
                    with self.assertRaises(ControlPlaneContractError):
                        store.resolve_decision(
                            decision_id, option="pause", decided_by=source, at=EVEN_LATER
                        )
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(
                    decision_id, option="explode", decided_by="human:cli:vitor", at=EVEN_LATER
                )
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")
            for source in ("human:chat:vitor", "human:linear:PIP-901", "human:cli:vitor"):
                self.assertTrue(is_human_source(source))

    def test_blocked_mission_resumes_only_after_decisions_resolve(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id)
            store.block(mission_id, reason_code="out_of_mission", at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.resume(mission_id, at=EVEN_LATER)
            store.resolve_decision(
                decision_id, option="continue", decided_by="human:cli:vitor", at=EVEN_LATER
            )
            store.resume(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")


def delegated_mission(store: MissionStore, **grant_cycle: object) -> str:
    rule = {"maxTimes": 1, "maxCostFraction": 0.5, "requireProgress": True}
    rule.update(grant_cycle)
    document = {**mission_input(), "schemaVersion": "0.2.0", "delegation": {"grantCycle": rule}}
    mission_id = store.create(build_mission(document, created_at=CREATED_AT), at=CREATED_AT)
    store.activate(mission_id, at=LATER)
    return mission_id


class DelegatedDecisionTests(TestCase):
    """``resolve_decision(..., decided_by="delegated:orchestrator")``: the store
    enforces the shape (escalation/grant_cycle) and the mission's own
    ``maxTimes``/``maxCostFraction``; the supervisor's acceptance tests cover
    the end-to-end cycle-granting behaviour built on top of this."""

    def _open_grant_cycle_decision(self, store: MissionStore, mission_id: str, *, cycle: int = 1) -> str:
        store.block(mission_id, reason_code="max_cycles", at=LATER)
        return store.open_decision(
            mission_id, kind="escalation", context={"reason": "max_cycles", "cycle": cycle},
            options=["stop", "grant_cycle"], safe_default="stop", blocked_scope="cycles",
            deadline=None, at=LATER,
        )

    def test_delegated_grant_marks_resolved_with_the_delegated_source(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)
            decision_id = self._open_grant_cycle_decision(store, mission_id)
            resolved = store.resolve_decision(
                decision_id, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
            )
            self.assertEqual(resolved["status"], "resolved")
            self.assertEqual(resolved["decidedOption"], "grant_cycle")
            self.assertEqual(resolved["decidedBy"], "delegated:orchestrator")
            event = store.list_events(mission_id)[-1]
            self.assertEqual(event["eventType"], "decision.delegated")
            self.assertEqual(event["payload"], {"decisionId": decision_id, "rule": "grantCycle"})

    # Revisão 2 do PIP-903, achado #3: cada checagem do store (opção, kind,
    # regra) tem um teste que só ela reprova — as outras passam.

    def test_delegated_source_cannot_choose_any_option_but_grant_cycle(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)
            decision_id = self._open_grant_cycle_decision(store, mission_id)
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(decision_id, option="stop", decided_by="delegated:orchestrator", at=EVEN_LATER)
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_delegated_grant_cycle_refused_on_a_non_escalation_decision(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)
            store.block(mission_id, reason_code="max_cycles", at=LATER)
            decision_id = store.open_decision(
                mission_id, kind="clarification", context={"reason": "max_cycles", "cycle": 1},
                options=["pause", "grant_cycle"], safe_default="pause", blocked_scope="mission",
                deadline=None, at=LATER,
            )
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(
                    decision_id, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
                )
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_delegated_grant_refused_when_the_mission_has_no_rule(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = self._open_grant_cycle_decision(store, mission_id)
            with self.assertRaises((ControlPlaneContractError, ControlPlaneStateError)):
                store.resolve_decision(
                    decision_id, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
                )
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_delegated_grant_refused_for_a_decision_kind_delegation_never_covers(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)
            store.block(mission_id, reason_code="budget_reached", at=LATER)
            budget_decision = store.open_decision(
                mission_id, kind="budget", context={"reason": "budget_reached"},
                options=["stop", "revise_mission"], safe_default="stop", blocked_scope="budget",
                deadline=None, at=LATER,
            )
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(
                    budget_decision, option="revise_mission",
                    decided_by="delegated:orchestrator", at=EVEN_LATER,
                )
            self.assertEqual(store.get_decision(budget_decision)["status"], "pending")

    def test_delegated_grant_respects_max_times(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store, maxTimes=1)
            first = self._open_grant_cycle_decision(store, mission_id)
            store.resolve_decision(
                first, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
            )
            store.resume(mission_id, at=EVEN_LATER)
            second = self._open_grant_cycle_decision(store, mission_id, cycle=2)
            with self.assertRaises(ControlPlaneStateError):
                store.resolve_decision(
                    second, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
                )
            # A human is never blocked by the exhausted delegation rule.
            store.resolve_decision(second, option="stop", decided_by="human:cli:vitor", at=EVEN_LATER)

    def test_delegated_grant_respects_cost_fraction(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store, maxCostFraction=0.1)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="worker:sonnet", at=LATER)
            budget = store.get(mission_id)["constraints"]["maxBudgetUsd"]
            store.collect_run(
                run_id, session_id=None, cost_usd=budget * 0.2, num_turns=1,
                result_ref=None, result_fingerprint=None, status="collected", at=LATER,
            )
            decision_id = self._open_grant_cycle_decision(store, mission_id)
            with self.assertRaises(ControlPlaneStateError):
                store.resolve_decision(
                    decision_id, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
                )

    def test_delegated_grant_accepts_cost_exactly_at_the_fraction(self) -> None:
        # cost/maxBudgetUsd == maxCostFraction must grant; only strictly above
        # refuses (a ``>=`` mutant would refuse here).
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store, maxCostFraction=0.5)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="worker:sonnet", at=LATER)
            budget = store.get(mission_id)["constraints"]["maxBudgetUsd"]
            store.collect_run(
                run_id, session_id=None, cost_usd=budget * 0.5, num_turns=1,
                result_ref=None, result_fingerprint=None, status="collected", at=LATER,
            )
            decision_id = self._open_grant_cycle_decision(store, mission_id)
            resolved = store.resolve_decision(
                decision_id, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER
            )
            self.assertEqual(resolved["status"], "resolved")

    def test_delegated_grant_refused_for_a_reason_outside_the_cycle_limit(self) -> None:
        """The store, not just the supervisor, is the enforcement point: a
        decision opened with any other ``context.reason`` (a legitimate
        reviewer verdict, the circuit breaker, an escalated worker or
        delivery failure) is never resolvable by ``delegated:orchestrator``,
        even though it is ``kind: escalation`` / option ``grant_cycle`` and
        the mission declares a covering rule."""

        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)
            for reason in ("no_progress", "review_blocked", "run_failed", "delivery_checks_failed"):
                with self.subTest(reason):
                    store.block(mission_id, reason_code=reason, at=LATER)
                    decision_id = store.open_decision(
                        mission_id, kind="escalation", context={"reason": reason, "cycle": 1},
                        options=["stop", "grant_cycle"], safe_default="stop", blocked_scope="cycles",
                        deadline=None, at=LATER,
                    )
                    with self.assertRaises(ControlPlaneContractError):
                        store.resolve_decision(
                            decision_id, option="grant_cycle",
                            decided_by="delegated:orchestrator", at=EVEN_LATER,
                        )
                    self.assertEqual(store.get_decision(decision_id)["status"], "pending")
                    # A human is never blocked by the reason restriction.
                    store.resolve_decision(
                        decision_id, option="stop", decided_by="human:cli:vitor", at=EVEN_LATER
                    )
                    store.resume(mission_id, at=EVEN_LATER)

    def test_delegated_source_other_than_orchestrator_is_refused(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)
            decision_id = self._open_grant_cycle_decision(store, mission_id)
            for source in ("delegated:", "delegated:other", "delegated:orchestrator ", "Delegated:orchestrator"):
                with self.subTest(source):
                    with self.assertRaises(ControlPlaneContractError):
                        store.resolve_decision(
                            decision_id, option="grant_cycle", decided_by=source, at=EVEN_LATER
                        )
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")


def answer_blockers_mission(store: MissionStore, **overrides: object) -> str:
    rule = {"maxTimes": 1}
    rule.update(overrides)
    document = {**mission_input(), "schemaVersion": "0.2.0", "delegation": {"answerBlockers": rule}}
    mission_id = store.create(build_mission(document, created_at=CREATED_AT), at=CREATED_AT)
    store.activate(mission_id, at=LATER)
    return mission_id


class AnswerBlockersDelegatedDecisionTests(TestCase):
    """PIP-906: the store-level half of ``delegation.answerBlockers`` — the
    supervisor's acceptance tests cover the end-to-end responder cycle built
    on top of this. Each check here is one that, removed, would let
    ``resolve_decision(decided_by="delegated:orchestrator")`` answer
    something only the founder should (a merge, a different decision kind,
    an unrelated ``clarification`` reason, or an exhausted rule)."""

    def _open_worker_blockers_decision(
        self, store: MissionStore, mission_id: str, *, reason: str = "worker_blockers", cycle: int = 1
    ) -> str:
        store.pause(mission_id, at=LATER)
        return store.open_decision(
            mission_id, kind="clarification", context={"reason": reason, "cycle": cycle},
            options=["pause", "retry"], safe_default="pause", blocked_scope="mission",
            deadline=None, at=LATER,
        )

    def test_delegated_retry_marks_resolved_with_the_answer_blockers_rule(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = answer_blockers_mission(store)
            decision_id = self._open_worker_blockers_decision(store, mission_id)
            resolved = store.resolve_decision(
                decision_id, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER
            )
            self.assertEqual(resolved["status"], "resolved")
            self.assertEqual(resolved["decidedOption"], "retry")
            self.assertEqual(resolved["decidedBy"], "delegated:orchestrator")
            event = store.list_events(mission_id)[-1]
            self.assertEqual(event["eventType"], "decision.delegated")
            self.assertEqual(event["payload"], {"decisionId": decision_id, "rule": "answerBlockers"})

    def test_delegated_source_cannot_choose_pause_for_a_worker_blockers_decision(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = answer_blockers_mission(store)
            decision_id = self._open_worker_blockers_decision(store, mission_id)
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(decision_id, option="pause", decided_by="delegated:orchestrator", at=EVEN_LATER)
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_delegated_retry_refused_for_a_clarification_reason_other_than_worker_blockers(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = answer_blockers_mission(store)
            decision_id = self._open_worker_blockers_decision(store, mission_id, reason="out_of_mission")
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(decision_id, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER)
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_delegated_retry_refused_on_an_escalation_decision(self) -> None:
        # Same option string ("retry" is not used by grant_cycle, but the
        # kind check must still hold on its own): a `worker_blockers`-shaped
        # context under the wrong decision kind is never covered.
        with MissionStore(":memory:") as store:
            mission_id = answer_blockers_mission(store)
            store.block(mission_id, reason_code="max_cycles", at=LATER)
            decision_id = store.open_decision(
                mission_id, kind="escalation", context={"reason": "worker_blockers", "cycle": 1},
                options=["stop", "retry"], safe_default="stop", blocked_scope="mission",
                deadline=None, at=LATER,
            )
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(decision_id, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER)
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_delegated_retry_refused_when_the_mission_has_no_answer_blockers_rule(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)  # no delegation at all
            decision_id = self._open_worker_blockers_decision(store, mission_id)
            with self.assertRaises((ControlPlaneContractError, ControlPlaneStateError)):
                store.resolve_decision(decision_id, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER)
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")

    def test_a_grant_cycle_only_mission_does_not_cover_answer_blockers(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = delegated_mission(store)  # grantCycle only
            decision_id = self._open_worker_blockers_decision(store, mission_id)
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(decision_id, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER)

    def test_answer_blockers_max_times_is_enforced(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = answer_blockers_mission(store, maxTimes=1)
            first = self._open_worker_blockers_decision(store, mission_id, cycle=1)
            store.resolve_decision(first, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER)
            store.resume(mission_id, at=EVEN_LATER)
            second = self._open_worker_blockers_decision(store, mission_id, cycle=2)
            with self.assertRaises(ControlPlaneStateError):
                store.resolve_decision(second, option="retry", decided_by="delegated:orchestrator", at=EVEN_LATER)
            self.assertEqual(store.get_decision(second)["status"], "pending")

    def test_answer_blockers_rule_never_grants_a_cycle(self) -> None:
        # The counterpart of DelegatedDecisionTests' grant_cycle-only checks:
        # an ``answerBlockers`` rule must not let a delegated source resolve
        # the unrelated ``escalation``/``grant_cycle`` decision.
        with MissionStore(":memory:") as store:
            mission_id = answer_blockers_mission(store)
            store.block(mission_id, reason_code="max_cycles", at=LATER)
            decision_id = store.open_decision(
                mission_id, kind="escalation", context={"reason": "max_cycles", "cycle": 1},
                options=["stop", "grant_cycle"], safe_default="stop", blocked_scope="cycles",
                deadline=None, at=LATER,
            )
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(decision_id, option="grant_cycle", decided_by="delegated:orchestrator", at=EVEN_LATER)


class EvidenceAndCompletionTests(TestCase):
    def _satisfy_all(self, store: MissionStore, mission_id: str, run_id: str) -> None:
        for criterion in store.get(mission_id)["successCriteria"]:
            store.record_evidence(
                mission_id,
                criterion_id=criterion["id"],
                run_id=run_id,
                satisfied=True,
                evidence_ref=f"evidence:{criterion['id']}",
                evidence_fingerprint=FP,
                at=EVEN_LATER,
            )

    def _delivered(self, store: MissionStore, mission_id: str) -> None:
        store.record_delivery(mission_id, event_type="delivery.pr_opened", ref="pr:1", at=EVEN_LATER)
        store.record_delivery(
            mission_id, event_type="delivery.checks_passed", ref="pr:1", at=EVEN_LATER
        )

    def test_complete_without_full_evidence_is_refused(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._delivered(store, mission_id)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_evidence(
                mission_id, criterion_id="C1", run_id=run_id, satisfied=True,
                evidence_ref="evidence:C1", evidence_fingerprint=FP, at=EVEN_LATER,
            )
            store.record_evidence(
                mission_id, criterion_id="C2", run_id=run_id, satisfied=True,
                evidence_ref="evidence:C2", evidence_fingerprint=FP, at=EVEN_LATER,
            )
            store.record_evidence(
                mission_id, criterion_id="C3", run_id=run_id, satisfied=False,
                evidence_ref=None, evidence_fingerprint=None, at=EVEN_LATER,
            )
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            self.assertNotIn(
                "mission.completed",
                [event["eventType"] for event in store.list_events(mission_id)],
            )
            status = [item["satisfied"] for item in store.criteria_status(mission_id)]
            self.assertEqual(status, [True, True, False])

    def test_latest_evidence_wins_and_complete_succeeds(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            store.record_evidence(
                mission_id, criterion_id="C1", run_id=run_id, satisfied=False,
                evidence_ref=None, evidence_fingerprint=None, at=LATER,
            )
            self._satisfy_all(store, mission_id, run_id)
            self._delivered(store, mission_id)
            store.complete(mission_id, at=EVEN_LATER)
            document = store.get(mission_id)
            self.assertEqual(document["status"], "completed")
            last = store.list_events(mission_id)[-1]
            self.assertEqual(last["eventType"], "mission.completed")
            self.assertEqual(last["payload"]["criteria"], 3)
            self.assertTrue(store.verify_chain(mission_id))

    def test_complete_requires_delivery_when_pull_request_declared(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._satisfy_all(store, mission_id, run_id)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_delivery(mission_id, event_type="delivery.pr_opened", ref="pr:1", at=EVEN_LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_delivery(
                mission_id, event_type="delivery.checks_failed", ref="pr:1", at=EVEN_LATER
            )
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_delivery(
                mission_id, event_type="delivery.checks_passed", ref="pr:1", at=EVEN_LATER
            )
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_checks_failed_then_passed_allows_complete(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._satisfy_all(store, mission_id, run_id)
            store.record_delivery(mission_id, event_type="delivery.pr_opened", ref="pr:1", at=EVEN_LATER)
            store.record_delivery(
                mission_id, event_type="delivery.checks_failed", ref="pr:1", at=EVEN_LATER
            )
            store.record_delivery(
                mission_id, event_type="delivery.checks_passed", ref="pr:1", at=EVEN_LATER
            )
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_checks_passed_then_failed_refuses_complete(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._satisfy_all(store, mission_id, run_id)
            self._delivered(store, mission_id)
            store.record_delivery(
                mission_id, event_type="delivery.checks_failed", ref="pr:1", at=EVEN_LATER
            )
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            store.record_delivery(
                mission_id, event_type="delivery.checks_passed", ref="pr:1", at=EVEN_LATER
            )
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_new_pr_opened_resets_passed_checks(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._satisfy_all(store, mission_id, run_id)
            self._delivered(store, mission_id)
            store.record_delivery(mission_id, event_type="delivery.pr_opened", ref="pr:2", at=EVEN_LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            store.record_delivery(
                mission_id, event_type="delivery.checks_passed", ref="pr:2", at=EVEN_LATER
            )
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_complete_without_delivery_requirement(self) -> None:
        draft = mission_input()
        draft["delivery"] = {"kind": "none", "requireChecks": False}
        with MissionStore(":memory:") as store:
            mission_id = store.create(build_mission(draft, created_at=CREATED_AT), at=CREATED_AT)
            store.activate(mission_id, at=LATER)
            self._satisfy_all(store, mission_id, None)
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_complete_refuses_pending_decisions_and_broken_chain(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            self._satisfy_all(store, mission_id, None)
            self._delivered(store, mission_id)
            decision_id = open_default_decision(store, mission_id)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.resolve_decision(
                decision_id, option="continue", decided_by="human:chat:vitor", at=EVEN_LATER
            )
            store._connection.execute(
                "UPDATE mission_events SET event_hash = 'sha256:' || substr('f' || event_hash, 1, 64)"
                " WHERE mission_id = ? AND sequence = 1",
                (mission_id,),
            )
            store._connection.commit()
            self.assertFalse(store.verify_chain(mission_id))
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")

    def test_evidence_validates_criterion_run_and_shape(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            other = store.create(
                build_mission({**mission_input(), "title": "outra"}, created_at=CREATED_AT),
                at=CREATED_AT,
            )
            store.activate(other, at=LATER)
            other_run = store.open_run(other, cycle=1, attempt=1, executor="claude-code", at=LATER)
            base = dict(
                criterion_id="C1", run_id=None, satisfied=True,
                evidence_ref="evidence:C1", evidence_fingerprint=FP, at=LATER,
            )
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "criterion_id": "C9"})
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "satisfied": "yes"})
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "evidence_ref": "has spaces"})
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "evidence_fingerprint": "nope"})
            with self.assertRaises(ControlPlaneStateError):
                store.record_evidence(mission_id, **{**base, "run_id": other_run})
            self.assertEqual(
                [item["satisfied"] for item in store.criteria_status(mission_id)],
                [False, False, False],
            )
