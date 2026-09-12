"""``pipe program`` pela linha de comando.

A revisão adversarial encontrou a superfície inteira sem teste: `create`,
`show`, `status`, `activate`, `pause`, `resume`, `cancel`, `decisions`. Funciona
— foi conferido à mão —, mas nada disso estava protegido contra regressão, e é
por onde o fundador entra.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.exit_codes import SUCCESS, USAGE_ERROR
from tests.mission.helpers import write_json
from tests.mission.loop_helpers import git, make_repo
from tests.mission.test_cli import run_cli
from tests.mission.test_program import program_document, stage


class ProgramCliTests(TestCase):
    def _setup(self, root: Path, stages=None, **overrides):
        repo = make_repo(root)
        (repo / "docs").mkdir(exist_ok=True)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "docs", "--allow-empty")
        document = program_document(repo, stages or [stage("a")], **overrides)
        source = write_json(root / "program.json", document)
        store = root / "mission.sqlite3"
        return repo, source, store

    def test_create_show_and_lifecycle_round_trip(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, source, store = self._setup(root, [stage("a"), stage("b", depends=["a"])])

            code, out, err = run_cli("program", "create", str(source), "--store", str(store), "--json")
            self.assertEqual(code, SUCCESS, err)
            program_id = json.loads(out)["programId"]
            self.assertTrue(program_id.startswith("PRG-"), program_id)

            code, out, err = run_cli("program", "show", program_id, "--store", str(store), "--json")
            self.assertEqual(code, SUCCESS, err)
            shown = json.loads(out)
            document = shown.get("program", shown)
            self.assertEqual([s["id"] for s in document["stages"]], ["a", "b"])

            for verb, expected in (
                ("activate", "active"), ("pause", "paused"),
                ("resume", "active"), ("cancel", "cancelled"),
            ):
                code, out, err = run_cli("program", verb, program_id, "--store", str(store), "--json")
                self.assertEqual(code, SUCCESS, f"{verb}: {err}")
                payload = json.loads(out)
                self.assertEqual(payload.get("status"), expected, f"{verb}: {payload}")

    def test_status_answers_the_three_questions_in_plain_text(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, source, store = self._setup(root)
            code, out, _ = run_cli("program", "create", str(source), "--store", str(store), "--json")
            program_id = json.loads(out)["programId"]
            run_cli("program", "activate", program_id, "--store", str(store), "--json")

            code, out, err = run_cli("program", "status", program_id, "--store", str(store))
            self.assertEqual(code, SUCCESS, err)
            # As três perguntas, na forma que o `program status` usa: onde
            # cada onda está, o custo com a cadeia de auditoria, e o que
            # depende do fundador.
            self.assertIn(program_id, out)
            self.assertIn("active", out)
            self.assertIn("custo US$", out)
            self.assertIn("cadeia de auditoria válida: true", out)
            self.assertIn("- a: pending", out)
            self.assertIn("depende de você", out)

    def test_status_json_carries_stages_cost_and_pending_decisions(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, source, store = self._setup(root, [stage("a"), stage("b", depends=["a"])])
            code, out, _ = run_cli("program", "create", str(source), "--store", str(store), "--json")
            program_id = json.loads(out)["programId"]
            run_cli("program", "activate", program_id, "--store", str(store), "--json")

            code, out, err = run_cli("program", "status", program_id, "--store", str(store), "--json")
            self.assertEqual(code, SUCCESS, err)
            # Mesma forma do `mission status --json`: o objeto inteiro vai em
            # `status`, para que dê para automatizar em cima disso.
            payload = json.loads(out)["status"]
            self.assertEqual([s["id"] for s in payload["stages"]], ["a", "b"])
            self.assertIn("costUsd", payload)
            self.assertIn("pendingDecisions", payload)
            self.assertTrue(payload["auditChainValid"])

    def test_decisions_lists_nothing_pending_on_a_fresh_program(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, source, store = self._setup(root)
            code, out, _ = run_cli("program", "create", str(source), "--store", str(store), "--json")
            program_id = json.loads(out)["programId"]
            code, out, err = run_cli(
                "program", "decisions", program_id, "--store", str(store), "--pending", "--json"
            )
            self.assertEqual(code, SUCCESS, err)
            payload = json.loads(out)
            self.assertEqual(payload.get("decisions", payload.get("pendingDecisions")), [])

    def test_an_unknown_program_id_is_an_error_not_a_traceback(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = Path(root) / "mission.sqlite3"
            code, _, err = run_cli("program", "show", "PRG-000000000000", "--store", str(store), "--json")
            self.assertNotEqual(code, SUCCESS)
            self.assertNotIn("Traceback", err)

    def test_a_malformed_program_id_is_refused_before_touching_the_store(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = Path(root) / "mission.sqlite3"
            # Travessia de caminho no id não pode chegar ao disco.
            code, _, err = run_cli(
                "program", "status", "../../etc/passwd", "--store", str(store), "--json"
            )
            self.assertNotEqual(code, SUCCESS)
            self.assertNotIn("Traceback", err)

    def test_activating_a_cancelled_program_is_refused(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, source, store = self._setup(root)
            code, out, _ = run_cli("program", "create", str(source), "--store", str(store), "--json")
            program_id = json.loads(out)["programId"]
            run_cli("program", "activate", program_id, "--store", str(store), "--json")
            run_cli("program", "cancel", program_id, "--store", str(store), "--json")
            code, _, err = run_cli("program", "activate", program_id, "--store", str(store), "--json")
            self.assertNotEqual(code, SUCCESS, "cancelado nao pode voltar a ativo")
            self.assertNotIn("Traceback", err)

    def test_create_refuses_an_invalid_program_document(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            quebrado = program_document(repo, [stage("a")])
            quebrado["stages"][0]["dependsOn"] = ["nao-existe"]
            source = write_json(root / "quebrado.json", quebrado)
            store = root / "mission.sqlite3"
            code, _, err = run_cli("program", "create", str(source), "--store", str(store), "--json")
            self.assertNotEqual(code, SUCCESS)
            self.assertNotIn("Traceback", err)

    def test_program_help_lists_every_verb(self) -> None:
        # argparse encerra o processo no `--help`; o que interessa é o texto.
        with self.assertRaises(SystemExit):
            run_cli("program", "--help")

        import argparse
        import contextlib
        import io

        from pipe_venture_builder.cli import main

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.suppress(SystemExit):
            main(["program", "--help"], stdout=buffer, stderr=buffer)
        text = buffer.getvalue()
        for verb in ("create", "show", "status", "activate", "pause",
                     "resume", "cancel", "decisions", "supervise"):
            self.assertIn(verb, text, f"verbo {verb} sumiu do --help")
