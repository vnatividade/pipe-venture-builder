# Platform Matrix

The PIP-709 bootstrap and doctor implementation uses Python `pathlib`, argument-array subprocess calls, JSON Schema Draft 2020-12, and repository-relative artifacts. It has no POSIX-shell dependency in the runtime path.

| Platform | Architectures | Contract status | Validation evidence | Known boundary |
|---|---|---|---|---|
| macOS | arm64, x86_64 | Supported | Unit, CLI, path-with-spaces, isolated-install, and live smoke validation on macOS arm64 | Executor and connector installation remains tool-specific. |
| Linux | arm64/aarch64, x86_64 | Supported contract | Injected platform fixtures and OS-neutral filesystem/Git code paths | A native Linux acceptance run is still recommended before release packaging. |
| Windows 10/11 | arm64, AMD64/x86_64 | Supported contract for Python CLI | Windows path rejection fixtures and injected platform matrix | Atelier's current shell installer and later Hermes adapter require their own Windows validation; doctor must show those gaps rather than imply support. |

An unknown operating system or architecture is `incompatible`, not silently supported.

Python 3.11+ and Git are required on every platform. Product repositories and manifest files must use repository-local paths; Windows drive paths, UNC-style absolute paths, Unix absolute paths, and `~` paths are rejected from the manifest.

Platform support here applies to `pipe bootstrap`, `pipe doctor`, manifest loading, and the existing Python CLI. It does not claim that every selected executor, connector, Atelier dependency, or future runtime adapter supports the same matrix.
