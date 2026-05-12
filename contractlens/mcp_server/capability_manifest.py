"""Structured MCP capability manifest (JSON) for portfolio and clients."""

from __future__ import annotations

import json
from typing import Any

from contractlens.config import DEFAULT_REPORT_DIR, PACKAGE_ROOT, RUNS_DIR

from contractlens.mcp_server import prompts as pr
from contractlens.mcp_server import resources as res
from contractlens.mcp_server.permissions import effective_ignore_dir_names

SERVER_DISPLAY_NAME = "ContractLens MCP Server"
SERVER_VERSION = "0.4.4"

TOOL_ENTRIES: list[dict[str, str]] = [
    {"name": "list_project_files", "description": "List text-like project files under a root (respects ignore dirs)."},
    {"name": "read_project_file", "description": "Read a UTF-8 file relative to repo_root (traversal blocked)."},
    {"name": "search_in_files", "description": "Search for a substring across text-like files."},
    {"name": "write_report", "description": "Write Markdown/text inside the workspace (requires allow_write)."},
    {"name": "find_openapi_specs", "description": "Locate openapi/swagger JSON/YAML spec filenames under a repo root."},
    {
        "name": "get_changed_files",
        "description": "List locally changed file paths under root via git diff (and staged paths when requested).",
    },
    {"name": "parse_openapi_contracts", "description": "Parse discovered specs into ApiContract-shaped operations."},
    {
        "name": "compare_backend_to_openapi",
        "description": "Deterministic drift between backend static routes and OpenAPI-documented operations.",
    },
    {"name": "scan_frontend_contracts", "description": "Run the frontend HTTP client scanner."},
    {"name": "scan_backend_routes", "description": "Run the backend route scanner."},
    {
        "name": "scan_frontend_auth",
        "description": "Heuristic frontend auth signals (roles, headers, withCredentials, guards).",
    },
    {
        "name": "scan_backend_auth",
        "description": "Heuristic backend auth annotations (Authorize/AllowAnonymous, Express/FastAPI hints).",
    },
    {"name": "compare_contracts", "description": "Compare frontend vs backend contract rows."},
    {
        "name": "compare_auth_contracts",
        "description": "Compare paired API contracts using frontend/backend auth scan findings (role/token drift).",
    },
    {
        "name": "scan_documentation_contracts",
        "description": "Extract Markdown documentation claims (routes, JSON keys, npm scripts, headings).",
    },
    {
        "name": "compare_documentation_drift",
        "description": "Compare documentation claims vs frontend/backend/OpenAPI scans plus package.json scripts.",
    },
    {"name": "generate_contract_report", "description": "Run the full analysis + Markdown report pipeline."},
    {
        "name": "generate_html_report",
        "description": "Run full pipeline and emit Markdown plus standalone HTML (embedded stylesheet).",
    },
    {"name": "get_latest_report", "description": "Read the newest *.md from the reports directory."},
    {
        "name": "get_run_trace",
        "description": "Load execution_trace.json for run_id=latest or run-YYYYMMDD-HHMMSS.",
    },
    {"name": "list_runs", "description": "List stamped run folders under contractlens-runs plus latest summary snapshot."},
    {"name": "get_run_summary", "description": "Load run_summary.json for latest or a stamped run id."},
    {
        "name": "get_run_artifact",
        "description": "Read one canonical artifact (JSON or report.md) from a run directory.",
    },
    {"name": "explain_mismatch", "description": "Deterministic narrative for one mismatch record."},
    {
        "name": "evaluate_ci_gate",
        "description": "CI-style pass/fail from mismatch list + fail_on threshold (returns exit_code suggestion).",
    },
    {"name": "list_mcp_resources", "description": "List contractlens:// resource URIs."},
    {"name": "read_mcp_resource", "description": "Fetch a resource payload as JSON (optional root override)."},
    {"name": "list_mcp_prompts", "description": "List deterministic prompt template names."},
    {"name": "get_mcp_prompt", "description": "Render a prompt template string (no LLM)."},
]


def build_capability_manifest() -> dict[str, Any]:
    resources = [
        {"uri": u, "description": res.RESOURCE_DESCRIPTIONS.get(u, "")} for u in res.RESOURCE_REGISTRY
    ]
    prompts = [
        {"name": n, "description": f"Deterministic string template `{n}` (MCP prompts/get)."} for n in pr.PROMPT_NAMES
    ]
    return {
        "server_name": SERVER_DISPLAY_NAME,
        "server_version": SERVER_VERSION,
        "tools": TOOL_ENTRIES,
        "resources": resources,
        "prompts": prompts,
        "permissions": {
            "read_default": True,
            "write_requires_allow_write": True,
            "path_traversal_blocked": True,
            "ignored_directory_names": sorted(effective_ignore_dir_names()),
        },
        "artifacts": {
            "reports_dir": DEFAULT_REPORT_DIR.relative_to(PACKAGE_ROOT).as_posix(),
            "runs_dir": RUNS_DIR.relative_to(PACKAGE_ROOT).as_posix(),
            "runs_latest_dir": (RUNS_DIR / "latest").relative_to(PACKAGE_ROOT).as_posix(),
            "tool_audit_log": (RUNS_DIR / "latest" / "tool_audit_log.json").relative_to(PACKAGE_ROOT).as_posix(),
            "execution_trace": (RUNS_DIR / "latest" / "execution_trace.json").relative_to(PACKAGE_ROOT).as_posix(),
            "agent_trace": (RUNS_DIR / "latest" / "agent_trace.json").relative_to(PACKAGE_ROOT).as_posix(),
            "frontend_contracts": (RUNS_DIR / "latest" / "frontend_contracts.json").relative_to(PACKAGE_ROOT).as_posix(),
            "backend_contracts": (RUNS_DIR / "latest" / "backend_contracts.json").relative_to(PACKAGE_ROOT).as_posix(),
            "mismatches": (RUNS_DIR / "latest" / "mismatches.json").relative_to(PACKAGE_ROOT).as_posix(),
            "report_snapshot": (RUNS_DIR / "latest" / "report.md").relative_to(PACKAGE_ROOT).as_posix(),
            "run_summary": (RUNS_DIR / "latest" / "run_summary.json").relative_to(PACKAGE_ROOT).as_posix(),
        },
        "limitations": [
            "Heuristic static analysis only; dynamic URLs and indirection are incomplete.",
            "Auth/role drift uses line-window heuristics and a coarse role ranking map—it does not evaluate real JWT claims.",
            "Documentation drift scans Markdown only; nested repos and non-markdown specs are out of scope for this pass.",
            "OpenAPI parsing resolves `$ref` only within local components/schemas (single-hop chaining); no external refs.",
            "YAML specs require PyYAML; otherwise JSON specs load and YAML files are skipped with a note.",
            "MCP prompts/get arguments are dict[str, str]; embed JSON payloads as strings.",
            "stdio MCP protocol traffic uses stdout; server banners are emitted on stderr.",
            "Full JSON-RPC client coverage is optional; client_smoke_test validates local dispatch.",
        ],
    }


def main() -> None:
    print(json.dumps(build_capability_manifest(), indent=2))


if __name__ == "__main__":
    main()
