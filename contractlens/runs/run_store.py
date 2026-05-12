"""Persist ContractLens run snapshots under contractlens-runs/latest and stamped folders."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contractlens.config import RUNS_DIR

RUN_ID_STAMP_RE = re.compile(r"^run-\d{8}-\d{6}$")

STANDARD_ARTIFACTS: frozenset[str] = frozenset(
    {
        "run_summary.json",
        "tool_audit_log.json",
        "execution_trace.json",
        "agent_trace.json",
        "frontend_contracts.json",
        "backend_contracts.json",
        "mismatches.json",
        "report.md",
    }
)

# Deprecated filenames removed from latest/ when snapshotting (older MVP layouts).
_OBSOLETE_ARTIFACTS: frozenset[str] = frozenset(
    {"agent_events.json", "risk_summary.json", "run_meta.json"},
)


def runs_root() -> Path:
    return RUNS_DIR.resolve()


def latest_dir() -> Path:
    d = runs_root() / "latest"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_latest_json(name: str, data: Any) -> Path:
    path = latest_dir() / name
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def resolve_run_directory(run_id: str) -> Path | None:
    """Resolve `latest` or `run-YYYYMMDD-HHMMSS` to an on-disk directory."""
    rid = (run_id or "").strip()
    if rid in ("", "latest"):
        ld = latest_dir()
        return ld if ld.is_dir() else None
    if RUN_ID_STAMP_RE.match(rid):
        p = runs_root() / rid
        return p if p.is_dir() else None
    return None


def list_stamp_directories(*, limit: int = 100) -> list[Path]:
    """Newest-first stamped run directories."""
    root = runs_root()
    if not root.is_dir():
        return []
    dirs = [p for p in root.iterdir() if p.is_dir() and RUN_ID_STAMP_RE.match(p.name)]
    dirs.sort(key=lambda p: p.name, reverse=True)
    return dirs[:limit]


def _duration_ms(started_at: str | None, completed_at: str) -> int:
    if not started_at:
        return 0
    try:
        s = started_at.replace("Z", "+00:00")
        e = completed_at.replace("Z", "+00:00")
        ts = datetime.fromisoformat(s)
        te = datetime.fromisoformat(e)
        return max(0, int((te - ts).total_seconds() * 1000))
    except (ValueError, TypeError):
        return 0


def _purge_obsolete_latest_files() -> None:
    ld = latest_dir()
    for name in _OBSOLETE_ARTIFACTS:
        try:
            (ld / name).unlink(missing_ok=True)
        except OSError:
            pass


def snapshot_run(
    *,
    feature_name: str,
    root_path: str,
    execution_trace: list[str],
    agent_trace: list[str],
    frontend_contracts: list[dict[str, Any]],
    backend_contracts: list[dict[str, Any]],
    mismatches: list[dict[str, Any]],
    report_path: str,
    report_markdown: str,
    run_id: str | None = None,
    started_at: str | None = None,
    runtime_probe_base_url: str = "",
    runtime_probe_result: dict[str, Any] | None = None,
) -> tuple[Path, Path | None]:
    """Write canonical artifacts to latest/, mirror into run-YYYYMMDD-HHMMSS/."""
    completed_at = datetime.now(timezone.utc).isoformat()
    stamp = run_id if run_id and RUN_ID_STAMP_RE.match(run_id) else f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    started_iso = started_at or completed_at

    _purge_obsolete_latest_files()

    write_latest_json("execution_trace.json", execution_trace)
    write_latest_json("agent_trace.json", agent_trace)
    write_latest_json("frontend_contracts.json", frontend_contracts)
    write_latest_json("backend_contracts.json", backend_contracts)
    write_latest_json("mismatches.json", mismatches)

    report_md_path = latest_dir() / "report.md"
    report_md_path.write_text(report_markdown, encoding="utf-8")

    high_risk = sum(1 for m in mismatches if isinstance(m, dict) and str(m.get("risk", "")).lower() == "high")
    rp: dict[str, Any]
    if isinstance(runtime_probe_result, dict):
        rp = dict(runtime_probe_result)
    else:
        rp = {"configured": False}
    if not rp.get("configured"):
        rp = {"configured": False}

    summary = {
        "run_id": stamp,
        "feature_name": feature_name,
        "root_path": root_path,
        "started_at": started_iso,
        "completed_at": completed_at,
        "duration_ms": _duration_ms(started_iso, completed_at),
        "frontend_contract_count": len(frontend_contracts),
        "backend_route_count": len(backend_contracts),
        "mismatch_count": len(mismatches),
        "high_risk_count": high_risk,
        "report_path": report_path,
        "runtime_probe_base_url": (runtime_probe_base_url or "").strip(),
        "runtime_probe": rp,
    }
    write_latest_json("run_summary.json", summary)

    stamped = runs_root() / stamp
    try:
        if stamped.exists():
            shutil.rmtree(stamped)
        shutil.copytree(latest_dir(), stamped)
    except OSError:
        return latest_dir(), None
    return latest_dir(), stamped


def read_artifact_text(run_dir: Path, artifact: str) -> tuple[str | None, str | None]:
    """Returns (content, error)."""
    if artifact not in STANDARD_ARTIFACTS:
        return None, f"unknown artifact: {artifact!r}"
    path = run_dir / artifact
    if not path.is_file():
        return None, f"missing file: {artifact}"
    try:
        return path.read_text(encoding="utf-8", errors="replace"), None
    except OSError as exc:
        return None, str(exc)


def read_artifact_json(run_dir: Path, artifact: str) -> tuple[Any, str | None]:
    raw, err = read_artifact_text(run_dir, artifact)
    if err or raw is None:
        return None, err or "empty"
    if artifact.endswith(".md"):
        return None, "use text endpoint for report.md"
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as exc:
        return None, str(exc)
