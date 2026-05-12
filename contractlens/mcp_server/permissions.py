"""Local permission boundaries for MCP-style repo tools (read vs write, root containment)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from contractlens.config import PACKAGE_ROOT

IGNORE_DIR_NAMES = frozenset(
    {
        "node_modules",
        ".git",
        ".contractlens",
        "bin",
        "obj",
        "dist",
        "build",
        "__pycache__",
        ".venv",
        "venv",
        ".idea",
        ".vs",
    }
)

_EXTRA_IGNORE_DIR_NAMES: frozenset[str] = frozenset()


def reset_extra_ignore_dir_names() -> None:
    """Clear repo-local ignore dirs (e.g. between tests)."""
    global _EXTRA_IGNORE_DIR_NAMES
    _EXTRA_IGNORE_DIR_NAMES = frozenset()


def set_extra_ignore_dir_names(names: Iterable[str]) -> None:
    """Merge directory **name** fragments (not paths) skipped like ``node_modules``."""
    global _EXTRA_IGNORE_DIR_NAMES
    clean = tuple(str(x).strip() for x in names if str(x).strip())
    _EXTRA_IGNORE_DIR_NAMES = frozenset(clean)


def effective_ignore_dir_names() -> frozenset[str]:
    return IGNORE_DIR_NAMES | _EXTRA_IGNORE_DIR_NAMES


def path_under_root_has_ignored_dir(relative_path: Path) -> bool:
    parts = relative_path.parts
    check = parts[:-1] if parts else ()
    names = effective_ignore_dir_names()
    return any(p in names for p in check)


def resolve_under_root(repo_root: Path, user_path: str) -> tuple[Path | None, dict[str, Any] | None]:
    """
    Resolve user_path to absolute path that must stay under repo_root.
    Returns (resolved_path, None) or (None, error_dict).
    """
    root = repo_root.resolve()
    if not root.is_dir():
        return None, {"status": "error", "error": f"Root is not a directory: {root}"}

    raw = Path(user_path)
    if not raw.is_absolute():
        candidate = (root / raw).resolve()
    else:
        candidate = raw.resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        return None, {"status": "error", "error": "Path is outside allowed root."}

    # Block traversal tricks after resolve (e.g. symlinks) — best-effort
    try:
        rel = candidate.relative_to(root)
    except ValueError:
        return None, {"status": "error", "error": "Path is outside allowed root."}

    if ".." in user_path.replace("\\", "/").split("/"):
        return None, {"status": "error", "error": "Path traversal is not allowed."}

    if path_under_root_has_ignored_dir(rel):
        return None, {"status": "error", "error": "Path is inside an ignored directory (e.g. node_modules, .git)."}

    return candidate, None


def resolve_repo_root(root: str) -> tuple[Path | None, dict[str, Any] | None]:
    base = Path(root).resolve()
    if not base.exists():
        return None, {"status": "error", "error": f"root not found: {base}"}
    if not base.is_dir():
        return None, {"status": "error", "error": f"root is not a directory: {base}"}
    return base, None


def assert_write_allowed(allow_write: bool) -> dict[str, Any] | None:
    if not allow_write:
        return {"status": "error", "error": "Write operations require allow_write=True."}
    return None


def resolve_write_within_workspace(user_path: str) -> tuple[Path | None, dict[str, Any] | None]:
    """Reports and audit logs must stay under the ContractLens project workspace."""
    workspace = PACKAGE_ROOT.resolve()
    raw = Path(user_path)
    candidate = (workspace / raw).resolve() if not raw.is_absolute() else raw.resolve()
    try:
        candidate.relative_to(workspace)
    except ValueError:
        return None, {"status": "error", "error": "Write path is outside the ContractLens workspace."}
    return candidate, None
