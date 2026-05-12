"""Local MCP-style resource payloads for contractlens:// URIs (no remote fetch)."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from contractlens.config import PACKAGE_ROOT
from contractlens.runs.run_store import read_artifact_json, resolve_run_directory

from contractlens.mcp_server import tools


_EMPTY = {"status": "empty", "message": "No audit run has been executed yet."}

DEFAULT_REPO_ROOT_FOR_RESOURCES = str((PACKAGE_ROOT / "examples" / "sample_project").resolve())

RESOURCE_DESCRIPTIONS: dict[str, str] = {
    "contractlens://repo/tree": "Relative file paths under a repo root (default: sample project; override via ?root= or tool arg).",
    "contractlens://contracts/frontend/latest": "Frontend API contracts from the latest snapshot under contractlens-runs/latest/.",
    "contractlens://contracts/backend/latest": "Backend routes from the latest snapshot.",
    "contractlens://mismatches/latest": "Comparator mismatches from the latest snapshot.",
    "contractlens://reports/latest": "Markdown body from the latest snapshot report.md.",
    "contractlens://runs/latest/trace": "LangGraph-style execution trace lines from the latest snapshot.",
    "contractlens://runs/latest/summary": (
        "run_summary.json from latest (run_id, timing, contract counts, mismatch counts, report_path, optional runtime_probe). "
        "Stamped runs: contractlens://runs/run-YYYYMMDD-HHMMSS/summary (same shape; readable via resources/read)."
    ),
}

_RUN_SUMMARY_KEY_RE = re.compile(r"^runs/(latest|run-\d{8}-\d{6})/summary$")


def _latest_json(name: str) -> Any | None:
    from contractlens.mcp_server import run_store

    p = run_store.latest_dir() / name
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def get_repo_tree_resource(root: str) -> dict[str, Any]:
    listing = tools.list_project_files(root, verbose_log=False, repo_root=root)
    if listing.get("status") == "error":
        return {"uri": "contractlens://repo/tree", **listing}
    return {"uri": "contractlens://repo/tree", "status": "ok", "files": listing.get("files") or []}


def get_latest_frontend_contracts_resource() -> dict[str, Any]:
    data = _latest_json("frontend_contracts.json")
    if data is None:
        return {"uri": "contractlens://contracts/frontend/latest", **_EMPTY}
    return {"uri": "contractlens://contracts/frontend/latest", "status": "ok", "contracts": data}


def get_latest_backend_contracts_resource() -> dict[str, Any]:
    data = _latest_json("backend_contracts.json")
    if data is None:
        return {"uri": "contractlens://contracts/backend/latest", **_EMPTY}
    return {"uri": "contractlens://contracts/backend/latest", "status": "ok", "routes": data}


def get_latest_mismatches_resource() -> dict[str, Any]:
    data = _latest_json("mismatches.json")
    if data is None:
        return {"uri": "contractlens://mismatches/latest", **_EMPTY}
    return {"uri": "contractlens://mismatches/latest", "status": "ok", "mismatches": data}


def get_latest_report_resource() -> dict[str, Any]:
    from contractlens.mcp_server import run_store

    p = run_store.latest_dir() / "report.md"
    if not p.is_file():
        return {"uri": "contractlens://reports/latest", **_EMPTY}
    try:
        body = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"uri": "contractlens://reports/latest", **_EMPTY}
    return {"uri": "contractlens://reports/latest", "status": "ok", "path": str(p), "content": body}


def get_latest_run_trace_resource() -> dict[str, Any]:
    data = _latest_json("execution_trace.json")
    if data is None:
        return {"uri": "contractlens://runs/latest/trace", **_EMPTY}
    return {"uri": "contractlens://runs/latest/trace", "status": "ok", "trace": data}


def get_run_summary_resource(run_segment: str) -> dict[str, Any]:
    uri = f"contractlens://runs/{run_segment}/summary"
    rd = resolve_run_directory(run_segment)
    if rd is None:
        return {"uri": uri, **_EMPTY}
    data, err = read_artifact_json(rd, "run_summary.json")
    if err or data is None:
        return {"uri": uri, **_EMPTY}
    return {"uri": uri, "status": "ok", "summary": data}


RESOURCE_REGISTRY = [
    "contractlens://repo/tree",
    "contractlens://contracts/frontend/latest",
    "contractlens://contracts/backend/latest",
    "contractlens://mismatches/latest",
    "contractlens://reports/latest",
    "contractlens://runs/latest/trace",
    "contractlens://runs/latest/summary",
]


def _canonical_key(uri: str) -> tuple[str, dict[str, list[str]]]:
    parsed = urlparse(uri.strip())
    if parsed.scheme != "contractlens":
        return "", {}
    key = f"{parsed.netloc}{parsed.path}".strip("/")
    return key.replace("//", "/"), parse_qs(parsed.query)


def read_resource_by_uri(uri: str, *, root: str | None = None) -> dict[str, Any]:
    """Resolve a contractlens:// URI to a JSON-serializable payload (never raises)."""
    key, qs = _canonical_key(uri)
    root_eff = root
    if qs.get("root") and qs["root"][0].strip():
        root_eff = qs["root"][0].strip()

    try:
        if key == "repo/tree":
            rr = root_eff or DEFAULT_REPO_ROOT_FOR_RESOURCES
            return get_repo_tree_resource(rr)
        if key == "contracts/frontend/latest":
            return get_latest_frontend_contracts_resource()
        if key == "contracts/backend/latest":
            return get_latest_backend_contracts_resource()
        if key == "mismatches/latest":
            return get_latest_mismatches_resource()
        if key == "reports/latest":
            return get_latest_report_resource()
        if key == "runs/latest/trace":
            return get_latest_run_trace_resource()
        m_sum = _RUN_SUMMARY_KEY_RE.fullmatch(key)
        if m_sum:
            return get_run_summary_resource(m_sum.group(1))
        return {
            "uri": uri,
            "status": "error",
            "error": f"Unknown resource path: {key or uri!r}",
        }
    except Exception as exc:
        return {"uri": uri, "status": "error", "error": str(exc)}
