"""PIP-833: o vínculo por venture é o que faz a diretriz valer sem alterar código."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.adapters.binding import (
    BINDING_RELATIVE_PATH,
    TOKEN_ENV,
    load_binding,
    read_token,
)
from pipe_venture_builder.errors import PipeError
from tests.helpers import REPOSITORY_ROOT

VALID = {
    "schemaVersion": "0.1.0",
    "workspace": "pipe-venture-builder",
    "team": "Natiivis",
    "project": {"id": "c461563e-99ce-488e-b368-428eeb34c384", "name": "Protocolo"},
    "initiative": None,
}


def venture_with(binding: object | None) -> TemporaryDirectory:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    (root / ".pipe").mkdir()
    if binding is not None:
        payload = binding if isinstance(binding, str) else json.dumps(binding)
        (root / BINDING_RELATIVE_PATH).write_text(payload, encoding="utf-8")
    return tmp


class BindingTests(TestCase):
    def test_a_venture_declares_its_binding_and_the_toolkit_reads_it(self) -> None:
        with venture_with(VALID) as tmp:
            binding = load_binding(Path(tmp), REPOSITORY_ROOT)
        self.assertEqual(binding["project"]["id"], VALID["project"]["id"])

    def test_missing_binding_says_what_to_declare(self) -> None:
        with venture_with(None) as tmp, self.assertRaises(PipeError) as caught:
            load_binding(Path(tmp), REPOSITORY_ROOT)
        self.assertEqual(caught.exception.code, "LINEAR_BINDING_MISSING")
        self.assertIn("workspace, team, and project", caught.exception.message)

    def test_malformed_json_is_a_clean_error(self) -> None:
        with venture_with("{nao é json") as tmp, self.assertRaises(PipeError) as caught:
            load_binding(Path(tmp), REPOSITORY_ROOT)
        self.assertEqual(caught.exception.code, "LINEAR_BINDING_INVALID_JSON")

    def test_binding_without_a_project_is_refused_with_the_field_path(self) -> None:
        broken = {k: v for k, v in VALID.items() if k != "project"}
        with venture_with(broken) as tmp, self.assertRaises(PipeError) as caught:
            load_binding(Path(tmp), REPOSITORY_ROOT)
        self.assertEqual(caught.exception.code, "LINEAR_BINDING_INVALID")
        self.assertTrue(caught.exception.details)

    def test_unknown_keys_are_refused_so_a_typo_is_not_silently_ignored(self) -> None:
        with venture_with({**VALID, "projet": {"id": "x"}}) as tmp:
            with self.assertRaises(PipeError) as caught:
                load_binding(Path(tmp), REPOSITORY_ROOT)
        self.assertEqual(caught.exception.code, "LINEAR_BINDING_INVALID")

    def test_a_credential_shaped_key_cannot_hide_in_the_binding(self) -> None:
        """Segredo em arquivo versionado é o modo mais fácil de vazar credencial."""
        with venture_with({**VALID, "apiKey": "lin_api_x"}) as tmp:
            with self.assertRaises(PipeError) as caught:
                load_binding(Path(tmp), REPOSITORY_ROOT)
        self.assertEqual(caught.exception.code, "LINEAR_BINDING_INVALID")

    def test_this_repository_ships_a_valid_binding(self) -> None:
        """O Pipe é consumidor do próprio manual: se o exemplo canônico não valida,
        nenhuma venture tem de onde copiar."""
        binding = load_binding(REPOSITORY_ROOT, REPOSITORY_ROOT)
        self.assertEqual(binding["workspace"], "pipe-venture-builder")


class TokenTests(TestCase):
    def test_token_comes_from_the_environment_not_from_the_binding(self) -> None:
        self.assertEqual(read_token({TOKEN_ENV: " chave "}), "chave")

    def test_missing_token_points_at_the_approved_vault_flow(self) -> None:
        with self.assertRaises(PipeError) as caught:
            read_token({})
        self.assertEqual(caught.exception.code, "LINEAR_TOKEN_MISSING")
        self.assertIn("vw get item", caught.exception.message)
        self.assertIn("gate absoluto", caught.exception.message)

    def test_blank_token_is_treated_as_missing(self) -> None:
        with self.assertRaises(PipeError):
            read_token({TOKEN_ENV: "   "})
