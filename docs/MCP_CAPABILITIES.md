# ContractLens — MCP capabilities

Generated reference for the MCP-compatible layer (stdio server + local tools).

## Server

- **Name:** ContractLens MCP Server
- **Version:** `0.4.4`

## Tools (29)

| Tool | Description |
| --- | --- |
| `list_project_files` | List text-like project files under a root (respects ignore dirs). |
| `read_project_file` | Read a UTF-8 file relative to repo_root (traversal blocked). |
| `search_in_files` | Search for a substring across text-like files. |
| `write_report` | Write Markdown/text inside the workspace (requires allow_write). |
| `find_openapi_specs` | Locate openapi/swagger JSON/YAML spec filenames under a repo root. |
| `get_changed_files` | List locally changed file paths under root via git diff (and staged paths when requested). |
| `parse_openapi_contracts` | Parse discovered specs into ApiContract-shaped operations. |
| `compare_backend_to_openapi` | Deterministic drift between backend static routes and OpenAPI-documented operations. |
| `scan_frontend_contracts` | Run the frontend HTTP client scanner. |
| `scan_backend_routes` | Run the backend route scanner. |
| `scan_frontend_auth` | Heuristic frontend auth signals (roles, headers, withCredentials, guards). |
| `scan_backend_auth` | Heuristic backend auth annotations (Authorize/AllowAnonymous, Express/FastAPI hints). |
| `compare_contracts` | Compare frontend vs backend contract rows. |
| `compare_auth_contracts` | Compare paired API contracts using frontend/backend auth scan findings (role/token drift). |
| `scan_documentation_contracts` | Extract Markdown documentation claims (routes, JSON keys, npm scripts, headings). |
| `compare_documentation_drift` | Compare documentation claims vs frontend/backend/OpenAPI scans plus package.json scripts. |
| `generate_contract_report` | Run the full analysis + Markdown report pipeline. |
| `generate_html_report` | Run full pipeline and emit Markdown plus standalone HTML (embedded stylesheet). |
| `get_latest_report` | Read the newest *.md from the reports directory. |
| `get_run_trace` | Load execution_trace.json for run_id=latest or run-YYYYMMDD-HHMMSS. |
| `list_runs` | List stamped run folders under contractlens-runs plus latest summary snapshot. |
| `get_run_summary` | Load run_summary.json for latest or a stamped run id. |
| `get_run_artifact` | Read one canonical artifact (JSON or report.md) from a run directory. |
| `explain_mismatch` | Deterministic narrative for one mismatch record. |
| `evaluate_ci_gate` | CI-style pass/fail from mismatch list + fail_on threshold (returns exit_code suggestion). |
| `list_mcp_resources` | List contractlens:// resource URIs. |
| `read_mcp_resource` | Fetch a resource payload as JSON (optional root override). |
| `list_mcp_prompts` | List deterministic prompt template names. |
| `get_mcp_prompt` | Render a prompt template string (no LLM). |

### Example tool calls (JSON bodies)

**`explain_mismatch`**

```json
{
  "mismatch": {
    "area": "endpoint_path",
    "frontend_expects": "/api/projects/{id}/files",
    "backend_provides": "/api/projects/{projectId}/models",
    "risk": "High",
    "suggestion": "Align route templates or add a compatibility alias."
  }
}
```

**`read_mcp_resource`**

```json
{ "uri": "contractlens://reports/latest" }
```

## Resources (7)

| URI | Description |
| --- | --- |
| `contractlens://repo/tree` | Relative file paths under a repo root (default: sample project; override via ?root= or tool arg). |
| `contractlens://contracts/frontend/latest` | Frontend API contracts from the latest snapshot under contractlens-runs/latest/. |
| `contractlens://contracts/backend/latest` | Backend routes from the latest snapshot. |
| `contractlens://mismatches/latest` | Comparator mismatches from the latest snapshot. |
| `contractlens://reports/latest` | Markdown body from the latest snapshot report.md. |
| `contractlens://runs/latest/trace` | LangGraph-style execution trace lines from the latest snapshot. |
| `contractlens://runs/latest/summary` | run_summary.json from latest (run_id, timing, contract counts, mismatch counts, report_path, optional runtime_probe). Stamped runs: contractlens://runs/run-YYYYMMDD-HHMMSS/summary (same shape; readable via resources/read). |

## Prompts (5)

| Name | Description |
| --- | --- |
| `audit_feature_contract` | Deterministic string template `audit_feature_contract` (MCP prompts/get). |
| `explain_contract_mismatch` | Deterministic string template `explain_contract_mismatch` (MCP prompts/get). |
| `generate_safe_fix_plan` | Deterministic string template `generate_safe_fix_plan` (MCP prompts/get). |
| `create_pr_review_comment` | Deterministic string template `create_pr_review_comment` (MCP prompts/get). |
| `summarize_agent_run` | Deterministic string template `summarize_agent_run` (MCP prompts/get). |

## Permission model

- **read_default:** True
- **write_requires_allow_write:** True
- **path_traversal_blocked:** True
- **ignored_directory_names:** .contractlens, .git, .idea, .venv, .vs, __pycache__, bin, build, dist, node_modules, obj, venv

## Artifact locations (relative to repo root)

- `contractlens-reports`
- `contractlens-runs`
- `contractlens-runs/latest`
- `contractlens-runs/latest/tool_audit_log.json`
- `contractlens-runs/latest/execution_trace.json`
- `contractlens-runs/latest/agent_trace.json`
- `contractlens-runs/latest/frontend_contracts.json`
- `contractlens-runs/latest/backend_contracts.json`
- `contractlens-runs/latest/mismatches.json`
- `contractlens-runs/latest/report.md`
- `contractlens-runs/latest/run_summary.json`

## Current limitations

- Heuristic static analysis only; dynamic URLs and indirection are incomplete.
- Auth/role drift uses line-window heuristics and a coarse role ranking map—it does not evaluate real JWT claims.
- Documentation drift scans Markdown only; nested repos and non-markdown specs are out of scope for this pass.
- OpenAPI parsing resolves `$ref` only within local components/schemas (single-hop chaining); no external refs.
- YAML specs require PyYAML; otherwise JSON specs load and YAML files are skipped with a note.
- MCP prompts/get arguments are dict[str, str]; embed JSON payloads as strings.
- stdio MCP protocol traffic uses stdout; server banners are emitted on stderr.
- Full JSON-RPC client coverage is optional; client_smoke_test validates local dispatch.

## Commands

```bash
python -m contractlens.mcp_server.capability_manifest
python -m contractlens.mcp_server.export_docs
python -m contractlens.mcp_server.inspect_mcp
python -m contractlens.mcp_server.stdio_client_test
python -m contractlens.mcp_server.client_smoke_test
```
