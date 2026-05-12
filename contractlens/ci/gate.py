"""Deterministic CI gate from mismatch risk levels (no GitHub API)."""

from __future__ import annotations

from typing import Any

_RISK_RANK = {"high": 3, "medium": 2, "low": 1, "unknown": 0}


def _canonical_fail_on(value: str) -> str:
    s = str(value or "High").strip().lower()
    if s == "high":
        return "High"
    if s == "medium":
        return "Medium"
    if s == "low":
        return "Low"
    return "High"


def _bucket_risk(raw: str) -> str:
    r = str(raw or "Unknown").strip()
    key = r.lower()
    if key == "high":
        return "High"
    if key == "medium":
        return "Medium"
    if key == "low":
        return "Low"
    return "Unknown"


def evaluate_ci_gate(mismatches: list[Any], *, fail_on: str = "High") -> dict[str, Any]:
    """
    Fail (exit_code 1) if any mismatch has risk severity **at or above** ``fail_on``.

    Ordering: High > Medium > Low > Unknown.
    """
    threshold_label = _canonical_fail_on(fail_on)
    threshold = _RISK_RANK[threshold_label.lower()]

    counts = {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
    rows = [m for m in mismatches if isinstance(m, dict)]

    for m in rows:
        counts[_bucket_risk(str(m.get("risk", "")))] += 1

    failed = False
    for m in rows:
        rk = _RISK_RANK.get(str(m.get("risk", "")).strip().lower(), 0)
        if rk >= threshold:
            failed = True
            break

    passed = not failed
    return {
        "passed": passed,
        "exit_code": 0 if passed else 1,
        "summary": {
            "counts_by_risk": counts,
            "fail_on": threshold_label,
            "mismatch_total": len(rows),
        },
    }


def format_ci_summary_lines(result: dict[str, Any]) -> list[str]:
    """Human-readable lines for stdout (``[CI] ...``)."""
    summary = result.get("summary") or {}
    counts = summary.get("counts_by_risk") or {}
    fo = summary.get("fail_on", "High")
    passed = bool(result.get("passed"))
    lines = [
        f"[CI] High risk mismatches: {counts.get('High', 0)}",
        f"[CI] Medium risk mismatches: {counts.get('Medium', 0)}",
        f"[CI] Low risk mismatches: {counts.get('Low', 0)}",
        f"[CI] Unknown risk mismatches: {counts.get('Unknown', 0)}",
        f"[CI] Fail threshold: {fo}",
        f"[CI] Result: {'passed' if passed else 'failed'}",
    ]
    return lines
