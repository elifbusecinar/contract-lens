"""Frontend scanner: TS template literals + deduplication."""

from __future__ import annotations

from pathlib import Path

from contractlens.config import PACKAGE_ROOT


def test_sample_project_api_client_template_literal() -> None:
    from contractlens.scanner.frontend_scanner import scan_file

    root = PACKAGE_ROOT / "examples" / "sample_project"
    contracts = scan_file(root / "frontend" / "projectApi.ts", root)
    posts = [c for c in contracts if c.method == "POST"]
    assert len(posts) == 1
    assert posts[0].path == "/api/projects/{id}/files"
