"""Build the Markdown audit report from workflow state."""

from __future__ import annotations

import json
from typing import Any

from contractlens.config import RUNS_DIR, display_path_under_repo
from contractlens.mcp_server import audit_log
from contractlens.mcp_server import capabilities as mcp_capabilities
from contractlens.mcp_server import prompts as mcp_prompt_catalog
from contractlens.mcp_server import resources as mcp_resources
from contractlens.mcp_server import tools as mcp_tools_mod
from contractlens.mcp_server.capability_manifest import SERVER_VERSION
from contractlens.scanner.route_graph import route_prefix_summary_markdown


def _bullet_lines(items: list[Any], *, formatter=lambda x: str(x)) -> str:
    if not items:
        return "_None detected._"
    return "\n".join(f"- {formatter(x)}" for x in items)


def _contract_row(side: str, d: dict[str, Any]) -> str:
    return (
        f"| {side} | `{d.get('method', '')}` | `{d.get('path', '')}` | `{d.get('source', '')}` | "
        f"{d.get('line') or ''} | {', '.join(d.get('request_fields') or [])} | "
        f"{', '.join(d.get('response_fields') or [])} | {d.get('request_dto') or ''} | "
        f"{d.get('response_dto') or ''} | {d.get('auth') or ''} |"
    )


def _mismatch_row(d: dict[str, Any]) -> str:
    fe = str(d.get("frontend_expects", "")).replace("|", "\\|")
    be = str(d.get("backend_provides", "")).replace("|", "\\|")
    sg = str(d.get("suggestion", "")).replace("|", "\\|")
    return (
        f"| `{d.get('area', '')}` | {d.get('risk', '')} | {fe} | {be} | {sg} |"
    )


def _mcp_audit_table() -> str:
    rows = audit_log.load_audit_entries()
    if not rows:
        return "_No MCP tool audit entries recorded for this process._"
    lines = [
        "| Tool | Status | Duration (ms) | Input summary | Output summary |",
        "|---|---:|---|---|---|",
    ]
    for e in rows:
        lines.append(
            f"| `{e.get('tool', '')}` | {e.get('status', '')} | {e.get('duration_ms', '')} | "
            f"{str(e.get('input_summary', ''))[:80].replace('|', '\\|')} | "
            f"{str(e.get('output_summary') or '—')[:80].replace('|', '\\|')} |"
        )
    return "\n".join(lines)


def _github_issue_draft(feature: str, mismatches: list[dict[str, Any]]) -> str:
    title = f"Contract drift audit: {feature}"
    bullets = []
    for d in mismatches[:12]:
        area = d.get("area", "")
        risk = d.get("risk", "")
        sug = d.get("suggestion", "")
        bullets.append(f"- **[{risk}] {area}**: {sug}")
    body_extra = "\n".join(bullets) if bullets else "_No mismatches recorded._"
    return (
        f"**Title (draft):** `{title}`\n\n"
        "**Body (draft):**\n\n"
        f"This issue was drafted from a ContractLens AI run for feature `{feature}`.\n\n"
        "### Findings\n\n"
        f"{body_extra}\n\n"
        "### Next steps\n\n"
        "- Align paths/DTOs listed above, or document intentional differences.\n"
        "- Re-run: `python -m contractlens.main --feature \"...\" --root <repo> --verbose`\n"
    )


def _agent_events_table(agent_events: list[dict[str, Any]]) -> str:
    if not agent_events:
        return "_No structured agent events (see legacy trace below)._"
    lines = [
        "| Agent | Role | Tool / step | Input summary | Output summary | ms |",
        "|---|---|---|---|---|---:|",
    ]
    for e in agent_events:
        lines.append(
            f"| {e.get('agent_name', '')} | {e.get('role', '')} | `{e.get('tool_used', '')}` | "
            f"{str(e.get('input_summary', ''))[:60].replace('|', '\\|')} | "
            f"{str(e.get('output_summary', ''))[:60].replace('|', '\\|')} | {e.get('duration_ms', '')} |"
        )
    return "\n".join(lines)


def _mcp_prompts_and_server_notes() -> str:
    native = mcp_capabilities.native_resources_prompts_available()
    prompt_names = ", ".join(f"`{n}`" for n in mcp_prompt_catalog.PROMPT_NAMES)
    if native:
        exposure = (
            "The ContractLens stdio MCP server registers native **resources** and **prompts** "
            "with the installed Python MCP SDK (verified via an internal registration probe)."
        )
    else:
        exposure = (
            "Native MCP **resources**/**prompts** registration was not confirmed for this environment "
            "(missing SDK, incompatible version, or probe failure). "
            "Use tools `list_mcp_resources`, `read_mcp_resource`, `list_mcp_prompts`, and `get_mcp_prompt`, "
            "or import `contractlens.mcp_server.resources` / `prompts` directly."
        )
    return (
        f"{exposure}\n\n"
        f"- **Deterministic prompt templates:** {prompt_names}\n"
        f"- **Tool audit log:** `{display_path_under_repo(audit_log.tool_audit_log_path())}`\n"
        f"- **Execution trace artifact:** `{display_path_under_repo(RUNS_DIR / 'latest' / 'execution_trace.json')}`\n"
    )


def _git_diff_mode_section(state: dict[str, Any]) -> str:
    requested = bool(state.get("changed_only"))
    considered = list(state.get("git_files_considered") or state.get("files") or [])
    count = int(state.get("git_changed_files_count") or 0)
    notes = state.get("git_diff_notes") or []

    if not requested:
        bullets = [
            "- **changed-only (CLI):** no",
            "- **effective:** full repository scan (discovered paths after ignore rules)",
            "- **Git changed paths applied:** _not applicable_",
            f"- **files scanned:** **{len(considered)}** (same list feeding scanners)",
        ]
        return "\n".join(bullets)

    graceful = bool(state.get("git_graceful_full_scan_not_git"))
    fallback = bool(state.get("git_fallback_full_scan_used"))
    narrowed_oas = bool(state.get("openapi_limit_to_scan_files"))

    if graceful:
        eff = "full scan (not inside a Git worktree or `git` unavailable — changed-only ignored)"
    elif fallback:
        eff = "full scan (`--fallback-full-scan` after zero intersecting changed paths)"
    elif not considered:
        eff = "narrowed — **no files** matched Git changes intersecting the project scan under root"
    elif narrowed_oas:
        eff = "narrowed to Git-changed files existing under root"
    else:
        eff = "requested"

    if graceful:
        count_disp = "_ignored — changed-only disabled under root (not Git)_"
    elif fallback:
        count_disp = f"**0** intersect (`--fallback-full-scan`; scanned **{len(considered)}** path(s))"
    else:
        count_disp = f"**{count}**"

    preview = considered[:60]
    rest = len(considered) - len(preview)
    file_lines = "\n".join(f"- `{p}`" for p in preview)
    if rest > 0:
        file_lines += f"\n- _…and **{rest}** more path(s)._"

    bullets = [
        "- **changed-only (CLI):** yes",
        f"- **effective:** {eff}",
        f"- **changed paths count (intersecting project scan):** {count_disp}",
        "",
        "### Files considered",
        "",
        file_lines if file_lines.strip() else "_None — scanners received an empty file list._",
        "",
        "### Git notes",
        "",
        _bullet_lines(list(notes)) if notes else "_None._",
        "",
        "### Limitations",
        "",
        "- Uses unstaged `git diff` paths plus cached paths (`git diff --cached`) merged deterministically.\n"
        "- Untracked files are **not** listed unless staged.\n"
        "- Paths are mapped through the Git worktree root; files outside `--root` are ignored.",
    ]
    return "\n".join(bullets)


def _runtime_probe_section(state: dict[str, Any]) -> str:
    pr = state.get("runtime_probe_result") or {}
    if not isinstance(pr, dict) or not pr.get("configured"):
        return (
            "_No runtime probe URL configured._ Set `probe_base_url` in `contractlens.toml` / `contractlens.yaml` "
            "or `CONTRACTLENS_PROBE_BASE_URL`. When set, ContractLens performs a single **GET** before the report "
            "is finalized and records the outcome below (response body is not analyzed)."
        )
    url = pr.get("url") or ""
    ok = bool(pr.get("ok"))
    code = pr.get("status_code")
    err = pr.get("error")
    elapsed = pr.get("elapsed_ms")
    lines = [
        "Optional reachability check (not a substitute for integration tests). **GET** only; redirects may be followed "
        "by the client; TLS/certificate validation uses system defaults.",
        "",
        f"- **URL:** `{url}`",
        f"- **Reachable (HTTP layer):** {'**yes**' if ok else '**no**'}",
        (
            f"- **HTTP status:** `{code}`"
            if code is not None
            else "- **HTTP status:** _none (connection failed before response)_"
        ),
    ]
    if elapsed is not None:
        lines.append(f"- **Round-trip:** `{elapsed}` ms")
    if err:
        lines.append(f"- **Error:** `{err}`")
    return "\n".join(lines)


def _run_summary_section(state: dict[str, Any]) -> str:
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
    return (
        f"- **Run ID:** `{state.get('run_id', '—')}`\n"
        f"- **Frontend contracts detected:** {len(fe)}\n"
        f"- **Backend routes detected:** {len(be)}\n"
        f"- **OpenAPI spec files detected:** {len(specs)}\n"
        f"- **OpenAPI operations parsed:** {len(oa_ops)}\n"
        f"- **OpenAPI/code drift mismatches:** {len(drift_mm)}\n"
        f"- **Mismatch count (total):** {len(mm)}\n"
        f"- **Auth / role drift rows:** {len(auth_mm)}\n"
        f"- **Documentation claims extracted:** {len(doc_claims)}\n"
        f"- **Documentation drift rows:** {len(doc_drift)}\n"
        f"- **High-risk mismatches:** {high}\n"
        f"- **Report path:** `{rp}`\n"
        f"- **Audit log:** `{display_path_under_repo(audit_log.tool_audit_log_path())}`\n"
        f"- **Execution trace:** `{display_path_under_repo(RUNS_DIR / 'latest' / 'execution_trace.json')}`\n"
        f"- **Run summary artifact:** `{display_path_under_repo(RUNS_DIR / 'latest' / 'run_summary.json')}`\n"
    )


def _auth_contract_analysis_section(state: dict[str, Any]) -> str:
    auth_mm = [x for x in (state.get("auth_mismatches") or []) if isinstance(x, dict)]
    fe_a = state.get("frontend_auth_findings") or []
    be_a = state.get("backend_auth_findings") or []

    def esc(s: str) -> str:
        return str(s).replace("|", "\\|").replace("\n", " ").replace("\r", "")

    lines = [
        "Heuristic pairing of frontend auth hints (roles, headers, `withCredentials`) with backend `[Authorize]` / "
        "`[AllowAnonymous]` plus light Express/FastAPI signals. **Treat as advisory**, not a substitute for policy tests.",
        "",
        f"- Frontend auth findings: **{len(fe_a)}**",
        f"- Backend auth findings: **{len(be_a)}**",
        "",
        "| Area | Frontend Assumption | Backend Rule | Risk | Suggestion |",
        "|---|---|---|---|---|",
    ]
    for d in auth_mm:
        lines.append(
            f"| `{esc(str(d.get('area', '')))}` | {esc(str(d.get('frontend_assumption', '')))} | "
            f"{esc(str(d.get('backend_rule', '')))} | {esc(str(d.get('risk', '')))} | {esc(str(d.get('suggestion', '')))} |"
        )
    if not auth_mm:
        lines.append("| _none_ | — | — | Low | No auth/role drift rows from current heuristics._ |")
    return "\n".join(lines)


def _documentation_drift_section(state: dict[str, Any]) -> str:
    rows = [x for x in (state.get("documentation_drift") or []) if isinstance(x, dict)]
    claims = state.get("documentation_claims") or []

    def esc(s: str) -> str:
        return str(s).replace("|", "\\|").replace("\n", " ").replace("\r", "")

    lines = [
        "Deterministic comparison of Markdown under the analyzed root vs scanned frontend/backend/OpenAPI contracts "
        "for **routes**, while **JSON property claims** use **backend-only** payload hints when backend routes exist "
        "(so client/OpenAPI optimism does not mask stale docs). Shallow `package.json` script checks apply when manifests exist. "
        "This is advisory static analysis, not a documentation linter.",
        "",
        f"- Markdown-derived claims: **{len(claims)}**",
        "",
        "| Documentation Claim | Actual Implementation | Risk | Suggestion |",
        "|---|---|---|---|",
    ]
    for d in rows:
        lines.append(
            f"| {esc(str(d.get('documentation_claim', '')))} | {esc(str(d.get('actual_implementation', '')))} | "
            f"{esc(str(d.get('risk', '')))} | {esc(str(d.get('suggestion', '')))} |"
        )
    if not rows:
        lines.append("| _none_ | — | Low | No documentation drift rows from current heuristics._ |")
    return "\n".join(lines)


def _openapi_swagger_analysis_section(state: dict[str, Any]) -> str:
    specs = state.get("openapi_spec_paths") or []
    oa = state.get("openapi_contracts") or []
    notes = state.get("openapi_notes") or []
    mm = state.get("mismatches") or []
    drift = [
        m
        for m in mm
        if isinstance(m, dict) and str(m.get("area", "")).startswith("openapi_vs_code")
    ]
    lim = (
        "- Parses OpenAPI 3.x / Swagger 2.0 JSON deterministically; YAML requires PyYAML.\n"
        "- `$ref` resolution is shallow (`components/schemas` / `definitions` only); external refs are not fetched.\n"
        "- Server `url` bases are not prefixed onto paths in this MVP.\n"
        "- Operation pairing uses HTTP method plus path-token similarity; ties break by lexicographic sort."
    )
    parts = [
        f"- **Detected spec files:** {len(specs)} ({', '.join(f'`{s}`' for s in specs) or '_none_'})",
        f"- **Endpoints parsed from specs:** {len(oa)}",
        "",
        "### Schema / documentation drift findings",
        "",
        _bullet_lines(drift, formatter=lambda d: f"`{d.get('area')}` ({d.get('risk')}): {d.get('suggestion')}"),
        "",
        "### Loader notes",
        "",
        _bullet_lines(list(notes)) if notes else "_None._",
        "",
        "### Limitations",
        "",
        lim,
    ]
    return "\n".join(parts)


def _mcp_capability_summary_section() -> str:
    sdk = mcp_capabilities.native_resources_prompts_available()
    sdk_label = "active (native resources/prompts probe succeeded)" if sdk else "fallback or unconfirmed (use helper tools)"
    return (
        f"- **Manifest server version:** `{SERVER_VERSION}`\n"
        f"- **Tools:** {len(mcp_tools_mod.MCP_TOOL_NAMES)}\n"
        f"- **Resources:** {len(mcp_resources.RESOURCE_REGISTRY)}\n"
        f"- **Prompts:** {len(mcp_prompt_catalog.PROMPT_NAMES)}\n"
        f"- **SDK registration:** {sdk_label}\n"
        "- **Permission model:** Reads confined to the selected repo root; writes require explicit `allow_write`; "
        "path traversal blocked; heavy folders (`node_modules`, `.git`, build outputs, virtualenvs) ignored.\n"
    )


def _run_artifacts_section(state: dict[str, Any]) -> str:
    rp = state.get("report_path") or ""
    rid = state.get("run_id") or ""
    latest_rel = display_path_under_repo(RUNS_DIR / "latest")
    artifacts = [
        "`run_summary.json` — run id, timing (`duration_ms`), counts, `report_path`",
        "`tool_audit_log.json` — MCP tool audit entries for this process",
        "`execution_trace.json` — LangGraph / sequential workflow trace lines",
        "`agent_trace.json` — CrewAI-style legacy string trace lines",
        "`frontend_contracts.json` / `backend_contracts.json` / `mismatches.json`",
        "`report.md` — mirrored Markdown audit written alongside `contractlens-reports/` output",
    ]
    bullet_lines = "\n".join(f"  - {a}" for a in artifacts)
    return (
        f"- **Current run id:** `{rid or '—'}`\n"
        f"- **Primary report:** `{rp}`\n"
        f"- **Latest snapshot dir:** `{latest_rel}/`\n"
        f"- **Stamped copies:** `contractlens-runs/run-YYYYMMDD-HHMMSS/` (same filenames as `latest/`)\n"
        f"- **Standard artifacts:**\n{bullet_lines}\n"
        "- **MCP:** `list_runs`, `get_run_summary`, `get_run_artifact`; resources `contractlens://runs/latest/summary` "
        "and `contractlens://runs/<run_id>/summary`."
    )


def build_markdown_report(state: dict[str, Any]) -> str:
    feature = state.get("feature_name", "")
    root = state.get("root_path", "")
    files = state.get("files") or []
    fe = state.get("frontend_findings") or []
    be = state.get("backend_findings") or []
    mm = state.get("mismatches") or []
    risk = state.get("risk_summary") or {}
    mcp_trace = state.get("mcp_trace") or []
    exec_trace = state.get("execution_trace") or []
    agent_trace = state.get("agent_trace") or []
    agent_events = state.get("agent_events") or []

    limitations = """- Static analysis is heuristic-based.
- Complex dynamic API paths may not be fully resolved.
- Response field extraction is limited in the MVP.
- **Git changed-only:** uses local `git diff --name-only` plus cached names when enabled; **untracked files are omitted** unless staged. Requires `git` on `PATH`.
- **OpenAPI:** shallow `$ref` resolution; server URL prefixes not applied to paths; YAML needs PyYAML.
- **MCP-first:** tools are audited locally; resources expose latest artifacts under `contractlens-runs/latest/`.
- **Agents:** With `OPENAI_API_KEY` (and without `--deterministic-agents`), CrewAI runs LLM agents that still call ContractLens tools. Otherwise steps stay deterministic but MCP-backed.
- **MCP stdio server:** exposes tools always; native resources/prompts only when the SDK registration probe succeeds — otherwise use helper tools listed in the MCP tooling section.
- **Auth / role pairing:** role ranks and token detection are regex/heuristic; policies are not expanded to roles.
- **Documentation drift:** Markdown-only heuristics; fenced JSON blocks drive property extraction; shallow `package.json` script checks only cover discovered manifests.
- **Runtime HTTP probe:** optional single GET to a configured base URL; result is recorded in this report and does not alter static findings.
- **GitHub REST:** optional PAT flags on `contractlens.main` — Issues, issue/PR timeline comments, and PR reviews (`COMMENT`, not line-threaded).
- **Scan cache:** `.contractlens/scan-cache/` uses mtime/size plus **SHA-256 of file bytes** when present in the cache entry (legacy entries fingerprint-only until resaved).
- Permission boundaries apply to filesystem tools.
- The sample project is intentionally tiny so the demo stays reproducible."""

    md_parts = [
        "# ContractLens AI Report",
        "",
        "## Feature",
        "",
        f"{feature}",
        "",
        "## Scan Summary",
        "",
        f"- Root: `{root}`",
        f"- Files discovered: **{len(files)}**",
        "",
        "## Git Diff Mode",
        "",
        _git_diff_mode_section(state),
        "",
        "## Run Summary",
        "",
        _run_summary_section(state),
        "",
        "## Runtime HTTP Probe",
        "",
        _runtime_probe_section(state),
        "",
        "## MCP Capability Summary",
        "",
        _mcp_capability_summary_section(),
        "",
        "## MCP Tool Usage",
        "",
        "### Tool audit (this process)",
        "",
        _mcp_audit_table(),
        "",
        "### High-level MCP trace",
        "",
        _bullet_lines(list(mcp_trace)),
        "",
        "## MCP Resources",
        "",
        "Local resource identifiers (payloads via `contractlens/mcp_server/resources.py`):",
        "",
        _bullet_lines(list(mcp_resources.RESOURCE_REGISTRY), formatter=lambda u: f"`{u}`"),
        "",
        "### MCP prompts & server tooling",
        "",
        _mcp_prompts_and_server_notes(),
        "",
        "## LangGraph Execution Trace",
        "",
        _bullet_lines(list(exec_trace)),
        "",
        "## Agent Trace",
        "",
        "### Structured agent / MCP tool events",
        "",
        _agent_events_table([e for e in agent_events if isinstance(e, dict)]),
        "",
        "### Legacy string trace",
        "",
        _bullet_lines(list(agent_trace)),
        "",
        "## Run Artifacts",
        "",
        _run_artifacts_section(state),
        "",
        "## Frontend Expectations",
        "",
        "```json",
        json.dumps(fe, indent=2),
        "```",
        "",
        "## Backend Reality",
        "",
        "```json",
        json.dumps(be, indent=2),
        "```",
        "",
        "## OpenAPI / Swagger Analysis",
        "",
        _openapi_swagger_analysis_section(state),
        "",
        "## Auth / Role Contract Analysis",
        "",
        _auth_contract_analysis_section(state),
        "",
        "## Documentation Drift Analysis",
        "",
        _documentation_drift_section(state),
        "",
        "## Route Prefix Graph (heuristic)",
        "",
        route_prefix_summary_markdown(
            [x for x in be if isinstance(x, dict)],
            [x for x in fe if isinstance(x, dict)],
        ),
        "",
        "## API Contract Table",
        "",
        "| Side | Method | Path | Source | Line | Request fields | Response fields | Request DTO | Response DTO | Auth |",
        "|---|---|---|---:|---|---|---|---|---|",
    ]

    for d in fe:
        md_parts.append(_contract_row("FE", d))
    if not fe:
        md_parts.append("| FE | _none_ | | | | | | | | |")

    for d in be:
        md_parts.append(_contract_row("BE", d))
    if not be:
        md_parts.append("| BE | _none_ | | | | | | | | |")

    md_parts.extend(
        [
            "",
            "## Mismatch Report",
            "",
            "| Area | Risk | Frontend expects | Backend provides | Suggestion |",
            "|---|---|---|---|---|",
        ]
    )

    for d in mm:
        md_parts.append(_mismatch_row(d))

    if not mm:
        md_parts.append("| _none_ | Low | | | No mismatches detected._ |")

    md_parts.extend(
        [
            "",
            "## Risk Assessment",
            "",
            f"- High: **{risk.get('high', 0)}**",
            f"- Medium: **{risk.get('medium', 0)}**",
            f"- Low: **{risk.get('low', 0)}**",
            f"- Unknown: **{risk.get('unknown', 0)}**",
            "",
            "## Suggested Fix Plan",
            "",
            _bullet_lines(
                mm,
                formatter=lambda d: f"**{d.get('area')}** ({d.get('risk')}): {d.get('suggestion')}",
            ),
            "",
            "## Optional GitHub Issue Draft",
            "",
            _github_issue_draft(feature, [m for m in mm if isinstance(m, dict)]),
            "",
            "## Current Limitations",
            "",
            limitations,
            "",
        ]
    )

    return "\n".join(md_parts)
