# ContractLens AI Report

## Feature

Create Project + Upload File

## Scan Summary

- Root: `C:\dev\projects\contract-lens\examples\sample_project`
- Files discovered: **5**

## MCP Tool Usage

### Tool audit (this process)

| Tool | Status | Duration (ms) | Summary |
|---|---:|---:|---|
| `scan_frontend_contracts` | success | 5.36 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_backend_routes` | success | 3.91 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `compare_contracts` | success | 0.56 | fe=2 be=2 |
| `list_project_files` | success | 1.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_frontend_contracts` | success | 2.62 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_backend_routes` | success | 3.67 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `compare_contracts` | success | 0.12 | fe=2 be=2 |
| `write_report` | success | 0.66 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=9 |
| `write_report` | success | 0.68 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=9 |
| `generate_contract_report` | success | 1150.92 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `list_project_files` | success | 1.08 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_frontend_contracts` | success | 2.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_backend_routes` | success | 4.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `compare_contracts` | success | 0.29 | fe=2 be=2 |
| `write_report` | success | 0.96 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=1 |
| `write_report` | success | 0.79 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=1 |
| `list_project_files` | success | 1.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_frontend_contracts` | success | 3.01 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_backend_routes` | success | 4.27 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `compare_contracts` | success | 0.37 | fe=2 be=2 |
| `list_project_files` | success | 0.98 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_frontend_contracts` | success | 2.23 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_backend_routes` | success | 3.3 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `compare_contracts` | success | 0.12 | fe=2 be=2 |
| `write_report` | success | 0.87 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=1 |
| `write_report` | success | 0.66 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=1 |
| `generate_contract_report` | success | 790.42 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `get_latest_report` | success | 10.25 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' |
| `list_project_files` | success | 1.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_frontend_contracts` | success | 3.36 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `scan_backend_routes` | success | 3.85 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' |
| `compare_contracts` | success | 0.32 | fe=2 be=2 |
| `write_report` | success | 0.73 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' bytes=1 |

### High-level MCP trace

- list_project_files root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' -> 5 files
- write_report path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-report-create-project-upload-file.md' success=True

## MCP Resources

Local resource identifiers (payloads via `contractlens/mcp_server/resources.py`):

- `contractlens://repo/tree`
- `contractlens://contracts/frontend/latest`
- `contractlens://contracts/backend/latest`
- `contractlens://mismatches/latest`
- `contractlens://reports/latest`
- `contractlens://runs/latest/trace`

## LangGraph Execution Trace

- [LangGraph] select_feature: feature='Create Project + Upload File'
- [LangGraph] scan_repository: 5 files
- [LangGraph] analyze_frontend: 2 API call(s)
- [CrewAI] CrewAI-shaped deterministic fallback enabled (no LLM)
- [CrewAI] Frontend Analyst running
- [LangGraph] analyze_backend: 2 route(s)
- [CrewAI] Backend Analyst running
- [LangGraph] compare_contracts: 6 mismatch(es); risk High=3 Medium=3 Low=0
- [CrewAI] Contract Reviewer running
- [LangGraph] generate_report -> C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md
- [CrewAI] Report Writer running

## Agent Trace

### Structured agent / MCP tool events

| Agent | Role | Tool / step | Input summary | Output summary | ms |
|---|---|---|---|---|---:|
| Frontend Analyst | Extract frontend API expectations | `scan_frontend_contracts` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 frontend API calls | 14.75 |
| Backend Analyst | Extract backend routes/DTOs | `scan_backend_routes` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 backend routes | 13.88 |
| Contract Reviewer | Compare frontend vs backend contracts | `compare_contracts` | fe=2 be=2 | 6 mismatch(es) | 10.58 |
| Report Writer | Build Markdown audit report | `build_markdown_report` | path=C:\dev\projects\contract-lens\contractlens-reports\cont | 12312 chars | 11.96 |

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
    "line": 10,
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
    "line": 10,
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
    "line": 12,
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
    "line": 23,
    "request_fields": [],
    "response_fields": [],
    "request_dto": "Guid",
    "response_dto": "anonymous {title, created_at}",
    "auth": "Authorize"
  }
]
```

## API Contract Table

| Side | Method | Path | Source | Line | Request fields | Response fields | Request DTO | Response DTO | Auth |
|---|---|---|---:|---|---|---|---|---|
| FE | `GET` | `/api/projects/{id}/detail` | `frontend/UploadModal.tsx` | 10 |  | name |  |  |  |
| FE | `POST` | `/api/projects/{id}/files` | `frontend/projectApi.ts` | 10 | file | id, thumbnailUrl |  |  |  |
| BE | `POST` | `/api/projects/{projectId}/models` | `backend/ProjectsController.cs` | 12 |  |  | Guid, IFormFile | anonymous {projectId, thumbnail_path} | Authorize |
| BE | `GET` | `/api/projects/{projectId}/detail` | `backend/ProjectsController.cs` | 23 |  |  | Guid | anonymous {title, created_at} | Authorize |

## Mismatch Report

| Area | Risk | Frontend expects | Backend provides | Suggestion |
|---|---|---|---|---|
| `auth` | Medium | not inferred (MVP static scan) | [Authorize] | Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints. |
| `response_field` | Medium | name | created_at, title | Align JSON property `name` with backend naming or map in the client (backend hints: created_at, title). |
| `path` | High | /api/projects/{id}/files | /api/projects/{projectId}/models | Align the frontend upload path with the backend route (e.g. `/files` vs `/models`) or add a compatibility alias endpoint. |
| `auth` | Medium | not inferred (MVP static scan) | [Authorize] | Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints. |
| `response_field` | High | id | projectId, thumbnail_path | Align JSON property `id` with backend naming or map in the client (backend hints: projectId, thumbnail_path). |
| `response_field` | High | thumbnailUrl | projectId, thumbnail_path | Align JSON property `thumbnailUrl` with backend naming or map in the client (backend hints: projectId, thumbnail_path). |

## Risk Assessment

- High: **3**
- Medium: **3**
- Low: **0**
- Unknown: **0**

## Suggested Fix Plan

- **auth** (Medium): Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints.
- **response_field** (Medium): Align JSON property `name` with backend naming or map in the client (backend hints: created_at, title).
- **path** (High): Align the frontend upload path with the backend route (e.g. `/files` vs `/models`) or add a compatibility alias endpoint.
- **auth** (Medium): Ensure the frontend obtains and sends credentials (cookies/Bearer token) required by authorized endpoints.
- **response_field** (High): Align JSON property `id` with backend naming or map in the client (backend hints: projectId, thumbnail_path).
- **response_field** (High): Align JSON property `thumbnailUrl` with backend naming or map in the client (backend hints: projectId, thumbnail_path).

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

### Next steps

- Align paths/DTOs listed above, or document intentional differences.
- Re-run: `python -m contractlens.main --feature "..." --root <repo> --verbose`


## Current Limitations

- Static analysis is heuristic-based.
- Complex dynamic API paths may not be fully resolved.
- Response field extraction is limited in the MVP.
- **MCP-first:** tools are audited locally; resources expose latest artifacts under `contractlens-runs/latest/`.
- **Agents:** With `OPENAI_API_KEY` (and without `--deterministic-agents`), CrewAI runs LLM agents that still call ContractLens tools. Otherwise steps stay deterministic but MCP-backed.
- Stdio MCP server requires the `mcp` package; permission boundaries apply to filesystem tools.
- The sample project is intentionally tiny so the demo stays reproducible.
