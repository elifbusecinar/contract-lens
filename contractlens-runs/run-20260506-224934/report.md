# ContractLens AI Report

## Feature

Create Project + Upload File

## Scan Summary

- Root: `C:\dev\projects\contract-lens\examples\sample_project`
- Files discovered: **5**

## Run Summary

- **Run ID:** `run-20260506-224934`
- **Frontend contracts detected:** 2
- **Backend routes detected:** 2
- **Mismatch count:** 6
- **High-risk mismatches:** 3
- **Report path:** `C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md`
- **Audit log:** `contractlens-runs/latest/tool_audit_log.json`
- **Execution trace:** `contractlens-runs/latest/execution_trace.json`
- **Run summary artifact:** `contractlens-runs/latest/run_summary.json`


## MCP Capability Summary

- **Manifest server version:** `0.4.0`
- **Tools:** 15
- **Resources:** 6
- **Prompts:** 5
- **SDK registration:** active (native resources/prompts probe succeeded)
- **Permission model:** Reads confined to the selected repo root; writes require explicit `allow_write`; path traversal blocked; heavy folders (`node_modules`, `.git`, build outputs, virtualenvs) ignored.


## MCP Tool Usage

### Tool audit (this process)

| Tool | Status | Duration (ms) | Input summary | Output summary |
|---|---:|---|---|---|
| `scan_frontend_contracts` | success | 5.36 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.91 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.56 | fe=2 be=2 | — |
| `list_project_files` | success | 1.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.62 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.67 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.12 | fe=2 be=2 | — |
| `write_report` | success | 0.66 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.68 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 1150.92 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `list_project_files` | success | 1.08 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 4.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.29 | fe=2 be=2 | — |
| `write_report` | success | 0.96 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.79 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `list_project_files` | success | 1.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 3.01 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 4.27 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.37 | fe=2 be=2 | — |
| `list_project_files` | success | 0.98 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.23 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.3 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.12 | fe=2 be=2 | — |
| `write_report` | success | 0.87 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.66 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 790.42 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `get_latest_report` | success | 10.25 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | — |
| `list_project_files` | success | 1.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 3.36 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.85 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.32 | fe=2 be=2 | — |
| `write_report` | success | 0.73 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.76 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `explain_mismatch` | success | 0.03 | area='path' | — |
| `scan_frontend_contracts` | success | 5.46 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.87 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.36 | fe=2 be=2 | — |
| `list_project_files` | success | 0.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.8 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.21 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.14 | fe=2 be=2 | — |
| `write_report` | success | 0.8 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.91 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 1301.45 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `explain_mismatch` | success | 0.03 | area='path' | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `list_project_files` | success | 0.86 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `list_project_files` | success | 1.07 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 3.22 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 4.3 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.35 | fe=2 be=2 | — |
| `list_project_files` | success | 0.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.25 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.12 | fe=2 be=2 | — |
| `write_report` | success | 0.99 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.88 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 1093.53 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `get_latest_report` | success | 11.35 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `read_mcp_resource` | success | 10.57 | uri='contractlens://reports/latest' | — |
| `read_mcp_resource` | success | 0.52 | uri='contractlens://reports/latest' | — |
| `list_mcp_prompts` | success | 0.01 |  | — |
| `list_mcp_prompts` | success | 0.0 |  | — |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | — |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | — |
| `list_project_files` | success | 0.97 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.9 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.66 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.32 | fe=2 be=2 | — |
| `write_report` | success | 0.93 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.8 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `explain_mismatch` | success | 0.03 | area='path' | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `read_mcp_resource` | success | 1.14 | uri='contractlens://reports/latest' | — |
| `list_mcp_prompts` | success | 0.01 |  | — |
| `get_mcp_prompt` | success | 0.05 | name='explain_contract_mismatch' | — |
| `list_project_files` | success | 1.08 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.97 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.68 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.43 | fe=2 be=2 | — |
| `list_project_files` | success | 1.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.24 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.2 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.13 | fe=2 be=2 | — |
| `write_report` | success | 0.7 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.63 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 1117.56 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `scan_frontend_contracts` | success | 3.5 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.37 | fe=2 be=2 | — |
| `list_project_files` | success | 1.13 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.52 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.38 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.12 | fe=2 be=2 | — |
| `write_report` | success | 0.76 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.68 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 1149.78 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `explain_mismatch` | success | 0.03 | area='path' | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `read_mcp_resource` | success | 0.9 | uri='contractlens://reports/latest' | — |
| `list_mcp_prompts` | success | 0.01 |  | — |
| `get_mcp_prompt` | success | 0.03 | name='explain_contract_mismatch' | — |
| `list_project_files` | success | 1.03 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `list_project_files` | success | 1.23 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `list_project_files` | success | 0.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.82 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.81 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.36 | fe=2 be=2 | — |
| `list_project_files` | success | 0.9 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 2.49 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.37 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.13 | fe=2 be=2 | — |
| `write_report` | success | 0.74 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 1.06 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `generate_contract_report` | success | 1094.62 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | — |
| `get_latest_report` | success | 10.39 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `list_mcp_resources` | success | 0.01 |  | — |
| `read_mcp_resource` | success | 9.55 | uri='contractlens://reports/latest' | — |
| `read_mcp_resource` | success | 0.56 | uri='contractlens://reports/latest' | — |
| `list_mcp_prompts` | success | 0.01 |  | — |
| `list_mcp_prompts` | success | 0.0 |  | — |
| `get_mcp_prompt` | success | 0.03 | name='explain_contract_mismatch' | — |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | — |
| `list_project_files` | success | 0.97 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_frontend_contracts` | success | 3.34 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `scan_backend_routes` | success | 3.91 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | — |
| `compare_contracts` | success | 0.32 | fe=2 be=2 | — |
| `write_report` | success | 0.69 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `write_report` | success | 0.66 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | — |
| `scan_frontend_contracts` | success | 11.75 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 10.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 1.51 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `list_project_files` | success | 3.49 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `scan_frontend_contracts` | success | 5.76 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 6.56 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.26 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `write_report` | success | 4.39 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.99 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 3959.03 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=6; report=contractlens-report-create-project-upload-file.md |
| `explain_mismatch` | success | 0.06 | area='path' | Returned explanation + suggested_fix |
| `list_mcp_resources` | success | 0.01 |  | 6 resource URI(s) |
| `read_mcp_resource` | success | 2.68 | uri='contractlens://reports/latest' | status=ok; body 24560 character(s) |
| `list_mcp_prompts` | success | 0.02 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.06 | name='explain_contract_mismatch' | Prompt string 230 character(s) |
| `list_project_files` | success | 2.29 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `list_project_files` | success | 2.36 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `list_project_files` | success | 3.41 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `scan_frontend_contracts` | success | 8.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 15.29 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 1.28 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `list_project_files` | success | 2.54 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `scan_frontend_contracts` | success | 6.26 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 10.62 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.24 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `write_report` | success | 2.03 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 3.89 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 2883.38 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=6; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 3.44 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 26758 character(s) |
| `list_mcp_resources` | success | 0.03 |  | 6 resource URI(s) |
| `list_mcp_resources` | success | 0.02 |  | 6 resource URI(s) |
| `read_mcp_resource` | success | 19.36 | uri='contractlens://reports/latest' | status=ok; body 26758 character(s) |
| `read_mcp_resource` | success | 1.78 | uri='contractlens://reports/latest' | status=ok; body 26758 character(s) |
| `list_mcp_prompts` | success | 0.02 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.1 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.12 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `list_project_files` | success | 2.68 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `scan_frontend_contracts` | success | 9.28 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 10.19 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.71 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `write_report` | success | 4.91 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 4.66 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `explain_mismatch` | success | 0.02 | area='path' | Returned explanation + suggested_fix |
| `scan_frontend_contracts` | success | 3.27 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.07 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.36 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `list_project_files` | success | 0.91 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `scan_frontend_contracts` | success | 2.78 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 3.82 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.13 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `write_report` | success | 0.71 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.89 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1285.08 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=6; report=contractlens-report-create-project-upload-file.md |
| `explain_mismatch` | success | 0.04 | area='path' | Returned explanation + suggested_fix |
| `list_mcp_resources` | success | 0.01 |  | 6 resource URI(s) |
| `read_mcp_resource` | success | 1.53 | uri='contractlens://reports/latest' | status=ok; body 29906 character(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.03 | name='explain_contract_mismatch' | Prompt string 230 character(s) |
| `list_project_files` | success | 1.12 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `explain_mismatch` | success | 0.02 | area='path' | Returned explanation + suggested_fix |
| `list_project_files` | success | 1.05 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 5 file path(s) |
| `scan_frontend_contracts` | success | 4.44 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.02 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.36 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `write_report` | success | 1.44 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |

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

### MCP prompts & server tooling

The ContractLens stdio MCP server registers native **resources** and **prompts** with the installed Python MCP SDK (verified via an internal registration probe).

- **Deterministic prompt templates:** `audit_feature_contract`, `explain_contract_mismatch`, `generate_safe_fix_plan`, `create_pr_review_comment`, `summarize_agent_run`
- **Tool audit log:** `contractlens-runs/latest/tool_audit_log.json`
- **Execution trace artifact:** `contractlens-runs/latest/execution_trace.json`


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
| Frontend Analyst | Extract frontend API expectations | `scan_frontend_contracts` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 frontend API calls | 21.25 |
| Backend Analyst | Extract backend routes/DTOs | `scan_backend_routes` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 backend routes | 16.0 |
| Contract Reviewer | Compare frontend vs backend contracts | `compare_contracts` | fe=2 be=2 | 6 mismatch(es) | 12.16 |
| Report Writer | Build Markdown audit report | `build_markdown_report` | path=C:\dev\projects\contract-lens\contractlens-reports\cont | 31252 chars | 396.79 |

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
- **MCP stdio server:** exposes tools always; native resources/prompts only when the SDK registration probe succeeds — otherwise use helper tools listed in the MCP tooling section.
- Permission boundaries apply to filesystem tools.
- The sample project is intentionally tiny so the demo stays reproducible.
