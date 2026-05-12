"""Standalone HTML audit report from workflow state (embedded CSS, no CDN)."""

from __future__ import annotations

import html
import json
from typing import Any

from contractlens.config import RUNS_DIR, display_path_under_repo
from contractlens.mcp_server import audit_log
from contractlens.mcp_server import capabilities as mcp_capabilities
from contractlens.mcp_server import prompts as mcp_prompt_catalog
from contractlens.mcp_server import resources as mcp_resources
from contractlens.mcp_server import tools as mcp_tools_mod
from contractlens.mcp_server.capability_manifest import SERVER_VERSION
from contractlens.reporting.markdown_report import (
    _auth_contract_analysis_section,
    _documentation_drift_section,
    _openapi_swagger_analysis_section,
    _runtime_probe_section,
)
from contractlens.scanner.route_graph import route_prefix_summary_markdown

LIMITATIONS_HTML_BULLETS = [
    "Static analysis is heuristic-based.",
    "Complex dynamic API paths may not be fully resolved.",
    "Response field extraction is limited in the MVP.",
    "Git changed-only uses local git diff paths; untracked files are omitted unless staged.",
    "OpenAPI: shallow $ref resolution; YAML needs PyYAML.",
    "MCP-first tooling is audited locally; resources expose latest artifacts under contractlens-runs/latest/.",
    "Agents use deterministic fallback unless an LLM provider is configured.",
    "Auth / role pairing and documentation drift use regex/heuristic extraction.",
    "Optional GitHub REST via PAT: Issues (`--github-create-issue`), timeline comments (`--github-issue-comment`), PR summary reviews (`--github-pr-review`).",
    "Optional scan cache under `.contractlens/scan-cache/` when `--scan-cache` or config enables it.",
    "Permission boundaries apply to filesystem tools.",
    "The sample project is intentionally tiny so the demo stays reproducible.",
]


def _esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def _risk_badge_class(risk: Any) -> str:
    r = str(risk or "").strip().lower()
    if r == "high":
        return "risk-high"
    if r == "medium":
        return "risk-medium"
    if r == "low":
        return "risk-low"
    return "risk-unknown"


def _run_summary_rows(state: dict[str, Any]) -> list[tuple[str, str]]:
    fe = state.get("frontend_findings") or []
    be = state.get("backend_findings") or []
    specs = state.get("openapi_spec_paths") or []
    oa_ops = state.get("openapi_contracts") or []
    mm = state.get("mismatches") or []
    auth_mm = state.get("auth_mismatches") or []
    doc_claims = state.get("documentation_claims") or []
    doc_drift = state.get("documentation_drift") or []
    drift_mm = [
        x for x in mm if isinstance(x, dict) and str(x.get("area", "")).startswith("openapi_vs_code")
    ]
    high = sum(1 for x in mm if isinstance(x, dict) and str(x.get("risk", "")).strip().lower() == "high")
    rp = state.get("report_path") or ""
    hp = state.get("html_report_path") or ""
    rows = [
        ("Run ID", str(state.get("run_id") or "—")),
        ("Frontend contracts detected", str(len(fe))),
        ("Backend routes detected", str(len(be))),
        ("OpenAPI spec files detected", str(len(specs))),
        ("OpenAPI operations parsed", str(len(oa_ops))),
        ("OpenAPI/code drift mismatches", str(len(drift_mm))),
        ("Mismatch count (total)", str(len(mm))),
        ("Auth / role drift rows", str(len(auth_mm))),
        ("Documentation claims extracted", str(len(doc_claims))),
        ("Documentation drift rows", str(len(doc_drift))),
        ("High-risk mismatches", str(high)),
        ("Markdown report path", rp),
    ]
    if hp:
        rows.append(("HTML report path", hp))
    rows.extend(
        [
            ("Audit log", display_path_under_repo(audit_log.tool_audit_log_path())),
            ("Execution trace artifact", display_path_under_repo(RUNS_DIR / "latest" / "execution_trace.json")),
            ("Run summary artifact", display_path_under_repo(RUNS_DIR / "latest" / "run_summary.json")),
        ]
    )
    return rows


def _mcp_capability_rows() -> list[tuple[str, str]]:
    sdk = mcp_capabilities.native_resources_prompts_available()
    sdk_label = "active (native resources/prompts probe succeeded)" if sdk else "fallback or unconfirmed (use helper tools)"
    return [
        ("Manifest server version", SERVER_VERSION),
        ("Tools", str(len(mcp_tools_mod.MCP_TOOL_NAMES))),
        ("Resources", str(len(mcp_resources.RESOURCE_REGISTRY))),
        ("Prompts", str(len(mcp_prompt_catalog.PROMPT_NAMES))),
        ("SDK registration", sdk_label),
        (
            "Permission model",
            "Reads confined to repo root; writes require allow_write; path traversal blocked; heavy dirs ignored.",
        ),
    ]


def _audit_rows() -> list[dict[str, Any]]:
    rows = audit_log.load_audit_entries()
    return rows if isinstance(rows, list) else []


def _suggested_contract_tests(mismatches: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for m in mismatches[:24]:
        if not isinstance(m, dict):
            continue
        area = m.get("area", "")
        fe = m.get("frontend_expects", "")
        be = m.get("backend_provides", "")
        out.append(
            f"Contract/integration test covering `{_esc(area)}`: assert frontend expectation `{_esc(fe)}` "
            f"matches backend `{_esc(be)}` (or document intentional divergence)."
        )
    return out


def _dl_rows(rows: list[tuple[str, str]]) -> str:
    parts = []
    for k, v in rows:
        parts.append(f"<dt>{_esc(k)}</dt><dd><code>{_esc(v)}</code></dd>")
    return "\n".join(parts)


def _section(title: str, inner: str) -> str:
    return (
        f'<section class="panel" id="{_esc(title.lower().replace(" ", "-"))}">'
        f'<h2>{_esc(title)}</h2>{inner}</section>'
    )


def _markdown_fragment_to_html(md_text: str) -> str:
    try:
        import markdown as md_mod

        return md_mod.markdown(
            md_text,
            extensions=["tables", "fenced_code", "nl2br"],
            output_format="html",
        )
    except Exception:
        return f"<pre>{html.escape(md_text)}</pre>"


def _api_contract_table_html(state: dict[str, Any]) -> str:
    fe = [x for x in (state.get("frontend_findings") or []) if isinstance(x, dict)]
    be = [x for x in (state.get("backend_findings") or []) if isinstance(x, dict)]

    def row(side: str, d: dict[str, Any]) -> str:
        rf = ", ".join(d.get("request_fields") or [])
        rsf = ", ".join(d.get("response_fields") or [])
        return (
            "<tr>"
            f"<td>{_esc(side)}</td>"
            f"<td><code>{_esc(d.get('method', ''))}</code></td>"
            f"<td><code>{_esc(d.get('path', ''))}</code></td>"
            f"<td>{_esc(d.get('source', ''))}</td>"
            f"<td>{_esc(d.get('line') or '')}</td>"
            f"<td>{_esc(rf)}</td>"
            f"<td>{_esc(rsf)}</td>"
            f"<td>{_esc(d.get('request_dto') or '')}</td>"
            f"<td>{_esc(d.get('response_dto') or '')}</td>"
            f"<td>{_esc(d.get('auth') or '')}</td>"
            "</tr>"
        )

    parts = [
        '<table class="data-table"><thead><tr>'
        "<th>Side</th><th>Method</th><th>Path</th><th>Source</th><th>Line</th>"
        "<th>Request fields</th><th>Response fields</th><th>Request DTO</th><th>Response DTO</th><th>Auth</th>"
        "</tr></thead><tbody>",
    ]
    if fe:
        for d in fe:
            parts.append(row("FE", d))
    else:
        parts.append('<tr><td colspan="10" class="muted">No frontend contracts.</td></tr>')
    if be:
        for d in be:
            parts.append(row("BE", d))
    else:
        parts.append('<tr><td colspan="10" class="muted">No backend routes.</td></tr>')
    parts.append("</tbody></table>")
    return "".join(parts)


def build_html_report(state: dict[str, Any]) -> str:
    feature = state.get("feature_name", "")
    fe = [x for x in (state.get("frontend_findings") or []) if isinstance(x, dict)]
    be = [x for x in (state.get("backend_findings") or []) if isinstance(x, dict)]
    mm = [x for x in (state.get("mismatches") or []) if isinstance(x, dict)]
    exec_trace = state.get("execution_trace") or []
    agent_trace = state.get("agent_trace") or []
    risk = state.get("risk_summary") or {}

    mismatch_rows = []
    for d in mm:
        mismatch_rows.append(
            "<tr>"
            f"<td><code>{_esc(d.get('area', ''))}</code></td>"
            f'<td><span class="risk-badge {_risk_badge_class(d.get("risk"))}">{_esc(d.get("risk", ""))}</span></td>'
            f"<td>{_esc(d.get('frontend_expects', ''))}</td>"
            f"<td>{_esc(d.get('backend_provides', ''))}</td>"
            f"<td>{_esc(d.get('suggestion', ''))}</td>"
            "</tr>"
        )
    mismatch_table = (
        '<table class="data-table"><thead><tr>'
        "<th>Area</th><th>Risk</th><th>Frontend expects</th><th>Backend provides</th><th>Suggestion</th>"
        "</tr></thead><tbody>"
        + (
            "".join(mismatch_rows)
            if mismatch_rows
            else '<tr><td colspan="5" class="muted">No mismatches detected.</td></tr>'
        )
        + "</tbody></table>"
    )

    fix_items = "".join(
        f"<li><strong>{_esc(d.get('area'))}</strong> ({_esc(d.get('risk'))}): {_esc(d.get('suggestion'))}</li>"
        for d in mm
    )
    fix_section = f"<ol class=\"fix-plan\">{fix_items}</ol>" if fix_items else "<p class=\"muted\">No fixes suggested.</p>"

    tests = _suggested_contract_tests(mm)
    tests_inner = (
        "<ul>" + "".join(f"<li>{t}</li>" for t in tests) + "</ul>"
        if tests
        else ""
    )
    tests_block = (
        _section("Suggested Contract Tests", tests_inner)
        if tests_inner
        else ""
    )

    audit_entries = _audit_rows()
    audit_body = ""
    if audit_entries:
        audit_body = (
            '<table class="data-table"><thead><tr>'
            "<th>Tool</th><th>Status</th><th>Duration (ms)</th><th>Input summary</th><th>Output summary</th>"
            "</tr></thead><tbody>"
        )
        for e in audit_entries:
            if not isinstance(e, dict):
                continue
            audit_body += (
                "<tr>"
                f"<td><code>{_esc(e.get('tool', ''))}</code></td>"
                f"<td>{_esc(e.get('status', ''))}</td>"
                f"<td>{_esc(e.get('duration_ms', ''))}</td>"
                f"<td>{_esc(str(e.get('input_summary', ''))[:120])}</td>"
                f"<td>{_esc(str(e.get('output_summary') or '—')[:120])}</td>"
                "</tr>"
            )
        audit_body += "</tbody></table>"
    else:
        audit_body = '<p class="muted">No MCP tool audit entries recorded for this process.</p>'

    trace_items = "".join(f"<li><code>{_esc(line)}</code></li>" for line in exec_trace)
    agent_items = "".join(f"<li>{_esc(line)}</li>" for line in agent_trace)

    limitations_list = "".join(f"<li>{_esc(x)}</li>" for x in LIMITATIONS_HTML_BULLETS)

    openapi_panel = _section(
        "OpenAPI / Swagger Analysis",
        f'<div class="markdown-section">{_markdown_fragment_to_html(_openapi_swagger_analysis_section(state))}</div>',
    )
    auth_panel = _section(
        "Auth / Role Contract Analysis",
        f'<div class="markdown-section">{_markdown_fragment_to_html(_auth_contract_analysis_section(state))}</div>',
    )
    doc_panel = _section(
        "Documentation Drift Analysis",
        f'<div class="markdown-section">{_markdown_fragment_to_html(_documentation_drift_section(state))}</div>',
    )
    route_panel = _section(
        "Route Prefix Graph (heuristic)",
        f'<div class="markdown-section">{_markdown_fragment_to_html(route_prefix_summary_markdown(be, fe))}</div>',
    )
    api_contract_panel = _section("API Contract Table", _api_contract_table_html(state))

    css = """
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --elevated: #1c2128;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #8b949e;
  --accent: #58a6ff;
  --green: #3fb950;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 1.5rem 1.25rem 3rem;
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  font-size: 15px;
}
header.hero {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(165deg, var(--elevated) 0%, var(--surface) 55%);
  margin-bottom: 1.5rem;
}
header.hero h1 { margin: 0 0 0.35rem; font-size: 1.35rem; letter-spacing: -0.02em; }
header.hero .subtitle { color: var(--muted); font-size: 0.9rem; }
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.25rem 1.25rem;
  margin-bottom: 1.25rem;
}
.panel h2 {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.5rem;
}
dl.summary-grid {
  display: grid;
  grid-template-columns: minmax(140px, 220px) 1fr;
  gap: 0.35rem 1rem;
  margin: 0;
}
dl.summary-grid dt { color: var(--muted); font-weight: 600; font-size: 0.82rem; margin: 0; }
dl.summary-grid dd { margin: 0; font-size: 0.88rem; word-break: break-word; }
dl.summary-grid code { font-size: 0.85rem; color: var(--green); }
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.data-table th, .data-table td {
  border: 1px solid var(--border);
  padding: 0.45rem 0.55rem;
  vertical-align: top;
}
.data-table th {
  background: var(--elevated);
  color: var(--muted);
  font-weight: 600;
  text-align: left;
}
.data-table code { font-size: 0.8rem; }
pre.json {
  margin: 0;
  padding: 0.85rem 1rem;
  background: var(--elevated);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.78rem;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-word;
}
ul.trace, ol.fix-plan { margin: 0; padding-left: 1.25rem; }
ul.trace li { margin-bottom: 0.25rem; font-size: 0.84rem; }
ul.trace code { font-size: 0.8rem; color: var(--muted); }
.muted { color: var(--muted); font-style: italic; }
.risk-badge {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.risk-high { background: #490202; color: #ffb4a8; border: 1px solid #a40e26; }
.risk-medium { background: #3d2a00; color: #ffdf9a; border: 1px solid #9e6a03; }
.risk-low { background: #033a16; color: #acf2bd; border: 1px solid #238636; }
.risk-unknown { background: #21262d; color: var(--muted); border: 1px solid var(--border); }
.risk-strip {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.88rem;
  margin-bottom: 0.75rem;
}
.risk-strip span strong { color: var(--accent); }
.markdown-section :is(h1,h2,h3,h4) { color: var(--accent); margin: 0.65rem 0 0.35rem; font-size: 0.95rem; }
.markdown-section pre {
  background: var(--elevated);
  padding: 0.65rem 0.85rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.78rem;
}
.markdown-section code { font-size: 0.82rem; background: var(--elevated); padding: 0.08rem 0.28rem; border-radius: 4px; }
.markdown-section table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin: 0.5rem 0; }
.markdown-section th, .markdown-section td {
  border: 1px solid var(--border);
  padding: 0.35rem 0.45rem;
  vertical-align: top;
}
.markdown-section ul { padding-left: 1.25rem; }
footer.meta {
  margin-top: 2rem;
  font-size: 0.75rem;
  color: var(--muted);
  text-align: center;
}
"""

    body_inner = (
        '<header class="hero">'
        f"<h1>ContractLens AI — Audit Report</h1>"
        f'<p class="subtitle">Static HTML export · Feature: <strong>{_esc(feature)}</strong></p>'
        "</header>"
        + _section("Feature", f"<p class=\"lead\">{_esc(feature)}</p>")
        + _section(
            "Run Summary",
            f"<dl class=\"summary-grid\">{_dl_rows(_run_summary_rows(state))}</dl>",
        )
        + _section(
            "Runtime HTTP Probe",
            f'<div class="markdown-section">{_markdown_fragment_to_html(_runtime_probe_section(state))}</div>',
        )
        + _section(
            "MCP Capability Summary",
            f"<dl class=\"summary-grid\">{_dl_rows(_mcp_capability_rows())}</dl>",
        )
        + _section("MCP Tool Usage", audit_body)
        + _section(
            "LangGraph Execution Trace",
            f"<ul class=\"trace\">{trace_items or '<li class=\"muted\">No trace lines.</li>'}</ul>",
        )
        + _section(
            "Agent Trace",
            f"<ul class=\"trace\">{agent_items or '<li class=\"muted\">No agent trace lines.</li>'}</ul>",
        )
        + _section(
            "Frontend Expectations",
            f"<pre class=\"json\">{_esc(json.dumps(fe, indent=2))}</pre>",
        )
        + _section(
            "Backend Reality",
            f"<pre class=\"json\">{_esc(json.dumps(be, indent=2))}</pre>",
        )
        + openapi_panel
        + auth_panel
        + doc_panel
        + route_panel
        + api_contract_panel
        + '<div class="risk-strip">'
        f"<span><strong>High</strong>: {_esc(risk.get('high', 0))}</span>"
        f"<span><strong>Medium</strong>: {_esc(risk.get('medium', 0))}</span>"
        f"<span><strong>Low</strong>: {_esc(risk.get('low', 0))}</span>"
        f"<span><strong>Unknown</strong>: {_esc(risk.get('unknown', 0))}</span>"
        + "</div>"
        + _section("Mismatch Report", mismatch_table)
        + _section("Suggested Fix Plan", fix_section)
        + tests_block
        + _section("Current Limitations", f"<ul>{limitations_list}</ul>")
        + '<footer class="meta">Generated by ContractLens AI · embedded stylesheet · no external assets</footer>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(feature)} — ContractLens Report</title>
<style>
{css}
</style>
</head>
<body>
{body_inner}
</body>
</html>
"""
