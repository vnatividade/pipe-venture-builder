"""PIP-910, revisão adversarial: os defeitos achados DEPOIS do CI verde.

Cada classe aqui prende um achado que a suíte original deixava passar. Todos
foram reproduzidos por execução antes de serem corrigidos; estes testes são o
que impede a volta deles.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pipe_venture_builder.control_plane.model import ControlPlaneStateError, utc_now
from pipe_venture_builder.mission.program_supervisor import _leaf_stage_ids, supervise_program
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.program import build_program

from tests.mission.helpers import mission_input
from tests.mission.loop_helpers import git
from tests.mission.test_program import (
    ProgramTestCase,
    delivered,
    program_document,
    satisfied,
    stage,
    writes,
)


class HooksOffTests(ProgramTestCase):
    """P1: ``git worktree add`` do ``startWhen`` roda ``post-checkout``.

    O diretório de hooks é o COMPARTILHADO do repositório — alcançável de
    dentro do worktree de uma onda, que fica fora do write set daquela missão e
    fora do diff que o revisor vê. Sem ``core.hooksPath=/dev/null``, um hook
    escrito pelo worker de uma onda executa no supervisor do programa, com as
    credenciais dele.
    """

    def _plant_hook(self, repo: Path, marker: Path) -> None:
        hooks = Path(
            subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "--git-common-dir"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
        )
        if not hooks.is_absolute():
            hooks = repo / hooks
        hooks = hooks / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        hook = hooks / "post-checkout"
        hook.write_text(f'#!/bin/sh\necho rodou > "{marker}"\n', encoding="utf-8")
        hook.chmod(0o755)

    def test_the_repository_post_checkout_hook_never_runs_in_a_start_when_worktree(self) -> None:
        h = self.program_harness([stage("a"), stage("b", depends=["a"], start_when=delivered("a"))])
        marker = self.root / "hook-rodou.txt"
        self._plant_hook(h.repo, marker)

        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        h.run()

        self.assertFalse(
            marker.exists(),
            "o post-checkout do repositorio rodou dentro do worktree descartavel do startWhen",
        )

    def test_the_planted_hook_would_run_without_the_guard(self) -> None:
        """Controle: o hook plantado É executável e roda num ``worktree add``
        comum. Sem isto, o teste acima passaria mesmo com o hook quebrado."""

        h = self.program_harness([stage("a")])
        marker = self.root / "controle-hook.txt"
        self._plant_hook(h.repo, marker)
        destino = self.root / "wt-controle"
        subprocess.run(
            ["git", "-C", str(h.repo), "worktree", "add", "--detach", str(destino), "HEAD"],
            capture_output=True, check=True,
        )
        self.assertTrue(marker.exists(), "o hook de controle nao rodou — o teste acima e vazio")


class StartWhenBaseTests(ProgramTestCase):
    """P1: o portão aprovava um artefato que a onda não ia enxergar."""

    def _has(self, repo: Path, ref: str, path: str) -> bool:
        return subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{ref}:{path}"], capture_output=True
        ).returncode == 0

    def test_a_start_when_met_only_outside_the_chain_from_base_blocks(self) -> None:
        # `c` encadeia por `a`, mas o portão cobra a entrega de `b`: como o
        # programa não mergeia, `c` nunca veria docs/b.md — então bloqueia.
        h = self.program_harness([
            stage("a"), stage("b"),
            stage("c", depends=["a", "b"], chainFrom="a", start_when=delivered("b")),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b"), writes("c")],
                         reviewer=[satisfied(), satisfied(), satisfied()])
        step = h.run()

        self.assertIsNone(h.missions().get("c"), "a onda c nao pode nascer sobre areia")
        self.assertEqual(step.reason, "start_when_unsatisfied")
        pending = h.store.list_decisions(h.program_id, pending_only=True)
        self.assertTrue(any(d["context"].get("stage") == "c" for d in pending))

    def test_a_start_when_met_on_the_chain_from_base_proceeds(self) -> None:
        """Controle positivo: mesmo grafo, portão cobrando a própria
        ``chainFrom`` — a onda começa, e começa numa base que tem o arquivo."""

        h = self.program_harness([
            stage("a"), stage("b"),
            stage("c", depends=["a", "b"], chainFrom="a", start_when=delivered("a")),
        ])
        h.fakes.scenario(worker=[writes("a"), writes("b"), writes("c")],
                         reviewer=[satisfied(), satisfied(), satisfied()])
        h.run()

        mission_id = h.missions().get("c")
        self.assertIsNotNone(mission_id, f"a onda c deveria ter comecado: {h.stage_status()}")
        base = h.store.get(mission_id)["workspace"]["baseRef"]
        self.assertTrue(self._has(h.repo, base, "docs/a.md"),
                        f"a base {base!r} nao tem o artefato que o portao confirmou")


class DoneWhenLeafTests(ProgramTestCase):
    """P2: ``doneWhen`` era conferido só na ÚLTIMA onda declarada."""

    def test_leaf_ids_follow_the_graph_not_the_declaration_order(self) -> None:
        document = build_program(program_document(
            self.root / "repo-falso",
            [stage("a"), stage("b", depends=["a"]), stage("c")],
        ))
        self.assertEqual(sorted(_leaf_stage_ids(document)), ["b", "c"])

    def test_done_when_is_satisfied_by_any_leaf_branch(self) -> None:
        # `c` é independente e é a última declarada; o criterio so existe na
        # ponta da outra cadeia. Antes, o programa bloqueava sem motivo.
        h = self.program_harness(
            [stage("a"), stage("b", depends=["a"]), stage("c")],
            doneWhen=delivered("b"),
        )
        h.fakes.scenario(worker=[writes("a"), writes("b"), writes("c")],
                         reviewer=[satisfied(), satisfied(), satisfied()])
        step = h.run()

        self.assertEqual(h.stage_status(), {"a": "completed", "b": "completed", "c": "completed"})
        self.assertEqual(step.status, "completed", f"programa nao concluiu: {step}")

    def test_a_done_when_no_leaf_satisfies_still_blocks(self) -> None:
        """Controle negativo: o OR entre folhas não pode virar 'sempre passa'."""

        h = self.program_harness(
            [stage("a"), stage("b", depends=["a"])],
            doneWhen=[{"id": "G9", "text": "arquivo que ninguem entrega", "kind": "check",
                       "command": "test -f docs/nunca-entregue.md", "cwd": "."}],
        )
        h.fakes.scenario(worker=[writes("a"), writes("b")], reviewer=[satisfied(), satisfied()])
        step = h.run()
        self.assertEqual(step.status, "blocked")
        self.assertEqual(step.reason, "done_when_unsatisfied")


class AtomicStageMissionTests(ProgramTestCase):
    """P2: janela entre ``create``/``activate`` e ``record_stage_mission``."""

    def test_a_mission_left_active_without_its_record_is_recovered(self) -> None:
        # Simula a janela: cria e ativa a missão da onda SEM gravar o vínculo,
        # exatamente o estado que um SIGKILL no meio deixaria.
        h = self.program_harness([stage("a")])
        from pipe_venture_builder.mission.program_supervisor import (
            _build_stage_mission, _resolve_stage_base,
        )

        program = h.store.get_program(h.program_id)
        stage_body = program["stages"][0]
        base = _resolve_stage_base(h.store, program, stage_body)
        document = _build_stage_mission(program, stage_body, base)
        orphan = h.store.create(document, at=utc_now())
        h.store.activate(orphan, at=utc_now())
        self.assertIsNone(h.store.stage_mission(h.program_id, "a"))

        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run()  # não pode explodir com "status transition is not allowed"

        self.assertEqual(h.store.stage_mission(h.program_id, "a"), orphan)

    def test_the_three_steps_commit_together(self) -> None:
        """Se ``record_stage_mission`` falhar, a missão não pode ficar criada:
        ou tudo entra, ou nada entra.

        O gatilho realista é a onda já ter OUTRA missão gravada — o store
        recusa trocar, e o ``create`` que veio antes na mesma transação tem que
        ir embora junto."""

        h = self.program_harness([stage("a")])
        from pipe_venture_builder.mission.program_supervisor import (
            _build_stage_mission, _resolve_stage_base,
        )

        program = h.store.get_program(h.program_id)
        stage_body = program["stages"][0]
        document = _build_stage_mission(
            program, stage_body, _resolve_stage_base(h.store, program, stage_body)
        )
        documento_outro = build_mission(mission_input())
        outra = h.store.create(documento_outro, at=utc_now())
        h.store.record_stage_mission(h.program_id, "a", outra, at=utc_now())
        antes = h.store._connection.execute("SELECT COUNT(*) FROM missions").fetchone()[0]

        with self.assertRaises(ControlPlaneStateError):
            h.store.start_stage_mission(h.program_id, "a", document, at=utc_now())

        self.assertEqual(h.store.stage_mission(h.program_id, "a"), outra)
        self.assertEqual(
            h.store._connection.execute("SELECT COUNT(*) FROM missions").fetchone()[0], antes,
            "a missao ficou gravada apesar do passo seguinte ter falhado",
        )
