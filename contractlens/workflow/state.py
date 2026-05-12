"""Shared workflow state (plain dict for LangGraph + sequential fallback)."""

from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    feature_name: str
    root_path: str
    mode: str
    verbose: bool
    report_output_dir: str
    use_llm_agents: bool
    mcp_allow_write: bool

    files: list[str]
    openapi_limit_to_scan_files: bool
    changed_only: bool
    fallback_full_scan: bool
    git_changed_only_requested: bool
    git_is_repository: bool
    git_graceful_full_scan_not_git: bool
    git_fallback_full_scan_used: bool
    git_changed_files_count: int
    git_diff_notes: list[str]
    git_files_considered: list[str]
    frontend_findings: list[dict[str, Any]]
    backend_findings: list[dict[str, Any]]
    openapi_spec_paths: list[str]
    openapi_contracts: list[dict[str, Any]]
    openapi_notes: list[str]
    frontend_auth_findings: list[dict[str, Any]]
    backend_auth_findings: list[dict[str, Any]]
    auth_mismatches: list[dict[str, Any]]
    documentation_claims: list[dict[str, Any]]
    documentation_drift: list[dict[str, Any]]
    mismatches: list[dict[str, Any]]
    risk_summary: dict[str, int]

    report_path: str
    report_markdown: str
    generate_html: bool
    html_report_path: str
    runtime_probe_base_url: str
    runtime_probe_result: dict[str, Any]
    scan_cache_enabled: bool

    execution_trace: list[str]
    mcp_trace: list[str]
    agent_trace: list[str]
    errors: list[str]


def new_state(
    feature_name: str,
    root_path: str,
    *,
    verbose: bool = False,
    mode: str = "default",
) -> dict[str, Any]:
    return {
        "feature_name": feature_name,
        "root_path": root_path,
        "verbose": verbose,
        "mode": mode,
        "report_output_dir": "",
        "files": [],
        "openapi_limit_to_scan_files": False,
        "changed_only": False,
        "fallback_full_scan": False,
        "git_changed_only_requested": False,
        "git_is_repository": False,
        "git_graceful_full_scan_not_git": False,
        "git_fallback_full_scan_used": False,
        "git_changed_files_count": 0,
        "git_diff_notes": [],
        "git_files_considered": [],
        "frontend_findings": [],
        "backend_findings": [],
        "openapi_spec_paths": [],
        "openapi_contracts": [],
        "openapi_notes": [],
        "frontend_auth_findings": [],
        "backend_auth_findings": [],
        "auth_mismatches": [],
        "documentation_claims": [],
        "documentation_drift": [],
        "mismatches": [],
        "risk_summary": {},
        "report_path": "",
        "report_markdown": "",
        "generate_html": False,
        "html_report_path": "",
        "runtime_probe_base_url": "",
        "runtime_probe_result": {},
        "scan_cache_enabled": False,
        "execution_trace": [],
        "mcp_trace": [],
        "agent_trace": [],
        "agent_events": [],
        "use_llm_agents": False,
        "mcp_allow_write": True,
        "errors": [],
    }


def trace_append(state: dict[str, Any], key: str, msg: str) -> None:
    state.setdefault(key, [])
    cast_list = state[key]
    if isinstance(cast_list, list):
        cast_list.append(msg)
