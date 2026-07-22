from unittest import TestCase

from src.widget import render_widget


class WidgetTests(TestCase):
    def test_renders_widget(self) -> None:
        self.assertEqual(render_widget(), "widget")
