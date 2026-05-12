"""Enumerate files under a repository root for scanners."""

from __future__ import annotations

from pathlib import Path


FRONTEND_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".vue"}
BACKEND_EXTENSIONS = {".cs", ".py", ".js"}  # .js for Express samples


def scan_repository_files(root: str | Path) -> list[str]:
    """Return POSIX-style relative paths for all files under root."""
    base = Path(root).resolve()
    if not base.is_dir():
        return []
    out: list[str] = []
    for p in base.rglob("*"):
        if p.is_file():
            try:
                rel = p.relative_to(base)
            except ValueError:
                continue
            out.append(str(rel).replace("\\", "/"))
    out.sort()
    return out


def filter_by_extensions(paths: list[str], extensions: set[str]) -> list[str]:
    return [p for p in paths if Path(p).suffix.lower() in extensions]
