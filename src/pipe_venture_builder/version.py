"""Package version resolution."""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("pipe-venture-builder")
except PackageNotFoundError:  # pragma: no cover - source tree without install
    __version__ = "0.1.0"
