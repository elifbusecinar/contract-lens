"""Runtime HTTP probe helper."""

from __future__ import annotations

from contractlens.reporting.markdown_report import _runtime_probe_section
from contractlens.reporting.runtime_probe import run_runtime_http_probe


def test_probe_empty_url_not_configured() -> None:
    r = run_runtime_http_probe("")
    assert r == {"configured": False}


def test_runtime_probe_section_markdown_when_skipped() -> None:
    md = _runtime_probe_section({"runtime_probe_result": {"configured": False}})
    assert "No runtime probe URL configured" in md


def test_runtime_probe_section_markdown_when_ok() -> None:
    md = _runtime_probe_section(
        {
            "runtime_probe_result": {
                "configured": True,
                "url": "https://example.invalid.test",
                "ok": True,
                "status_code": 200,
                "error": None,
                "elapsed_ms": 12,
            },
        }
    )
    assert "Reachable" in md and "200" in md
