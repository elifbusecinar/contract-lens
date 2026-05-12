"""Append-only style tool audit log for MCP-style calls."""

from __future__ import annotations

import json
import threading
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contractlens.config import RUNS_DIR

_LOCK = threading.Lock()
_RUN_ID: ContextVar[str | None] = ContextVar("contractlens_audit_run_id", default=None)


def runs_root() -> Path:
    return RUNS_DIR.resolve()


def latest_dir() -> Path:
    d = runs_root() / "latest"
    d.mkdir(parents=True, exist_ok=True)
    return d


def tool_audit_log_path() -> Path:
    return latest_dir() / "tool_audit_log.json"


def attach_run_context(run_id: str) -> Token[str | None]:
    """Link subsequent tool audit entries to a workflow run_id (supports nesting via ContextVar)."""
    return _RUN_ID.set(run_id)


def detach_run_context(token: Token[str | None]) -> None:
    _RUN_ID.reset(token)


def current_run_id() -> str | None:
    return _RUN_ID.get()


def log_tool_call(
    *,
    tool: str,
    input_summary: str,
    status: str,
    duration_ms: float,
    error: str | None = None,
    output_summary: str | None = None,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": current_run_id(),
        "tool": tool,
        "input_summary": input_summary[:500],
        "status": status,
        "duration_ms": round(duration_ms, 2),
        "error": error,
        "output_summary": (output_summary[:400] + "...") if output_summary and len(output_summary) > 400 else output_summary,
    }
    path = tool_audit_log_path()
    with _LOCK:
        entries: list[dict[str, Any]] = []
        if path.is_file():
            try:
                entries = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(entries, list):
                    entries = []
            except (json.JSONDecodeError, OSError):
                entries = []
        entries.append(entry)
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def load_audit_entries() -> list[dict[str, Any]]:
    path = tool_audit_log_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []
