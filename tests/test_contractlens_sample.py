"""Golden-style checks on the bundled sample project."""

from __future__ import annotations

from pathlib import Path

from contractlens.config import PACKAGE_ROOT
from contractlens.mcp_server import tools


def test_sample_project_frontend_backend_and_openapi_signals() -> None:
    root = str((PACKAGE_ROOT / "examples" / "sample_project").resolve())
    fe = tools.scan_frontend_contracts(root, verbose_log=False)
    be = tools.scan_backend_routes(root, verbose_log=False)
    assert len(fe.get("contracts") or []) >= 1
    assert len(be.get("routes") or []) >= 1

    cmp_res = tools.compare_contracts(fe.get("contracts") or [], be.get("routes") or [], verbose_log=False)
    assert len(cmp_res.get("mismatches") or []) >= 3

    fo = tools.find_openapi_specs(root, verbose_log=False)
    assert len(fo.get("spec_paths") or []) >= 1


def test_dashboard_snapshot_smoke() -> None:
    from fastapi.testclient import TestClient

    from contractlens.dashboard.server import app

    c = TestClient(app)
    assert c.get("/api/health").json().get("status") == "ok"
    snap = c.get("/api/snapshot")
    assert snap.status_code == 200
    body = snap.json()
    assert "has_run_summary" in body
    runs = c.get("/api/runs")
    assert runs.status_code == 200
    assert "runs" in runs.json()
