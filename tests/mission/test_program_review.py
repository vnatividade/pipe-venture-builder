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


class Pip911Onda1ReviewTests(ProgramTestCase):
    """PIP-911 onda 1, revisão adversarial: as guardas novas que a suíte
    entregue não exercitava (provado por mutação, com a suíte ficando verde).
    """

    def _store(self):
        from pipe_venture_builder.mission.store import MissionStore

        store = MissionStore(self.root / "guardas.sqlite3")
        self.addCleanup(store.close)
        return store

    def _mission(self, store) -> str:
        from pipe_venture_builder.mission.contract import build_mission

        from tests.mission.helpers import mission_input

        mission_id = store.create(build_mission(mission_input()), at=utc_now())
        store.activate(mission_id, at=utc_now())
        return mission_id

    def test_an_unknown_executor_kind_is_refused_when_a_run_opens(self) -> None:
        from pipe_venture_builder.control_plane.model import ControlPlaneContractError

        store = self._store()
        mission_id = self._mission(store)
        with self.assertRaises(ControlPlaneContractError):
            store.open_run(mission_id, attempt=1, cycle=1, executor="worker:sonnet",
                           executor_kind="ollama", model="sonnet", at=utc_now())

    def test_a_model_with_an_unsafe_shape_is_refused_when_a_run_opens(self) -> None:
        from pipe_venture_builder.control_plane.model import ControlPlaneContractError

        store = self._store()
        mission_id = self._mission(store)
        for hostile in ("../../etc/passwd", "sonnet; rm -rf /", "modelo com espaco"):
            with self.subTest(model=hostile):
                with self.assertRaises(ControlPlaneContractError):
                    store.open_run(mission_id, attempt=1, cycle=1, executor="worker:sonnet",
                                   executor_kind="claude", model=hostile, at=utc_now())

    def test_a_well_formed_run_is_accepted(self) -> None:
        """Controle positivo: as guardas acima recusam algo, não tudo."""

        store = self._store()
        mission_id = self._mission(store)
        run_id = store.open_run(mission_id, attempt=1, cycle=1, executor="worker:sonnet",
                                executor_kind="claude", model="sonnet", at=utc_now())
        row = store._connection.execute(
            "SELECT executor_kind, model FROM mission_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        self.assertEqual((row["executor_kind"], row["model"]), ("claude", "sonnet"))

    def test_reviewer_and_responder_runs_never_declare_a_non_claude_executor(self) -> None:
        """A política de rubric usa como RAZÃO que o revisor e o respondedor
        rodam sempre no modelo forte — nenhum dos dois tem um campo de
        executor próprio (``program._validate_execution``). Isso precisa ser
        uma invariante do arquivo, não uma convenção: bastaria trocar
        ``EXECUTOR_KIND_CLAUDE`` por uma variável num desses dois `open_run`
        para a política perder o chão, sem derrubar nenhum outro teste.

        O `open_run` do WORKER (`_dispatch`) fica de fora desta invariante a
        partir da onda 2 do PIP-911: é exatamente o ponto que passou a variar
        entre ``claude`` e ``local`` (`_resolve_dispatch_executor`) — por
        isso o teste ainda confirma que ele existe e que sua origem é essa
        função, mas não mais que é um literal fixo.
        """

        import ast

        fonte = Path("src/pipe_venture_builder/mission/supervisor.py").read_text(encoding="utf-8")
        arvore = ast.parse(fonte)
        por_metodo: dict[str, list] = {}
        for no in ast.walk(arvore):
            if not isinstance(no, ast.FunctionDef):
                continue
            for interno in ast.walk(no):
                if not isinstance(interno, ast.Call):
                    continue
                alvo = interno.func
                if not (isinstance(alvo, ast.Attribute) and alvo.attr == "open_run"):
                    continue
                kwargs = {k.arg: k.value for k in interno.keywords if k.arg}
                por_metodo.setdefault(no.name, []).append(kwargs.get("executor_kind"))

        for metodo in ("_review", "_answer_blockers"):
            valores = por_metodo.get(metodo, [])
            self.assertEqual(len(valores), 1, f"esperava exatamente um open_run em {metodo}")
            valor = valores[0]
            self.assertIsNotNone(valor, f"{metodo} omitiu executor_kind")
            self.assertIsInstance(valor, ast.Name)
            self.assertEqual(
                valor.id, "EXECUTOR_KIND_CLAUDE",
                f"{metodo} pode abrir fora do modelo forte; "
                "a política de rubric perde a razão de ser",
            )

        dispatch = por_metodo.get("_dispatch", [])
        self.assertEqual(len(dispatch), 1, "esperava um open_run em _dispatch")
        valor_dispatch = dispatch[0]
        self.assertIsNotNone(valor_dispatch, "_dispatch omitiu executor_kind")
        self.assertIsInstance(valor_dispatch, ast.Name)
        self.assertEqual(
            valor_dispatch.id, "executor_kind",
            "_dispatch deve abrir o worker com o resultado de "
            "_resolve_dispatch_executor, não um valor hardcoded",
        )

    def test_a_declared_executor_the_dispatch_ignores_is_recorded_as_divergence(self) -> None:
        """P2 da revisão: declarar `executor: local` na onda 1 rodava no Claude
        pago em silêncio absoluto — nada em evento, log ou status. Agora a
        divergência entra na cadeia de auditoria."""

        h = self.program_harness([stage("a", execution={"executor": "local"})])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run()

        eventos = h.store.list_program_events(h.program_id)
        gravados = [e for e in eventos
                    if e["eventType"] == "program.stage_mission_recorded"]
        self.assertEqual(len(gravados), 1)
        payload = gravados[0]["payload"]
        self.assertEqual(payload.get("executorDeclared"), "local")
        self.assertEqual(payload.get("executorUsed"), "claude")

    def test_a_wave_without_a_declared_executor_records_no_divergence(self) -> None:
        """Controle: o campo só aparece quando há divergência de verdade."""

        h = self.program_harness([stage("a")])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run()
        gravados = [e for e in h.store.list_program_events(h.program_id)
                    if e["eventType"] == "program.stage_mission_recorded"]
        self.assertNotIn("executorDeclared", gravados[0]["payload"])
