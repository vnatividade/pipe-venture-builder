"""Migração do banco: a FK de ``decisions`` some para o sujeito poder ser um
programa.

Todo teste do repositório nasce com banco novo, então o modo de falha que
importa — banco **já existente**, criado antes de existir programa — é
inalcançável sem montar o esquema antigo à mão. É o que estes testes fazem.
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipe_venture_builder.control_plane.model import ControlPlaneStateError
from pipe_venture_builder.mission.program import build_program
from pipe_venture_builder.mission.store import DATABASE_SCHEMA_VERSION, MissionStore

from tests.mission.loop_helpers import make_repo

# O DDL exato de antes do PIP-910, com a FK que impede sujeito `PRG-`.
DECISIONS_V1 = """
CREATE TABLE decisions(
    decision_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL REFERENCES missions(mission_id),
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    context_json TEXT NOT NULL,
    options_json TEXT NOT NULL,
    safe_default TEXT NOT NULL,
    blocked_scope TEXT NOT NULL,
    deadline TEXT,
    opened_at TEXT NOT NULL,
    decided_by TEXT,
    decided_option TEXT,
    decided_at TEXT
);
"""

MISSIONS_V1 = """
CREATE TABLE missions(
    mission_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    status TEXT NOT NULL,
    document_json TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

# O DDL exato de ``mission_runs`` na versao 2 (PIP-910, antes do PIP-911):
# sem ``executor_kind``/``model`` — só o ``executor`` livre ``"<role>:<model>"``.
MISSION_RUNS_V2 = """
CREATE TABLE mission_runs(
    run_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL REFERENCES missions(mission_id),
    attempt INTEGER NOT NULL,
    cycle INTEGER NOT NULL,
    executor TEXT NOT NULL,
    session_id TEXT,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    cost_usd REAL NOT NULL DEFAULT 0,
    num_turns INTEGER NOT NULL DEFAULT 0,
    result_ref TEXT,
    result_fingerprint TEXT,
    verdict TEXT
);
"""


class MigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="migracao-"))
        self.path = self.root / "mission.sqlite3"

    def _build_v1(self, *, decisions: int = 1) -> None:
        connection = sqlite3.connect(self.path)
        connection.executescript(
            MISSIONS_V1
            + DECISIONS_V1
            + """
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO metadata(key, value) VALUES ('schema_version', '1');
            INSERT INTO missions VALUES
                ('MSN-antiga', 1, 'completed', '{}', 'sha256:x', 'ontem', 'ontem');
            """
        )
        for index in range(decisions):
            connection.execute(
                "INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (f"DEC-{index}", "MSN-antiga", "escalation", "pending", "{}", "[]",
                 "stop", "mission", None, "ontem", None, None, None),
            )
        connection.commit()
        connection.close()

    def _ddl(self, store: MissionStore, table: str) -> str:
        row = store._connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = ?", (table,)
        ).fetchone()
        return row["sql"]

    def test_an_existing_database_loses_the_foreign_key_and_keeps_every_row(self) -> None:
        self._build_v1(decisions=3)
        store = MissionStore(self.path)
        self.addCleanup(store.close)

        version = store._connection.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()["value"]
        self.assertEqual(version, str(DATABASE_SCHEMA_VERSION))
        self.assertNotIn("REFERENCES missions", self._ddl(store, "decisions"))
        self.assertEqual(
            store._connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0], 3
        )
        self.assertEqual(
            store._connection.execute("SELECT COUNT(*) FROM missions").fetchone()[0], 1
        )
        self.assertEqual(
            store._connection.execute("PRAGMA integrity_check").fetchone()[0], "ok"
        )
        self.assertEqual(store._connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_a_program_decision_works_on_a_migrated_database(self) -> None:
        """O defeito concreto: sem a migração isto estoura ``IntegrityError``,
        porque o sujeito da decisão é um `PRG-` que não existe em ``missions``.
        Este é o caminho que TODO portão do programa usa — portão humano,
        `startWhen` insatisfeito, teto de orçamento e `doneWhen`."""

        from tests.mission.test_program import program_document, stage

        self._build_v1()
        store = MissionStore(self.path)
        self.addCleanup(store.close)
        repo = make_repo(self.root)
        document = build_program(program_document(repo, [stage("a")]))
        program_id = store.create_program(document)
        store.activate_program(program_id)

        store.open_decision(
            program_id, kind="approval", context={"reason": "requires_founder", "stage": "a"},
            options=["approve", "stop"], safe_default="stop", blocked_scope="stage",
            deadline=None, at="2026-09-12T00:00:00Z",
        )
        pending = store.list_decisions(program_id, pending_only=True)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["missionId"], program_id)

    def test_the_foreign_key_is_actually_on_so_the_test_above_is_not_vacuous(self) -> None:
        """Controle: com a FK antiga e ``foreign_keys=ON``, o INSERT falha
        mesmo. Se este teste parar de falhar, o de cima deixa de provar algo."""

        self._build_v1()
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("DEC-prg", "PRG-a0f82c285b92", "escalation", "pending", "{}",
                 "[]", "stop", "program", None, "ontem", None, None, None),
            )
        connection.close()

    def test_migrating_twice_is_a_no_op(self) -> None:
        self._build_v1(decisions=2)
        first = MissionStore(self.path)
        first.close()
        second = MissionStore(self.path)
        self.addCleanup(second.close)
        self.assertEqual(
            second._connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0], 2
        )
        self.assertNotIn("REFERENCES missions", self._ddl(second, "decisions"))

    def test_an_unknown_future_version_is_refused_instead_of_guessed(self) -> None:
        self._build_v1()
        connection = sqlite3.connect(self.path)
        connection.execute("UPDATE metadata SET value = '99' WHERE key = 'schema_version'")
        connection.commit()
        connection.close()
        with self.assertRaises(ControlPlaneStateError):
            MissionStore(self.path)


class RunExecutorKindMigrationTests(unittest.TestCase):
    """PIP-911: ``mission_runs`` gains ``executor_kind``/``model`` without
    losing a row — the same "montar o esquema antigo à mão" posture as
    ``MigrationTests`` above, but for a version-2 database (the one every
    mission created before this ticket actually has)."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="migracao-911-"))
        self.path = self.root / "mission.sqlite3"

    def _build_v2(self, *, runs: list[tuple[str, str]]) -> None:
        connection = sqlite3.connect(self.path)
        connection.executescript(
            MISSIONS_V1
            + MISSION_RUNS_V2
            + """
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO metadata(key, value) VALUES ('schema_version', '2');
            INSERT INTO missions VALUES
                ('MSN-antiga', 1, 'completed', '{}', 'sha256:x', 'ontem', 'ontem');
            """
        )
        for index, (run_id, executor) in enumerate(runs):
            connection.execute(
                "INSERT INTO mission_runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (run_id, "MSN-antiga", 1, index + 1, executor, None, "collected",
                 "ontem", "ontem", 1.5, 3, None, None, "satisfied"),
            )
        connection.commit()
        connection.close()

    def test_an_existing_database_gains_the_columns_and_keeps_every_row(self) -> None:
        self._build_v2(runs=[("MRUN-aaaaaaaaaaaa", "worker:sonnet"), ("MRUN-bbbbbbbbbbbb", "reviewer:opus")])
        store = MissionStore(self.path)
        self.addCleanup(store.close)

        version = store._connection.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()["value"]
        self.assertEqual(version, str(DATABASE_SCHEMA_VERSION))
        columns = {
            row[1]
            for row in store._connection.execute("PRAGMA table_info(mission_runs)").fetchall()
        }
        self.assertIn("executor_kind", columns)
        self.assertIn("model", columns)
        self.assertEqual(
            store._connection.execute("SELECT COUNT(*) FROM mission_runs").fetchone()[0], 2
        )
        self.assertEqual(
            store._connection.execute("PRAGMA integrity_check").fetchone()[0], "ok"
        )

    def test_every_pre_existing_run_backfills_as_claude_with_its_model(self) -> None:
        """Every run before this migration ran on Claude — the only executor
        that ever existed — so the backfill records what actually happened,
        not a guess; the model is recovered from the old ``executor`` text."""

        self._build_v2(runs=[("MRUN-aaaaaaaaaaaa", "worker:sonnet"), ("MRUN-bbbbbbbbbbbb", "reviewer:opus")])
        store = MissionStore(self.path)
        self.addCleanup(store.close)
        worker_run = store.get_run("MRUN-aaaaaaaaaaaa")
        reviewer_run = store.get_run("MRUN-bbbbbbbbbbbb")
        self.assertEqual(worker_run["executor_kind"], "claude")
        self.assertEqual(worker_run["model"], "sonnet")
        self.assertEqual(reviewer_run["executor_kind"], "claude")
        self.assertEqual(reviewer_run["model"], "opus")

    def test_a_run_without_a_model_suffix_backfills_a_null_model(self) -> None:
        self._build_v2(runs=[("MRUN-aaaaaaaaaaaa", "claude-code")])
        store = MissionStore(self.path)
        self.addCleanup(store.close)
        run = store.get_run("MRUN-aaaaaaaaaaaa")
        self.assertEqual(run["executor_kind"], "claude")
        self.assertIsNone(run["model"])

    def test_migrating_twice_is_a_no_op(self) -> None:
        self._build_v2(runs=[("MRUN-aaaaaaaaaaaa", "worker:sonnet")])
        first = MissionStore(self.path)
        first.close()
        second = MissionStore(self.path)
        self.addCleanup(second.close)
        self.assertEqual(second.get_run("MRUN-aaaaaaaaaaaa")["model"], "sonnet")
        self.assertEqual(
            second._connection.execute("SELECT COUNT(*) FROM mission_runs").fetchone()[0], 1
        )

    def test_a_version_one_database_with_real_runs_gets_both_migrations(self) -> None:
        """Um v1 REALISTA: com `mission_runs` populada, que é o que existe num
        banco de verdade da época do PIP-901/902.

        A fixture v1 abaixo não cria `mission_runs`, então o
        ``CREATE TABLE IF NOT EXISTS`` do `_initialize` já traz as colunas
        novas e a migração cai no ramo "colunas já existem" — o caminho OPOSTO
        ao de um banco real. Sem este teste, o `ALTER TABLE` de verdade nunca é
        exercitado a partir da versão 1.
        """

        connection = sqlite3.connect(self.path)
        connection.executescript(
            MISSIONS_V1
            + DECISIONS_V1
            + """
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO metadata(key, value) VALUES ('schema_version', '1');
            CREATE TABLE mission_runs(
                run_id TEXT PRIMARY KEY, mission_id TEXT NOT NULL, attempt INTEGER NOT NULL,
                cycle INTEGER NOT NULL, executor TEXT NOT NULL, session_id TEXT,
                status TEXT NOT NULL, started_at TEXT NOT NULL, ended_at TEXT,
                cost_usd REAL NOT NULL DEFAULT 0, num_turns INTEGER NOT NULL DEFAULT 0,
                result_ref TEXT, result_fingerprint TEXT, verdict TEXT);
            INSERT INTO missions VALUES
                ('MSN-antiga', 1, 'completed', '{}', 'sha256:x', 'ontem', 'ontem');
            INSERT INTO mission_runs(run_id, mission_id, attempt, cycle, executor, status, started_at)
                VALUES ('MRUN-aaaaaaaaaaaa', 'MSN-antiga', 1, 1, 'worker:sonnet', 'collected', 'ontem'),
                       ('MRUN-bbbbbbbbbbbb', 'MSN-antiga', 1, 1, 'reviewer:opus', 'collected', 'ontem');
            """
        )
        connection.commit()
        connection.close()

        store = MissionStore(self.path)
        self.addCleanup(store.close)
        linhas = store._connection.execute(
            "SELECT run_id, executor_kind, model FROM mission_runs ORDER BY run_id"
        ).fetchall()
        self.assertEqual(len(linhas), 2, "run perdido na migração 1→3")
        self.assertEqual([r["executor_kind"] for r in linhas], ["claude", "claude"])
        self.assertEqual([r["model"] for r in linhas], ["sonnet", "opus"])
        self.assertNotIn(
            "REFERENCES missions",
            store._connection.execute(
                "SELECT sql FROM sqlite_master WHERE name = 'decisions'"
            ).fetchone()["sql"],
        )
        self.assertEqual(
            store._connection.execute("PRAGMA integrity_check").fetchone()[0], "ok"
        )
        self.assertEqual(store._connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_a_version_one_database_gets_both_migrations_and_keeps_its_rows(self) -> None:
        """A database old enough to still need the 1→2 decisions fix also
        needs 2→3: both run in sequence, from a bare version-1 schema (no
        ``mission_runs`` table at all yet, as in ``MigrationTests``)."""

        connection = sqlite3.connect(self.path)
        connection.executescript(
            MISSIONS_V1
            + DECISIONS_V1
            + """
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO metadata(key, value) VALUES ('schema_version', '1');
            INSERT INTO missions VALUES
                ('MSN-antiga', 1, 'completed', '{}', 'sha256:x', 'ontem', 'ontem');
            """
        )
        connection.execute(
            "INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("DEC-0", "MSN-antiga", "escalation", "pending", "{}", "[]",
             "stop", "mission", None, "ontem", None, None, None),
        )
        connection.commit()
        connection.close()

        store = MissionStore(self.path)
        self.addCleanup(store.close)
        version = store._connection.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()["value"]
        self.assertEqual(version, str(DATABASE_SCHEMA_VERSION))
        self.assertEqual(
            store._connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0], 1
        )
        columns = {
            row[1]
            for row in store._connection.execute("PRAGMA table_info(mission_runs)").fetchall()
        }
        self.assertIn("executor_kind", columns)
        self.assertIn("model", columns)


if __name__ == "__main__":
    unittest.main()
