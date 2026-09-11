from __future__ import annotations

import ast
from pathlib import Path
from types import MappingProxyType
from typing import Any
from unittest import TestCase

import pipe_venture_builder.adapters.deepseek_harness as deepseek_harness
from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessContractError,
    validate_preflight,
)
from tests.deepseek_harness.helpers import (
    SECRET_SENTINEL,
    TEXT_SENTINEL,
    assert_blocked,
    forbid_host_access,
)


VALID_CONFIG = MappingProxyType(
    {
        "inheritEnvironment": False,
        "credentialDiscovery": False,
        "pluginDiscovery": False,
        "telemetry": False,
        "hotReload": False,
        "network": False,
    }
)
FLAG_CODES = {
    "inheritEnvironment": "preflight_environment_inherited",
    "credentialDiscovery": "preflight_credential_discovery",
    "pluginDiscovery": "preflight_plugin_discovery",
    "telemetry": "preflight_telemetry",
    "hotReload": "preflight_hot_reload",
    "network": "preflight_network",
}
PACKAGE_NAME = "pipe_venture_builder.adapters.deepseek_harness"
FORBIDDEN_MODULES = (
    "asyncio",
    "http",
    "logging",
    "multiprocessing",
    "pipe_venture_builder.adapters.hermes",
    "pipe_venture_builder.apply",
    "requests",
    "socket",
    "ssl",
    "subprocess",
    "urllib",
)
FORBIDDEN_NAMES = frozenset(
    {
        "__import__",
        "environ",
        "environb",
        "execl",
        "execle",
        "execlp",
        "execlpe",
        "execv",
        "execve",
        "execvp",
        "execvpe",
        "expanduser",
        "expandvars",
        "fork",
        "forkpty",
        "getenv",
        "getenvb",
        "home",
        "import_module",
        "popen",
        "posix_spawn",
        "posix_spawnp",
        "putenv",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "startfile",
        "system",
        "unsetenv",
    }
)


class FakeSessionFactory:
    """Synthetic stand-in for session creation; it never starts anything."""

    def __init__(self) -> None:
        self.calls = 0
        self.session = object()

    def __call__(self) -> object:
        self.calls += 1
        return self.session


def config(**changes: Any) -> dict[Any, Any]:
    return {**VALID_CONFIG, **changes}


class PreflightTests(TestCase):
    """ADR-004 BDD 5 / D8: synthetic preflight fails closed before any session."""

    def assert_refused(self, code: str, value: Any) -> None:
        factory = FakeSessionFactory()
        with forbid_host_access() as log:
            assert_blocked(self, code, validate_preflight, value, start_session=factory)
        self.assertEqual(factory.calls, 0)
        self.assertEqual(log, [])

    def test_strictly_false_flags_start_the_fake_session_once(self) -> None:
        for value in (VALID_CONFIG, dict(VALID_CONFIG)):
            with self.subTest(mapping=type(value).__name__):
                factory = FakeSessionFactory()
                with forbid_host_access() as log:
                    result = validate_preflight(value, start_session=factory)
                self.assertIs(result, factory.session)
                self.assertEqual(factory.calls, 1)
                self.assertEqual(log, [])

    def test_each_enabled_flag_blocks_with_stable_code_before_session(self) -> None:
        for flag, code in FLAG_CODES.items():
            with self.subTest(flag=flag):
                self.assert_refused(code, config(**{flag: True}))

    def test_several_enabled_flags_still_block_before_session(self) -> None:
        factory = FakeSessionFactory()
        with forbid_host_access() as log:
            with self.assertRaises(DeepSeekHarnessContractError) as caught:
                validate_preflight(
                    config(telemetry=True, network=True, hotReload=True),
                    start_session=factory,
                )
        self.assertIn(
            caught.exception.code,
            {FLAG_CODES["telemetry"], FLAG_CODES["network"], FLAG_CODES["hotReload"]},
        )
        self.assertEqual(factory.calls, 0)
        self.assertEqual(log, [])

    def test_flag_values_must_be_real_booleans(self) -> None:
        for flag in FLAG_CODES:
            for value in (0, 1, 0.0, None, "false", "False", "", [], {}, TEXT_SENTINEL):
                with self.subTest(flag=flag, value=value):
                    self.assert_refused("preflight_config_invalid", config(**{flag: value}))

    def test_unknown_keys_are_refused_without_echo(self) -> None:
        for extra in (
            {"sandbox": False},
            {"inheritEnv": False},
            {"environment": {"PATH": "/usr/bin"}},
            {"telemetryEndpoint": "https://collector.invalid"},
            {SECRET_SENTINEL: False},
            {TEXT_SENTINEL: TEXT_SENTINEL},
            {1: False},
        ):
            with self.subTest(extra=list(extra)):
                self.assert_refused("preflight_config_invalid", {**VALID_CONFIG, **extra})

    def test_missing_keys_are_refused(self) -> None:
        for flag in FLAG_CODES:
            with self.subTest(missing=flag):
                incomplete = dict(VALID_CONFIG)
                del incomplete[flag]
                self.assert_refused("preflight_config_invalid", incomplete)
        self.assert_refused("preflight_config_invalid", {})

    def test_non_mapping_config_is_refused(self) -> None:
        for value in (
            None,
            [],
            list(VALID_CONFIG.items()),
            "inheritEnvironment=false",
            b"{}",
            False,
        ):
            with self.subTest(value=type(value).__name__):
                self.assert_refused("preflight_config_invalid", value)

    def test_shape_errors_take_precedence_over_enabled_flags(self) -> None:
        self.assert_refused(
            "preflight_config_invalid", config(telemetry=True, unexpected=False)
        )
        self.assert_refused("preflight_config_invalid", config(network=True, hotReload=1))

    def test_config_is_not_mutated(self) -> None:
        value = config(telemetry=True)
        snapshot = dict(value)
        self.assert_refused(FLAG_CODES["telemetry"], value)
        self.assertEqual(value, snapshot)


class HostBoundaryTests(TestCase):
    """Static guard: the package cannot reach env, processes, network or apply."""

    def test_package_source_has_no_host_process_or_network_access(self) -> None:
        package_root = Path(deepseek_harness.__file__).resolve().parent
        sources = sorted(package_root.rglob("*.py"))
        self.assertTrue(sources)
        findings: list[str] = []
        for source in sources:
            relative = source.relative_to(package_root)
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(relative))
            package_parts = PACKAGE_NAME.split(".") + list(relative.parent.parts)
            for node in ast.walk(tree):
                for module in imported_modules(node, package_parts):
                    if is_forbidden_module(module):
                        findings.append(f"{relative}:{node.lineno}: import {module}")
                name = referenced_name(node)
                if name in FORBIDDEN_NAMES:
                    findings.append(f"{relative}:{getattr(node, 'lineno', 0)}: {name}")
        self.assertEqual(findings, [])


def imported_modules(node: ast.AST, package_parts: list[str]) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if node.level:
            anchor = package_parts[: len(package_parts) - (node.level - 1)]
            base = ".".join(anchor + ([node.module] if node.module else []))
        else:
            base = node.module or ""
        return [base] + [f"{base}.{alias.name}" for alias in node.names]
    return []


def is_forbidden_module(module: str) -> bool:
    return any(
        module == forbidden or module.startswith(f"{forbidden}.")
        for forbidden in FORBIDDEN_MODULES
    )


def referenced_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.alias):
        return node.name.rsplit(".", 1)[-1]
    return None
