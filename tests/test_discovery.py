from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.discovery import discover_project_root, is_pipe_root
from pipe_venture_builder.errors import PipeError

from .helpers import make_pipe_root


class ProjectRootDiscoveryTests(TestCase):
    def test_discovers_root_from_nested_path_with_spaces(self) -> None:
        with TemporaryDirectory(prefix="pipe root with spaces ") as temporary:
            root = make_pipe_root(Path(temporary) / "example product")
            nested = root / "src" / "feature"
            nested.mkdir(parents=True)

            self.assertEqual(discover_project_root(nested), root.resolve())
            self.assertTrue(is_pipe_root(root))

    def test_rejects_directory_without_pipe_markers(self) -> None:
        with TemporaryDirectory() as temporary:
            with self.assertRaises(PipeError) as captured:
                discover_project_root(temporary)

        self.assertEqual(captured.exception.code, "PROJECT_ROOT_NOT_FOUND")
        self.assertNotIn(temporary, captured.exception.message)

    def test_accepts_file_as_search_start(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_pipe_root(Path(temporary))
            source = root / "notes.md"
            source.write_text("safe fixture", encoding="utf-8")

            self.assertEqual(discover_project_root(source), root.resolve())
