"""Discover OpenAPI/Swagger spec files under a repository root."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from contractlens.mcp_server.permissions import path_under_root_has_ignored_dir

SPEC_FILENAMES_LOWER: frozenset[str] = frozenset(
    {
        "openapi.json",
        "swagger.json",
        "openapi.yaml",
        "openapi.yml",
        "swagger.yaml",
        "swagger.yml",
    }
)


def find_openapi_specs_under_root(root: str | Path) -> list[str]:
    """Return sorted POSIX paths relative to ``root`` for known spec filenames."""
    base = Path(root).resolve()
    found: list[str] = []
    if not base.is_dir():
        return found
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(base)
        except ValueError:
            continue
        if path_under_root_has_ignored_dir(rel):
            continue
        if p.name.lower() not in SPEC_FILENAMES_LOWER:
            continue
        found.append(rel.as_posix())
    found.sort()
    return found


def yaml_supported() -> bool:
    try:
        import yaml  # noqa: F401

        return True
    except ImportError:
        return False


def load_spec_dict(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Load JSON or YAML OpenAPI document. Returns ``(doc, error_message)``."""
    path = path.resolve()
    if not path.is_file():
        return None, f"not a file: {path}"
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return None, str(exc)
        if not isinstance(data, dict):
            return None, "top-level JSON must be an object"
        return data, None

    if suffix in {".yaml", ".yml"}:
        if not yaml_supported():
            return (
                None,
                "PyYAML is not installed; install PyYAML or use a .json spec",
            )
        import yaml

        data = yaml.safe_load(text)
        if data is None:
            return None, "empty YAML document"
        if not isinstance(data, dict):
            return None, "top-level YAML must be a mapping"
        return data, None

    return None, f"unsupported extension: {suffix}"
