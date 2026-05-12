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

- **Run ID:** `run-20260512-003744`
- **Frontend contracts detected:** 2
- **Backend routes detected:** 2
- **OpenAPI spec files detected:** 1
- **OpenAPI operations parsed:** 2
- **OpenAPI/code drift mismatches:** 3
- **Mismatch count (total):** 9
- **Auth / role drift rows:** 3
- **Documentation claims extracted:** 7
- **Documentation drift rows:** 3
- **High-risk mismatches:** 4
- **Report path:** `C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md`
- **Audit log:** `contractlens-runs/latest/tool_audit_log.json`
- **Execution trace:** `contractlens-runs/latest/execution_trace.json`
- **Run summary artifact:** `contractlens-runs/latest/run_summary.json`


## Runtime HTTP Probe

_No runtime probe URL configured._ Set `probe_base_url` in `contractlens.toml` / `contractlens.yaml` or `CONTRACTLENS_PROBE_BASE_URL`. When set, ContractLens performs a single **GET** before the report is finalized and records the outcome below (response body is not analyzed).

## MCP Capability Summary

- **Manifest server version:** `0.4.4`
- **Tools:** 29
- **Resources:** 7
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
| `write_report` | success | 1.5 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1293.22 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 10.47 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 19657 character(s) |
| `list_mcp_resources` | success | 0.01 |  | 6 resource URI(s) |
| `list_mcp_resources` | success | 0.01 |  | 6 resource URI(s) |
| `read_mcp_resource` | success | 10.68 | uri='contractlens://reports/latest' | status=ok; body 19657 character(s) |
| `read_mcp_resource` | success | 0.52 | uri='contractlens://reports/latest' | status=ok; body 19657 character(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.03 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.05 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `scan_frontend_contracts` | success | 4.71 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.46 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.09 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 3.21 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.24 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 19.83 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 2.05 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 9.83 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.04 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.12 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 4 documentation drift row(s) |
| `list_project_files` | success | 1.24 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.75 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.53 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.72 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.11 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1227.4 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.98 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `list_project_files` | success | 1.26 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `find_openapi_specs` | success | 22.37 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `find_openapi_specs` | success | 1.8 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `get_changed_files` | success | 41.4 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `get_changed_files` | success | 36.54 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `parse_openapi_contracts` | success | 1.85 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `parse_openapi_contracts` | success | 1.67 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 8.68 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `compare_backend_to_openapi` | success | 7.47 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_frontend_contracts` | success | 4.44 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.73 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `scan_frontend_auth` | success | 2.14 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_frontend_auth` | success | 1.99 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.43 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `scan_backend_auth` | success | 2.7 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.29 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `compare_auth_contracts` | success | 0.15 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `scan_documentation_contracts` | success | 2.22 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `scan_documentation_contracts` | success | 1.87 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.18 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 4 documentation drift row(s) |
| `compare_documentation_drift` | success | 1.02 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 4 documentation drift row(s) |
| `compare_contracts` | success | 0.26 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=0 | passed=True; exit_code=0 |
| `list_project_files` | success | 1.47 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.76 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.44 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.99 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.25 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1238.15 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 11.68 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 27956 character(s) |
| `list_mcp_resources` | success | 0.01 |  | 6 resource URI(s) |
| `list_mcp_resources` | success | 0.01 |  | 6 resource URI(s) |
| `read_mcp_resource` | success | 10.73 | uri='contractlens://reports/latest' | status=ok; body 27956 character(s) |
| `read_mcp_resource` | success | 0.56 | uri='contractlens://reports/latest' | status=ok; body 27956 character(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.03 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.05 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `scan_frontend_contracts` | success | 3.47 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.89 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.41 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.04 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.07 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.17 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 20.05 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.79 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 7.03 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 1.78 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.81 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.16 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.87 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.8 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.27 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1237.73 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.3 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.9 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.26 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 1.04 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.75 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `scan_frontend_contracts` | success | 8.47 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 8.59 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.42 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 3.41 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.54 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.71 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 33.19 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 7.73 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.32 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.77 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.34 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.22 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.67 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 1.18 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.16 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1958.81 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.62 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 4.54 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 6.4 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 1.11 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.21 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 2.32 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `list_project_files` | success | 1.52 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `find_openapi_specs` | success | 24.04 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `find_openapi_specs` | success | 2.17 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `get_changed_files` | success | 135.79 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `get_changed_files` | success | 137.32 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `parse_openapi_contracts` | success | 2.56 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `parse_openapi_contracts` | success | 2.51 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 8.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `compare_backend_to_openapi` | success | 7.89 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_frontend_contracts` | success | 6.29 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.73 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `scan_frontend_auth` | success | 2.82 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_frontend_auth` | success | 2.75 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.48 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `scan_backend_auth` | success | 2.65 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.49 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `compare_auth_contracts` | success | 0.33 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `scan_documentation_contracts` | success | 3.07 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `scan_documentation_contracts` | success | 3.07 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.55 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_documentation_drift` | success | 1.14 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_contracts` | success | 0.29 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `evaluate_ci_gate` | success | 0.03 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=0 | passed=True; exit_code=0 |
| `list_project_files` | success | 1.85 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.75 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.89 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.98 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.98 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1502.11 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 9.6 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 39885 character(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `read_mcp_resource` | success | 12.18 | uri='contractlens://reports/latest' | status=ok; body 39885 character(s) |
| `read_mcp_resource` | success | 0.68 | uri='contractlens://reports/latest' | status=ok; body 39885 character(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.05 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `explain_mismatch` | success | 0.04 | area='path' | Returned explanation + suggested_fix |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `read_mcp_resource` | success | 1.47 | uri='contractlens://reports/latest' | status=ok; body 39885 character(s) |
| `read_mcp_resource` | success | 1.12 | uri='contractlens://runs/latest/summary' | status=ok |
| `list_runs` | success | 3.09 | limit=10 | 10 stamped run(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 230 character(s) |
| `list_project_files` | success | 1.8 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 5.17 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.24 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.38 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.6 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.43 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.47 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 24.54 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.9 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 5.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.09 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.1 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.48 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.82 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.88 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1451.25 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.27 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.47 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.13 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.98 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.9 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.39 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.24 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.09 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.82 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.74 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 2.27 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.html |
| `list_project_files` | success | 1.21 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `list_project_files` | success | 1.59 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `find_openapi_specs` | success | 18.78 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `find_openapi_specs` | success | 1.55 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `get_changed_files` | success | 100.59 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `get_changed_files` | success | 112.4 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `parse_openapi_contracts` | success | 2.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `parse_openapi_contracts` | success | 1.71 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 7.2 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `compare_backend_to_openapi` | success | 6.73 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_frontend_contracts` | success | 3.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.72 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `scan_frontend_auth` | success | 2.12 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_frontend_auth` | success | 2.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.13 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `scan_backend_auth` | success | 2.09 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.23 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `compare_auth_contracts` | success | 0.14 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `scan_documentation_contracts` | success | 1.95 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `scan_documentation_contracts` | success | 1.8 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.4 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_documentation_drift` | success | 0.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_contracts` | success | 0.28 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=0 | passed=True; exit_code=0 |
| `list_project_files` | success | 1.1 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.36 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.38 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.9 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.79 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1106.63 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 12.11 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 49931 character(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `read_mcp_resource` | success | 10.67 | uri='contractlens://reports/latest' | status=ok; body 49931 character(s) |
| `read_mcp_resource` | success | 0.59 | uri='contractlens://reports/latest' | status=ok; body 49931 character(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `scan_frontend_contracts` | success | 3.91 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.49 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.37 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.7 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.19 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 19.86 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 2.78 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 6.41 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 1.78 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.56 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.04 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.67 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 1.3 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.18 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1164.09 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.34 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.81 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.85 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.19 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.19 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `list_project_files` | success | 1.19 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `find_openapi_specs` | success | 23.69 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `find_openapi_specs` | success | 1.31 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `get_changed_files` | success | 106.37 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `get_changed_files` | success | 48.6 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `parse_openapi_contracts` | success | 1.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `parse_openapi_contracts` | success | 1.8 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 8.96 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `compare_backend_to_openapi` | success | 6.44 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_frontend_contracts` | success | 3.34 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.54 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `scan_frontend_auth` | success | 2.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_frontend_auth` | success | 2.66 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `scan_backend_auth` | success | 2.58 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.18 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `compare_auth_contracts` | success | 0.14 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `scan_documentation_contracts` | success | 1.76 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `scan_documentation_contracts` | success | 2.21 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.09 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_documentation_drift` | success | 0.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_contracts` | success | 0.27 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=0 | passed=True; exit_code=0 |
| `list_project_files` | success | 1.21 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.49 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.7 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.96 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.82 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1177.5 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 12.08 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 58320 character(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `read_mcp_resource` | success | 11.12 | uri='contractlens://reports/latest' | status=ok; body 58320 character(s) |
| `read_mcp_resource` | success | 0.61 | uri='contractlens://reports/latest' | status=ok; body 58320 character(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.05 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `scan_frontend_contracts` | success | 39.03 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 42.53 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.38 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.26 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.21 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 48.67 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.64 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 6.4 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.37 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.48 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.31 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.12 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 1.24 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.84 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 2360.5 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.25 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 4.03 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.9 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.93 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.05 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `list_project_files` | success | 1.2 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `find_openapi_specs` | success | 17.47 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `find_openapi_specs` | success | 1.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `get_changed_files` | success | 39.08 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `get_changed_files` | success | 38.42 | root='C:\\dev\\projects\\contract-lens' include_cached=True | 0 path(s); git=False |
| `parse_openapi_contracts` | success | 1.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `parse_openapi_contracts` | success | 1.71 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 7.01 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `compare_backend_to_openapi` | success | 6.26 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_frontend_contracts` | success | 3.57 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.68 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `scan_frontend_auth` | success | 2.48 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_frontend_auth` | success | 2.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.42 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `scan_backend_auth` | success | 2.6 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.17 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `compare_auth_contracts` | success | 0.14 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `scan_documentation_contracts` | success | 2.14 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `scan_documentation_contracts` | success | 1.55 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.45 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_documentation_drift` | success | 0.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `compare_contracts` | success | 0.26 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.01 | fail_on='High' n=6 | passed=False; exit_code=1 |
| `evaluate_ci_gate` | success | 0.02 | fail_on='High' n=0 | passed=True; exit_code=0 |
| `list_project_files` | success | 1.91 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.06 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.7 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.89 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 1.01 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1366.67 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `get_latest_report` | success | 10.89 | reports_dir='C:\\dev\\projects\\contract-lens\\contractlens-reports' | Latest report body 66710 character(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `read_mcp_resource` | success | 10.42 | uri='contractlens://reports/latest' | status=ok; body 66710 character(s) |
| `read_mcp_resource` | success | 0.58 | uri='contractlens://reports/latest' | status=ok; body 66710 character(s) |
| `list_mcp_prompts` | success | 0.02 |  | 5 prompt template(s) |
| `list_mcp_prompts` | success | 0.0 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.03 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 244 character(s) |
| `scan_frontend_contracts` | success | 3.18 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.68 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.34 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `find_openapi_specs` | success | 19.81 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `scan_frontend_contracts` | success | 3.2 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.57 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.41 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `find_openapi_specs` | success | 19.99 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `explain_mismatch` | success | 0.04 | area='path' | Returned explanation + suggested_fix |
| `list_mcp_resources` | success | 0.01 |  | 7 resource URI(s) |
| `read_mcp_resource` | success | 1.57 | uri='contractlens://reports/latest' | status=ok; body 66710 character(s) |
| `read_mcp_resource` | success | 0.54 | uri='contractlens://runs/latest/summary' | status=ok |
| `list_runs` | success | 3.49 | limit=10 | 10 stamped run(s) |
| `list_mcp_prompts` | success | 0.01 |  | 5 prompt template(s) |
| `get_mcp_prompt` | success | 0.04 | name='explain_contract_mismatch' | Prompt string 230 character(s) |
| `list_project_files` | success | 1.38 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 3.16 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.6 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.35 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `find_openapi_specs` | success | 19.53 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `scan_frontend_contracts` | success | 3.65 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.58 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.35 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 1.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.8 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.16 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 20.54 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.68 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 5.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.63 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.12 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.33 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.45 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.23 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.85 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.78 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1267.79 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `list_project_files` | success | 1.25 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.95 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.14 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 1.62 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 2.1 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `scan_frontend_contracts` | success | 3.58 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.66 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.36 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `find_openapi_specs` | success | 20.84 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `scan_frontend_contracts` | success | 3.24 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.69 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.51 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.25 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 1.94 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.18 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 17.96 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.62 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 5.84 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.01 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.16 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.15 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.27 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 3.81 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.99 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.78 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1228.61 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `scan_frontend_contracts` | success | 3.32 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 4 contract(s) |
| `scan_backend_routes` | success | 4.92 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.54 | fe=4 be=2 | 12 mismatch(es); High=6 |
| `find_openapi_specs` | success | 17.75 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `scan_frontend_contracts` | success | 3.84 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.45 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.35 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `find_openapi_specs` | success | 19.63 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `scan_frontend_contracts` | success | 4.51 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 6.0 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.36 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.49 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.38 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.34 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 20.79 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 2.25 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 6.58 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.41 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.11 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.21 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.74 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.62 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.95 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `write_report` | success | 0.93 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |
| `generate_contract_report` | success | 1339.96 | feature='Create Project + Upload File' root='C:\\dev\\projects\\contract-lens\\e | mismatch_count=9; report=contractlens-report-create-project-upload-file.md |
| `scan_frontend_contracts` | success | 3.78 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.38 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.37 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `find_openapi_specs` | success | 22.18 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `scan_frontend_contracts` | success | 3.45 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 5.23 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `compare_contracts` | success | 0.4 | fe=2 be=2 | 6 mismatch(es); High=3 |
| `scan_frontend_auth` | success | 2.07 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 auth finding(s) |
| `scan_backend_auth` | success | 2.16 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 auth finding(s) |
| `compare_auth_contracts` | success | 0.17 | fe_contracts=2 be_contracts=2 fe_auth=1 be_auth=2 | 3 auth mismatch(es) |
| `find_openapi_specs` | success | 18.63 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 1 spec path(s); yaml_supported=True |
| `parse_openapi_contracts` | success | 1.66 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 operation(s); specs=1 |
| `compare_backend_to_openapi` | success | 6.18 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' backend_rows=0 | 3 openapi drift mismatch(es); High=1 |
| `scan_documentation_contracts` | success | 2.08 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 doc claim(s) |
| `compare_documentation_drift` | success | 1.17 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' claims=7 fe=2  | 3 documentation drift row(s) |
| `list_project_files` | success | 1.16 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 7 file path(s) |
| `scan_frontend_contracts` | success | 2.55 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 contract(s) |
| `scan_backend_routes` | success | 4.1 | root='C:\\dev\\projects\\contract-lens\\examples\\sample_project' | 2 route(s) |
| `write_report` | success | 0.91 | path='C:\\dev\\projects\\contract-lens\\contractlens-reports\\contractlens-repor | Wrote OK -> contractlens-report-create-project-upload-file.md |

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
- `contractlens://runs/latest/summary`

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
- [LangGraph] analyze_documentation: doc_claims=7 documentation_drift_rows=3
- [LangGraph] generate_report -> C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md
- [CrewAI] Report Writer running

## Agent Trace

### Structured agent / MCP tool events

| Agent | Role | Tool / step | Input summary | Output summary | ms |
|---|---|---|---|---|---:|
| Frontend Analyst | Extract frontend API expectations | `scan_frontend_contracts` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 frontend API calls | 14.53 |
| Backend Analyst | Extract backend routes/DTOs | `scan_backend_routes` | root=C:\dev\projects\contract-lens\examples\sample_project | Detected 2 backend routes | 15.97 |
| Contract Reviewer | Compare contracts (+ OpenAPI drift) | `compare_contracts` | fe=2 be=2 | 9 mismatch(es); openapi drift=3 | 0.17 |
| Report Writer | Build Markdown audit report | `build_markdown_report` | path=C:\dev\projects\contract-lens\contractlens-reports\cont | 83359 chars | 412.13 |

### Legacy string trace

- [CrewAI] CrewAI-shaped deterministic fallback enabled (no LLM)
- [CrewAI] Frontend Analyst running
- [CrewAI] Backend Analyst running
- [CrewAI] Contract Reviewer running
- [CrewAI] Report Writer running

## Run Artifacts

- **Current run id:** `run-20260512-003744`
- **Primary report:** `C:\dev\projects\contract-lens\contractlens-reports\contractlens-report-create-project-upload-file.md`
- **Latest snapshot dir:** `contractlens-runs/latest/`
- **Stamped copies:** `contractlens-runs/run-YYYYMMDD-HHMMSS/` (same filenames as `latest/`)
- **Standard artifacts:**
  - `run_summary.json` — run id, timing (`duration_ms`), counts, `report_path`
  - `tool_audit_log.json` — MCP tool audit entries for this process
  - `execution_trace.json` — LangGraph / sequential workflow trace lines
  - `agent_trace.json` — CrewAI-style legacy string trace lines
  - `frontend_contracts.json` / `backend_contracts.json` / `mismatches.json`
  - `report.md` — mirrored Markdown audit written alongside `contractlens-reports/` output
- **MCP:** `list_runs`, `get_run_summary`, `get_run_artifact`; resources `contractlens://runs/latest/summary` and `contractlens://runs/<run_id>/summary`.

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

Deterministic comparison of Markdown under the analyzed root vs scanned frontend/backend/OpenAPI contracts for **routes**, while **JSON property claims** use **backend-only** payload hints when backend routes exist (so client/OpenAPI optimism does not mask stale docs). Shallow `package.json` script checks apply when manifests exist. This is advisory static analysis, not a documentation linter.

- Markdown-derived claims: **7**

| Documentation Claim | Actual Implementation | Risk | Suggestion |
|---|---|---|---|
| POST /api/projects/upload (`docs/API.md`:7) | Implementation reference: `POST /api/projects/{projectId}/models` (`backend/ProjectsController.cs` line 14) match_score≈0.50 | Medium | Update docs to the real template path or add a backward-compatible alias route. |
| Docs/json mention field `thumbnailUrl` (known mismatch vs `thumbnail_path`) (`docs/API.md`:14) | Scanned contracts carry `thumbnail_path` but not `thumbnailUrl` in payload hints. | Medium | Align docs with `thumbnail_path` or change responses to emit `thumbnailUrl`. |
| Docs/setup: `npm run dev` (`docs/API.md`:23) | package.json exists under analyzed root but defines no `scripts` block. | Low | Add a `scripts` section (e.g. `"dev": "..."`) or adjust docs to match the repo. |

## Route Prefix Graph (heuristic)

Heuristic **prefix histogram** (depth **3** segments). Useful for spotting missing `/api` clusters; it does **not** execute framework routers or resolve lazy-loaded modules.

### Backend prefixes

- `/api` — **2** hit(s) across routes
- `/api/projects` — **2** hit(s) across routes
- `/api/projects/{projectId}` — **2** hit(s) across routes

### Frontend prefixes

- `/api` — **2** hit(s) across calls
- `/api/projects` — **2** hit(s) across calls
- `/api/projects/{id}` — **2** hit(s) across calls

### Interpretation

- Large frontend buckets with **no** overlapping backend bucket often indicate path drift or missing scanners for alternate HTTP clients.
- Template tokens such as `{id}` are normalized from `${id}` in TS template literals when matched.

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
- **Runtime HTTP probe:** optional single GET to a configured base URL; result is recorded in this report and does not alter static findings.
- **GitHub REST:** optional PAT flags on `contractlens.main` — Issues, issue/PR timeline comments, and PR reviews (`COMMENT`, not line-threaded).
- **Scan cache:** `.contractlens/scan-cache/` uses mtime/size plus **SHA-256 of file bytes** when present in the cache entry (legacy entries fingerprint-only until resaved).
- Permission boundaries apply to filesystem tools.
- The sample project is intentionally tiny so the demo stays reproducible.
