from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.adapters.hermes.probe import probe_hermes


class HermesProbeTests(TestCase):
    def test_missing_runtime_is_a_controlled_blocker(self) -> None:
        result = probe_hermes("definitely-not-a-hermes-runtime")
        self.assertFalse(result["available"])
        self.assertEqual(result["reason"], "runtime_unavailable")

    def test_old_runtime_is_detected_without_shell(self) -> None:
        with TemporaryDirectory() as directory:
            executable = Path(directory) / "hermes-old"
            executable.write_text(
                "#!/bin/sh\nprintf '%s\\n' 'Hermes Agent v0.16.9'\n",
                encoding="utf-8",
            )
            os.chmod(executable, 0o700)
            result = probe_hermes(str(executable))

        self.assertTrue(result["available"])
        self.assertFalse(result["compatible"])
        self.assertEqual(result["reason"], "runtime_version_unsupported")
