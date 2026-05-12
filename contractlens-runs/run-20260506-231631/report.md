# ContractLens AI Report

## Feature

Create Project + Upload File

## Scan Summary

- Root: `C:\dev\projects\contract-lens\examples\sample_project`
- Files discovered: **7**

## Git Diff Mode

- **changed-only (CLI):** no
- **effective:** full repository scan (discovered paths after ignore rules)
- **Git changed paths applied:** _not applicable_
- **files scanned:** **7** (same list feeding scanners)

## Run Summary

- **Run ID:** `run-20260506-231631`
- **Frontend contracts detected:** 2
- **Backend routes detected:** 2
- **OpenAPI spec files detected:** 1
- **OpenAPI operations parsed:** 2
- **OpenAPI/code drift mismatches:** 3
- **Mismatch count (total):** 9
- **Auth / role drift rows:** 3
- **Documentation claims extracted:** 7
- **Documentation drift rows:** 2
- **High-risk mismatches:** 4
- **Report path:** `C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md`
- **Audit log:** `contractlens-runs/latest/tool_audit_log.json`
- **Execution trace:** `contractlens-runs/latest/execution_trace.json`
- **Run summary artifact:** `contractlens-runs/latest/run_summary.json`


## MCP Capability Summary

- **Manifest server version:** `0.4.2`
- **Tools:** 25
- **Resources:** 6
- **Prompts:** 5
- **SDK registration:** active (native resources/prompts probe succeeded)
- **Permission model:** Reads confined to the selected repo root; writes require explicit `allow_write`; path traversal blocked; heavy folders (`node_modules`, `.git`, build outputs, virtualenvs) ignored.


## MCP Tool Usage

### Tool audit (this process)

| Tool | Status | Duration (ms) | Input summary | Output summary |
|---|---:|---|---|---|
| `scan_documentation_contracts` | success | 2.08 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `scan_documentation_contracts` | success | 1.57 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.1 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 2 documentation drift row(s) |
| `compare_documentation_drift` | success | 1.37 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 2 documentation drift row(s) |
| `compare_contracts` | success | 0.25 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=0 | passed=True; exit_code=0 |
| `write_report` | success | 0.79 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.93 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.16 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.09 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.08 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.83 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |

### High-level MCP trace

- list_project_files root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' -> 7 files
- write_report path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' success=True

## MCP Resources

Local resource identifiers (payloads via `contractlens/mcp_server/resources.py`):

- `contractlens://repo/tree`
- `contractlens://contracts/frontend/latest`
- `contractlens://contracts/backend/latest`
- `contractlens://mismatches/latest`
- `contractlens://reports/latest`
- `contractlens://runs/latest/trace`

### MCP prompts & server tooling

The ContractLens stdio MCP server registers native **resources** and **prompts** with the installed Python MCP SDK (verified via an internal registration probe).

- **Deterministic prompt templates:** `audit_feature_contract`, `explain_contract_mismatch`, `generate_safe_fix_plan`, `create_pr_review_comment`, `summarize_agent_run`
- **Tool audit log:** `contractlens-runs/latest/tool_audit_log.json`
- **Execution trace artifact:** `contractlens-runs/latest/execution_trace.json`


## LangGraph Execution Trace

- [LangGraph] select_feature: feature='Create Project + Upload File'
- [LangGraph] scan_repository: 7 files
- [LangGraph] apply_git_changed_filter: changed_only=False narrow_openapi=False scan_files=7
- [LangGraph] scan_openapi: 1 spec file(s), 2 operation(s) parsed
- [LangGraph] analyze_frontend: 2 API call(s)
- [CrewAI] CrewAI-shaped deterministic fallback enabled (no LLM)
- [CrewAI] Frontend Analyst running
- [LangGraph] analyze_backend: 2 route(s)
- [CrewAI] Backend Analyst running
- [LangGraph] analyze_auth: frontend_auth_signals=1 backend_auth_signals=2 auth_mismatch_rows=3
- [LangGraph] compare_contracts: 9 mismatch(es) (3 OpenAPI/code drift); risk High=4 Medium=5 Low=0
- [CrewAI] Contract Reviewer running
- [LangGraph] analyze_documentation: doc_claims=7 documentation_drift_rows=2
- [LangGraph] generate_report -> C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md
- [CrewAI] Report Writer running

## Agent Trace

### Structured agent / MCP tool events

| Agent | Role | Tool / step | Input summary | Output summary | ms |
|---|---|---|---|---|---:|
| Frontend Analyst | Extract frontend API expectations | `scan_frontend_contracts` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 frontend API calls | 13.58 |
| Backend Analyst | Extract backend routes/DTOs | `scan_backend_routes` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 backend routes | 15.38 |
| Contract Reviewer | Compare contracts (+ OpenAPI drift) | `compare_contracts` | fe=2 be=2 | 9 mismatch(es); openapi drift=3 | 0.18 |
| Report Writer | Build Markdown audit report | `build_markdown_report` | path=C:\dev\projects\contract-lens\contractlens-reports\cont | 19301 chars | 412.57 |

### Legacy string trace

- [CrewAI] CrewAI-shaped deterministic fallback enabled (no LLM)
- [CrewAI] Frontend Analyst running
- [CrewAI] Backend Analyst running
- [CrewAI] Contract Reviewer running
- [CrewAI] Report Writer running

## Run Artifacts

- Report: `C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md`
- Tool audit log: `contractlens-runs/latest/tool_audit_log.json`
- Execution trace (latest): `contractlens-runs/latest/execution_trace.json`
- Latest run dir: `contractlens-runs/latest`
- Timestamped snapshots: `contractlens-runs/run-YYYYMMDD-HHMMSS/`

## Frontend Expectations

```json
[
  {
    "method": "GET",
    "path": "/api/projects/{id}/detail",
    "source": "frontend/UploadModal.tsx",
    "line": 11,
    "request_fields": [],
    "response_fields": [
      "name"
    ],
    "request_dto": null,
    "response_dto": null,
    "auth": null
  },
  {
    "method": "POST",
    "path": "/api/projects/{id}/files",
    "source": "frontend/projectApi.ts",
    "line": 12,
    "request_fields": [
      "file"
    ],
    "response_fields": [
      "id",
      "thumbnailUrl"
    ],
    "request_dto": null,
    "response_dto": null,
    "auth": null
  }
]
```

## Backend Reality

```json
[
  {
    "method": "POST",
    "path": "/api/projects/{projectId}/models",
    "source": "backend/ProjectsController.cs",
    "line": 14,
    "request_fields": [],
    "response_fields": [],
    "request_dto": "Guid, IFormFile",
    "response_dto": "anonymous {projectId, thumbnail_path}",
    "auth": "Authorize"
  },
  {
    "method": "GET",
    "path": "/api/projects/{projectId}/detail",
    "source": "backend/ProjectsController.cs",
    "line": 25,
    "request_fields": [],
    "response_fields": [],
    "request_dto": "Guid",
    "response_dto": "anonymous {title, created_at}",
    "auth": "Authorize"
  }
]
```

## OpenAPI / Swagger Analysis

- **Detected spec files:** 1 (`openapi.json`)
- **Endpoints parsed from specs:** 2

### Schema / documentation drift findings

- `openapi_vs_code_response_schema` (Medium): Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON.
- `openapi_vs_code_path` (High): Update the published OpenAPI path or change the controller route so spec and implementation agree (add an alias route if both must remain temporarily).
- `openapi_vs_code_response_schema` (Medium): Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON.

### Loader notes

_None._

### Limitations

- Parses OpenAPI 3.x / Swagger 2.0 JSON deterministically; YAML requires PyYAML.
- `$ref` resolution is shallow (`components/schemas` / `definitions` only); external refs are not fetched.
- Server `url` bases are not prefixed onto paths in this MVP.
- Operation pairing uses HTTP method plus path-token similarity; ties break by lexicographic sort.

## Auth / Role Contract Analysis

Heuristic pairing of frontend auth hints (roles, headers, `withCredentials`) with backend `[Authorize]` / `[AllowAnonymous]` plus light Express/FastAPI signals. **Treat as advisory**, not a substitute for policy tests.

- Frontend auth findings: **1**
- Backend auth findings: **2**

| Area | Frontend Assumption | Backend Rule | Risk | Suggestion |
|---|---|---|---|---|
| `backend_requires_auth_frontend_missing_token` | No Authorization/Bearer/withCredentials signal near `frontend/UploadModal.tsx` around API line 11 (GET `/api/projects/{id}/detail` ↔ `backend/ProjectsController.cs`:25) | Backend auth required (roles=authenticated policies=[]) | High | Attach credentials (cookies via `withCredentials`, or `Authorization` bearer token) or expose an explicit `[AllowAnonymous]` route if public. |
| `backend_requires_auth_frontend_missing_token` | No Authorization/Bearer/withCredentials signal near `frontend/projectApi.ts` around API line 12 (POST `/api/projects/{id}/files` ↔ `backend/ProjectsController.cs`:14) | Backend auth required (roles=['Admin', 'Architect'] policies=[]) | High | Attach credentials (cookies via `withCredentials`, or `Authorization` bearer token) or expose an explicit `[AllowAnonymous]` route if public. |
| `frontend_allows_role_backend_blocks` | Frontend hints imply weaker roles ['Client'] (max heuristic rank 20) for POST `/api/projects/{id}/files` ↔ `backend/ProjectsController.cs`:14 | Backend requires elevated roles: Admin, Architect | High | Hide actions from insufficient roles in the UI or loosen `[Authorize(Roles=...)]` if self-service is intentional. |

## Documentation Drift Analysis

Deterministic comparison of Markdown under the analyzed root vs scanned frontend/backend contracts (implementation-first for JSON fields when backend routes exist), with OpenAPI operations included for route pairing. This is advisory static analysis, not a documentation linter.

- Markdown-derived claims: **7**

| Documentation Claim | Actual Implementation | Risk | Suggestion |
|---|---|---|---|
| POST /api/projects/upload (`docs/API.md`:7) | Implementation reference: `POST /api/projects/{projectId}/models` (`backend/ProjectsController.cs` line 14) match_score≈0.50 | Medium | Update docs to the real template path or add a backward-compatible alias route. |
| Docs/setup: `npm run dev` (`docs/API.md`:23) | package.json exists under analyzed root but defines no `scripts` block. | Low | Add a `scripts` section (e.g. `"dev": "..."`) or adjust docs to match the repo. |

## API Contract Table

| Side | Method | Path | Source | Line | Request fields | Response fields | Request DTO | Response DTO | Auth |
|---|---|---|---:|---|---|---|---|---|
| FE | `GET` | `/api/projects/{id}/detail` | `frontend/UploadModal.tsx` | 11 |  | name |  |  |  |
| FE | `POST` | `/api/projects/{id}/files` | `frontend/projectApi.ts` | 12 | file | id, thumbnailUrl |  |  |  |
| BE | `POST` | `/api/projects/{projectId}/models` | `backend/ProjectsController.cs` | 14 |  |  | Guid, IFormFile | anonymous {projectId, thumbnail_path} | Authorize |
| BE | `GET` | `/api/projects/{projectId}/detail` | `backend/ProjectsController.cs` | 25 |  |  | Guid | anonymous {title, created_at} | Authorize |

## Mismatch Report

| Area | Risk | Frontend expects | Backend provides | Suggestion |
|---|---|---|---|---|
| `auth` | Medium | not inferred (MVP static scan) | [Authorize] | Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints. |
| `response_field` | Medium | name | created_at, title | Align JSON property `name` with backend naming or map in the client (backend hints: created_at, title). |
| `path` | High | /api/projects/{id}/files | /api/projects/{projectId}/models | Align the frontend upload path with the backend route (e.g. `/files` vs `/models`) or add a compatibility alias endpoint. |
| `auth` | Medium | not inferred (MVP static scan) | [Authorize] | Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints. |
| `response_field` | High | id | projectId, thumbnail_path | Align JSON property `id` with backend naming or map in the client (backend hints: projectId, thumbnail_path). |
| `response_field` | High | thumbnailUrl | projectId, thumbnail_path | Align JSON property `thumbnailUrl` with backend naming or map in the client (backend hints: projectId, thumbnail_path). |
| `openapi_vs_code_response_schema` | Medium | OpenAPI fields: createdAt, name | Implementation fields: created_at, title; only-in-spec (normalized): name; only-in-code (normalized): title | Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON. |
| `openapi_vs_code_path` | High | OpenAPI POST `/api/projects/{projectId}/files` (`openapi.json`) | Code POST `/api/projects/{projectId}/models` (`backend/ProjectsController.cs`) | Update the published OpenAPI path or change the controller route so spec and implementation agree (add an alias route if both must remain temporarily). |
| `openapi_vs_code_response_schema` | Medium | OpenAPI fields: id, thumbnailUrl | Implementation fields: projectId, thumbnail_path; only-in-spec (normalized): id, thumbnailUrl; only-in-code (normalized): projectId, thumbnail_path | Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON. |

## Risk Assessment

- High: **4**
- Medium: **5**
- Low: **0**
- Unknown: **0**

## Suggested Fix Plan

- **auth** (Medium): Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints.
- **response_field** (Medium): Align JSON property `name` with backend naming or map in the client (backend hints: created_at, title).
- **path** (High): Align the frontend upload path with the backend route (e.g. `/files` vs `/models`) or add a compatibility alias endpoint.
- **auth** (Medium): Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints.
- **response_field** (High): Align JSON property `id` with backend naming or map in the client (backend hints: projectId, thumbnail_path).
- **response_field** (High): Align JSON property `thumbnailUrl` with backend naming or map in the client (backend hints: projectId, thumbnail_path).
- **openapi_vs_code_response_schema** (Medium): Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON.
- **openapi_vs_code_path** (High): Update the published OpenAPI path or change the controller route so spec and implementation agree (add an alias route if both must remain temporarily).
- **openapi_vs_code_response_schema** (Medium): Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON.

## Optional GitHub Issue Draft

**Title (draft):** `Contract drift audit: Create Project + Upload File`

**Body (draft):**

This issue was drafted from a ContractLens AI run for feature `Create Project + Upload File`.

### Findings

- **[Medium] auth**: Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints.
- **[Medium] response_field**: Align JSON property `name` with backend naming or map in the client (backend hints: created_at, title).
- **[High] path**: Align the frontend upload path with the backend route (e.g. `/files` vs `/models`) or add a compatibility alias endpoint.
- **[Medium] auth**: Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints.
- **[High] response_field**: Align JSON property `id` with backend naming or map in the client (backend hints: projectId, thumbnail_path).
- **[High] response_field**: Align JSON property `thumbnailUrl` with backend naming or map in the client (backend hints: projectId, thumbnail_path).
- **[Medium] openapi_vs_code_response_schema**: Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON.
- **[High] openapi_vs_code_path**: Update the published OpenAPI path or change the controller route so spec and implementation agree (add an alias route if both must remain temporarily).
- **[Medium] openapi_vs_code_response_schema**: Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties / configure serializers so documentation reflects runtime JSON.

### Next steps

- Align paths/DTOs listed above, or document intentional differences.
- Re-run: `python -m contractlens.main --feature "..." --root <repo> --verbose`


## Current Limitations

- Static analysis is heuristic-based.
- Complex dynamic API paths may not be fully resolved.
- Response field extraction is limited in the MVP.
- **Git changed-only:** uses local `git diff --name-only` plus cached names when enabled; **untracked files are omitted** unless staged. Requires `git` on `PATH`.
- **OpenAPI:** shallow `$ref` resolution; server URL prefixes not applied to paths; YAML needs PyYAML.
- **MCP-first:** tools are audited locally; resources expose latest artifacts under `contractlens-runs/latest/`.
- **Agents:** With `OPENAI_API_KEY` (and without `--deterministic-agents`), CrewAI runs LLM agents that still call ContractLens tools. Otherwise steps stay deterministic but MCP-backed.
- **MCP stdio server:** exposes tools always; native resources/prompts only when the SDK registration probe succeeds — otherwise use helper tools listed in the MCP tooling section.
- **Auth / role pairing:** role ranks and token detection are regex/heuristic; policies are not expanded to roles.
- **Documentation drift:** Markdown-only heuristics; fenced JSON blocks drive property extraction; shallow `package.json` script checks only cover discovered manifests.
- Permission boundaries apply to filesystem tools.
- The sample project is intentionally tiny so the demo stays reproducible.
