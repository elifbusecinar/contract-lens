"""FastAPI app: read-only dashboard over contractlens-runs/latest/ and stamped run-* folders."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from contractlens.config import PACKAGE_ROOT, default_html_report_path
from contractlens.runs.run_store import (
    STANDARD_ARTIFACTS,
    latest_dir,
    list_stamp_directories,
    read_artifact_json,
    resolve_run_directory,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_BUILT_DIR = Path(__file__).resolve().parent / "static_built"

_ALLOWED_READ_ROOT = PACKAGE_ROOT.resolve()


def _under_package_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(_ALLOWED_READ_ROOT)
        return True
    except ValueError:
        return False


def _safe_read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    if not _under_package_root(path):
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _load_summary(ld: Path) -> dict[str, Any]:
    p = ld / "run_summary.json"
    if not p.is_file():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _report_paths(summary: dict[str, Any], run_dir: Path) -> tuple[str | None, str | None, bool]:
    mirrored_md = run_dir / "report.md"
    md_path: Path | None = None
    if mirrored_md.is_file():
        md_path = mirrored_md
    rp = summary.get("report_path")
    if isinstance(rp, str) and rp.strip():
        cand = Path(rp.strip())
        if cand.is_file() and _under_package_root(cand):
            md_path = cand if md_path is None else md_path

    md_str = str(md_path.resolve()) if md_path else None

    html_path: Path | None = None
    if md_path and md_path.suffix.lower() == ".md":
        alt = md_path.with_suffix(".html")
        if alt.is_file():
            html_path = alt
    fn = summary.get("feature_name")
    if html_path is None and isinstance(fn, str) and fn.strip():
        h = default_html_report_path(fn)
        if h.is_file():
            html_path = h

    html_str = str(html_path.resolve()) if html_path else None
    return md_str, html_str, mirrored_md.is_file()


def _group_agent_trace(lines: list[Any]) -> dict[str, list[str]]:
    buckets = {
        "Frontend Analyst": [],
        "Backend Analyst": [],
        "Contract Reviewer": [],
        "Report Writer": [],
        "Other": [],
    }
    if not isinstance(lines, list):
        return buckets
    for raw in lines:
        line = str(raw).strip()
        if not line:
            continue
        if "Frontend Analyst" in line:
            buckets["Frontend Analyst"].append(line)
        elif "Backend Analyst" in line:
            buckets["Backend Analyst"].append(line)
        elif "Contract Reviewer" in line:
            buckets["Contract Reviewer"].append(line)
        elif "Report Writer" in line:
            buckets["Report Writer"].append(line)
        else:
            buckets["Other"].append(line)
    return buckets


def resolve_snapshot_run_dir(run_id: str | None) -> tuple[Path | None, str]:
    rid = (run_id or "latest").strip()
    if rid == "latest":
        ld = latest_dir()
        return (ld if ld.is_dir() else None, "latest")
    p = resolve_run_directory(rid)
    return (p, rid)


def build_snapshot(run_id: str | None = None) -> dict[str, Any]:
    run_dir, label = resolve_snapshot_run_dir(run_id)
    if run_dir is None:
        return {
            "run_id": label,
            "snapshot_dir": "",
            "latest_dir": str(latest_dir().resolve()),
            "run_summary": {},
            "has_run_summary": False,
            "execution_trace": [],
            "tool_audit": [],
            "agent_trace": [],
            "agent_trace_grouped": _group_agent_trace([]),
            "frontend_contracts": [],
            "backend_contracts": [],
            "mismatches": [],
            "report_paths": {
                "markdown_abs": None,
                "html_abs": None,
                "mirrored_report_md": False,
                "standard_artifacts": sorted(STANDARD_ARTIFACTS),
            },
            "feature_name_fallback": "",
            "errors": {"snapshot": "run directory missing"},
        }

    summary = _load_summary(run_dir)

    exec_lines: list[Any] = []
    raw_exec, err_exec = read_artifact_json(run_dir, "execution_trace.json")
    if not err_exec and isinstance(raw_exec, list):
        exec_lines = raw_exec

    audit_entries: list[Any] = []
    raw_audit, err_audit = read_artifact_json(run_dir, "tool_audit_log.json")
    if not err_audit and isinstance(raw_audit, list):
        audit_entries = raw_audit

    agent_lines: list[Any] = []
    raw_ag, err_ag = read_artifact_json(run_dir, "agent_trace.json")
    if not err_ag and isinstance(raw_ag, list):
        agent_lines = raw_ag

    fe: list[Any] = []
    raw_fe, err_fe = read_artifact_json(run_dir, "frontend_contracts.json")
    if not err_fe and isinstance(raw_fe, list):
        fe = raw_fe

    be: list[Any] = []
    raw_be, err_be = read_artifact_json(run_dir, "backend_contracts.json")
    if not err_be and isinstance(raw_be, list):
        be = raw_be

    mm: list[Any] = []
    raw_mm, err_mm = read_artifact_json(run_dir, "mismatches.json")
    if not err_mm and isinstance(raw_mm, list):
        mm = raw_mm

    md_path, html_path, mirrored_md = _report_paths(summary, run_dir)
    feature = summary.get("feature_name") or ""

    rid_out = str(summary.get("run_id") or label)

    return {
        "run_id": rid_out,
        "snapshot_dir": str(run_dir.resolve()),
        "latest_dir": str(latest_dir().resolve()),
        "run_summary": summary,
        "has_run_summary": bool(summary),
        "execution_trace": exec_lines,
        "tool_audit": audit_entries,
        "agent_trace": agent_lines,
        "agent_trace_grouped": _group_agent_trace(agent_lines),
        "frontend_contracts": fe,
        "backend_contracts": be,
        "mismatches": mm,
        "report_paths": {
            "markdown_abs": md_path,
            "html_abs": html_path,
            "mirrored_report_md": mirrored_md,
            "standard_artifacts": sorted(STANDARD_ARTIFACTS),
        },
        "feature_name_fallback": feature,
        "errors": {
            "execution_trace": err_exec,
            "tool_audit": err_audit,
            "agent_trace": err_ag,
            "frontend_contracts": err_fe,
            "backend_contracts": err_be,
            "mismatches": err_mm,
        },
    }


def build_runs_index(limit: int = 80) -> dict[str, Any]:
    stamped = list_stamp_directories(limit=max(1, min(limit, 500)))
    rows: list[dict[str, Any]] = []
    for p in stamped:
        meta: dict[str, Any] = {}
        sp = p / "run_summary.json"
        if sp.is_file():
            try:
                raw = json.loads(sp.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    meta = raw
            except (json.JSONDecodeError, OSError):
                meta = {}
        rp = meta.get("runtime_probe") if isinstance(meta.get("runtime_probe"), dict) else {}
        cfg = bool(rp.get("configured"))
        rows.append(
            {
                "run_id": p.name,
                "feature_name": meta.get("feature_name"),
                "completed_at": meta.get("completed_at"),
                "mismatch_count": meta.get("mismatch_count"),
                "high_risk_count": meta.get("high_risk_count"),
                "runtime_probe_configured": cfg,
                "runtime_probe_ok": rp.get("ok") if cfg else None,
            }
        )
    latest_meta: dict[str, Any] = {}
    lp = latest_dir() / "run_summary.json"
    if lp.is_file():
        try:
            raw = json.loads(lp.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                latest_meta = raw
        except (json.JSONDecodeError, OSError):
            latest_meta = {}
    return {
        "runs": rows,
        "latest_run_id": latest_meta.get("run_id"),
        "latest_summary": latest_meta,
    }


def _mm_sig(m: dict[str, Any]) -> str:
    return f"{m.get('area')}|{m.get('frontend_expects')}|{m.get('backend_provides')}|{m.get('risk')}"


def build_mismatch_diff(left_id: str | None, right_id: str | None) -> dict[str, Any]:
    left_dir, _ = resolve_snapshot_run_dir(left_id or "latest")
    right_dir, _ = resolve_snapshot_run_dir(right_id or "latest")
    if left_dir is None or right_dir is None:
        return {"error": "missing_run_dir", "left": left_id, "right": right_id}

    raw_l, _ = read_artifact_json(left_dir, "mismatches.json")
    raw_r, _ = read_artifact_json(right_dir, "mismatches.json")
    lm = [x for x in (raw_l if isinstance(raw_l, list) else []) if isinstance(x, dict)]
    rm = [x for x in (raw_r if isinstance(raw_r, list) else []) if isinstance(x, dict)]

    sl = {_mm_sig(m): m for m in lm}
    sr = {_mm_sig(m): m for m in rm}
    keys_l = set(sl.keys())
    keys_r = set(sr.keys())

    return {
        "left_run": left_id or "latest",
        "right_run": right_id or "latest",
        "left_total": len(lm),
        "right_total": len(rm),
        "only_in_left": [sl[k] for k in sorted(keys_l - keys_r)],
        "only_in_right": [sr[k] for k in sorted(keys_r - keys_l)],
        "in_both": len(keys_l & keys_r),
    }


def _markdown_to_html_fragment(md_text: str) -> str:
    try:
        import markdown as md_mod

        return md_mod.markdown(
            md_text,
            extensions=["tables", "fenced_code", "nl2br"],
            output_format="html",
        )
    except Exception:
        escaped = md_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre>{escaped}</pre>"


def create_app() -> FastAPI:
    app = FastAPI(title="ContractLens Dashboard", version="0.2.0")

    static_exists = STATIC_DIR.is_dir()
    built_index = STATIC_BUILT_DIR / "index.html"
    use_vite_build = built_index.is_file()

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/runs")
    async def api_runs(limit: int = Query(default=80, ge=1, le=500)) -> dict[str, Any]:
        return build_runs_index(limit=limit)

    @app.get("/api/diff")
    async def api_diff(
        left: str | None = Query(default=None),
        right: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return build_mismatch_diff(left, right)

    @app.get("/api/snapshot")
    async def snapshot(run_id: str | None = Query(default=None)) -> dict[str, Any]:
        return build_snapshot(run_id)

    @app.get("/api/report/markdown", response_class=PlainTextResponse)
    async def report_markdown(run_id: str | None = Query(default=None)) -> PlainTextResponse:
        run_dir, _ = resolve_snapshot_run_dir(run_id)
        if run_dir is None:
            return PlainTextResponse("Run directory not found.", status_code=404)
        summary = _load_summary(run_dir)
        md_path_str, _, _ = _report_paths(summary, run_dir)
        if not md_path_str:
            return PlainTextResponse("No Markdown report path resolved.", status_code=404)
        body = _safe_read_text(Path(md_path_str))
        if body is None:
            return PlainTextResponse("Could not read Markdown report.", status_code=404)
        return PlainTextResponse(body)

    @app.get("/api/report/markdown-html", response_class=HTMLResponse)
    async def report_markdown_html(run_id: str | None = Query(default=None)) -> HTMLResponse:
        run_dir, _ = resolve_snapshot_run_dir(run_id)
        if run_dir is None:
            return HTMLResponse("<p>Run not found.</p>", status_code=404)
        summary = _load_summary(run_dir)
        md_path_str, _, _ = _report_paths(summary, run_dir)
        if not md_path_str:
            return HTMLResponse("<p>No Markdown report available.</p>", status_code=404)
        body = _safe_read_text(Path(md_path_str))
        if body is None:
            return HTMLResponse("<p>Could not read Markdown report.</p>", status_code=404)
        inner = _markdown_to_html_fragment(body)
        wrapped = '<article class="markdown-body">' + inner + "</article>"
        return HTMLResponse(wrapped)

    @app.get("/open/html-report")
    async def open_html_report(run_id: str | None = Query(default=None)):
        run_dir, _ = resolve_snapshot_run_dir(run_id)
        if run_dir is None:
            return PlainTextResponse("Run directory not found.", status_code=404)
        summary = _load_summary(run_dir)
        _, html_path_str, _ = _report_paths(summary, run_dir)
        if not html_path_str:
            return PlainTextResponse(
                "No HTML report found — generate with --html or generate_html_report.", status_code=404
            )
        p = Path(html_path_str)
        if not p.is_file() or not _under_package_root(p):
            return PlainTextResponse("HTML report path invalid.", status_code=404)
        try:
            rel = p.resolve().relative_to(PACKAGE_ROOT.resolve())
            return RedirectResponse(url=f"/files/{rel.as_posix()}", status_code=307)
        except ValueError:
            return PlainTextResponse("HTML report outside package root.", status_code=404)

    @app.get("/files/{full_path:path}")
    async def serve_under_package(full_path: str):
        candidate = (PACKAGE_ROOT / full_path).resolve()
        if not _under_package_root(candidate) or not candidate.is_file():
            return PlainTextResponse("Not found.", status_code=404)
        return FileResponse(candidate)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        if use_vite_build:
            return HTMLResponse(built_index.read_text(encoding="utf-8"))
        index_html = STATIC_DIR / "index.html"
        if index_html.is_file():
            return HTMLResponse(index_html.read_text(encoding="utf-8"))
        return HTMLResponse(
            "<p>Dashboard UI missing — run <code>npm run build</code> in <code>dashboard-ui/</code> "
            "or keep <code>contractlens/dashboard/static/index.html</code>.</p>",
            status_code=500,
        )

    if use_vite_build:
        vite_assets = STATIC_BUILT_DIR / "assets"
        if vite_assets.is_dir():
            app.mount("/assets", StaticFiles(directory=str(vite_assets)), name="vite_assets")
    elif static_exists:
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


app = create_app()


def main() -> None:
    import uvicorn

    host = os.environ.get("CONTRACTLENS_DASHBOARD_HOST", "127.0.0.1")
    port = int(os.environ.get("CONTRACTLENS_DASHBOARD_PORT", "8765"))
    uvicorn.run(
        "contractlens.dashboard.server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
