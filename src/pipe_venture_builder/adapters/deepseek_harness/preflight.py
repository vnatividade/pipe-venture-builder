"""Synthetic preflight that fails closed before any session (ADR-004 D8, BDD 5).

The preflight only inspects the synthetic configuration it is given. It never
reads the host environment, credential files, plugin directories, or network
state, and it never starts a process. Every flag must be present and exactly
``False``; unknown keys or non-boolean values are refused before any flag.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable, TypeVar

from .errors import DeepSeekHarnessContractError


_Session = TypeVar("_Session")

PREFLIGHT_FLAG_CODES = (
    ("inheritEnvironment", "preflight_environment_inherited"),
    ("credentialDiscovery", "preflight_credential_discovery"),
    ("pluginDiscovery", "preflight_plugin_discovery"),
    ("telemetry", "preflight_telemetry"),
    ("hotReload", "preflight_hot_reload"),
    ("network", "preflight_network"),
)
PREFLIGHT_FLAGS = frozenset(flag for flag, _ in PREFLIGHT_FLAG_CODES)


def validate_preflight(
    config: Any, *, start_session: Callable[[], _Session]
) -> _Session:
    """Validate the synthetic config, then call ``start_session`` exactly once."""

    if not callable(start_session):
        raise DeepSeekHarnessContractError("preflight_config_invalid") from None
    flags = _snapshot(config)
    for flag, code in PREFLIGHT_FLAG_CODES:
        if flags[flag] is not False:
            raise DeepSeekHarnessContractError(code) from None
    return start_session()


def _snapshot(config: Any) -> dict[str, bool]:
    """Copy the config once so a mapping cannot change between checks."""

    if not isinstance(config, Mapping):
        raise DeepSeekHarnessContractError("preflight_config_invalid") from None
    try:
        items = [(key, config[key]) for key in config]
    except Exception:
        raise DeepSeekHarnessContractError("preflight_config_invalid") from None
    if len(items) != len(PREFLIGHT_FLAG_CODES):
        raise DeepSeekHarnessContractError("preflight_config_invalid") from None
    flags: dict[str, bool] = {}
    for key, value in items:
        if (
            type(key) is not str
            or key not in PREFLIGHT_FLAGS
            or key in flags
            or type(value) is not bool
        ):
            raise DeepSeekHarnessContractError("preflight_config_invalid") from None
        flags[key] = value
    return flags
