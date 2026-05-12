# AGENTS.md

## Project Name

ContractLens AI

## Project Intent

ContractLens AI is a presentation-ready multi-agent developer tool that detects frontend-backend contract drift.

The goal is not to build a generic chatbot.

The goal is to demonstrate a real agent-based software engineering workflow using:

- CrewAI for specialist agent roles
- LangGraph for stateful workflow orchestration
- MCP for safe local repository tools
- deterministic static analysis for reliable demo results

ContractLens AI analyzes a selected feature flow and detects mismatches between frontend expectations and backend reality.

Example problem:

The frontend calls:

```text
POST /api/projects/{id}/files
```

but the backend exposes:

```text
POST /api/projects/{projectId}/models
```

Or the frontend expects:

```text
id
thumbnailUrl
```

but the backend returns:

```text
projectId
thumbnail_path
```

The MVP should generate a Markdown report explaining these mismatches, their risk level, and suggested fixes.

---

## Primary Goal for MVP

The MVP must be ready for a presentation demo.

When this command runs:

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --verbose
```

the user should clearly see:

- MCP tool layer
- LangGraph workflow execution
- CrewAI agent role execution
- frontend API calls detected
- backend routes detected
- contract mismatches detected
- Markdown report generated

This MVP does not need to be production-perfect.

It must be small, reliable, visible, and explainable.

---

## Non-Negotiable Requirements

Do not create only empty folders or fake placeholder files.

The project must include real minimal implementations of:

1. MCP tools
2. LangGraph workflow
3. CrewAI agent definitions or deterministic CrewAI-compatible fallback
4. frontend scanner
5. backend scanner
6. contract comparator
7. Markdown report writer
8. sample project with intentional mismatches

The analysis accuracy can be simple, but the pipeline must actually run.

---

## Important Demo Principle

For the presentation, visibility is more important than complexity.

The terminal should show logs such as:

```text
[MCP] list_project_files called
[LangGraph] scan_repository node executed
[CrewAI] Frontend Analyst running
[CrewAI] Backend Analyst running
[CrewAI] Contract Reviewer running
[Report] Markdown report generated
```

This makes it easy to explain how CrewAI, LangGraph, and MCP fit together.

---

## Required Project Structure

Use this structure where possible:

```text
contractlens/
  __init__.py
  main.py
  config.py

  scanner/
    __init__.py
    file_scanner.py
    frontend_scanner.py
    backend_scanner.py

  contracts/
    __init__.py
    models.py
    comparator.py

  agents/
    __init__.py
    crew.py

  workflow/
    __init__.py
    state.py
    graph.py

  mcp_server/
    __init__.py
    tools.py
    server.py
    tools_demo.py

  reporting/
    __init__.py
    markdown_report.py

examples/
  sample_project/
    frontend/
      projectApi.ts
      UploadModal.tsx
    backend/
      ProjectsController.cs

contractlens-reports/

docs/
  CONTRACTLENS_MVP.md
  ARCHITECTURE.md
  EXAMPLE_REPORT.md

README.md
requirements.txt
```

---

## Required CLI

The main command must be:

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --verbose
```

Optional mode flag:

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --mode demo --verbose
```

Default behavior should prioritize a stable demo.

If CrewAI, LangGraph, or MCP packages are unavailable or require extra setup, the system should not crash. It should use deterministic fallback and clearly print what happened.

Example:

```text
[CrewAI] Deterministic fallback mode enabled because no LLM provider is configured.
```

---

## MCP Requirements

Create MCP-related files under:

```text
contractlens/mcp_server/
```

Required files:

```text
tools.py
server.py
tools_demo.py
```

The MCP tool layer must expose real local repository functions:

```text
list_project_files
read_project_file
search_in_files
write_report
```

### Tool: list_project_files

Input:

```json
{
  "root": "."
}
```

Output:

```json
{
  "files": ["..."]
}
```

### Tool: read_project_file

Input:

```json
{
  "path": "examples/sample_project/frontend/projectApi.ts"
}
```

Output:

```json
{
  "content": "..."
}
```

### Tool: search_in_files

Input:

```json
{
  "root": ".",
  "query": "axios.post"
}
```

Output:

```json
{
  "matches": []
}
```

### Tool: write_report

Input:

```json
{
  "path": "contractlens-reports/report.md",
  "content": "..."
}
```

Output:

```json
{
  "success": true,
  "path": "contractlens-reports/report.md"
}
```

The MCP tools must also be callable directly from the local workflow so the demo can run without a complex MCP client setup.

Add this command:

```bash
python -m contractlens.mcp_server.tools_demo
```

It should demonstrate the tool layer by calling:

- list_project_files
- search_in_files
- read_project_file

and printing clear output.

Also add:

```bash
python -m contractlens.mcp_server.server
```

If a real FastMCP server can be implemented safely, implement it.

If not, implement the local MCP-style tool layer and document that the MVP exposes MCP-compatible repository tools.

Do not pretend something is fully implemented if it is only partially wired.

---

## LangGraph Requirements

Create:

```text
contractlens/workflow/state.py
contractlens/workflow/graph.py
```

LangGraph must define a real workflow if the package is available.

The workflow nodes should be:

```text
select_feature
scan_repository
analyze_frontend
analyze_backend
compare_contracts
generate_report
```

Workflow:

```text
START
  ↓
select_feature
  ↓
scan_repository
  ↓
analyze_frontend
  ↓
analyze_backend
  ↓
compare_contracts
  ↓
generate_report
  ↓
END
```

Each node should update a shared state.

The state should include:

```python
feature_name
root_path
files
frontend_findings
backend_findings
mismatches
risk_summary
report_path
execution_trace
mcp_trace
agent_trace
errors
```

Each node should print visible logs in verbose mode.

Example logs:

```text
[LangGraph] select_feature
[LangGraph] scan_repository
[LangGraph] analyze_frontend
[LangGraph] analyze_backend
[LangGraph] compare_contracts
[LangGraph] generate_report
```

If LangGraph is unavailable, create a deterministic sequential fallback workflow with the same node names and execution trace.

The report must include the LangGraph execution trace.

---

## CrewAI Requirements

Create:

```text
contractlens/agents/crew.py
```

The MVP should define these agent roles:

### Frontend Analyst

Responsible for:

- finding frontend API calls
- detecting expected request fields
- detecting expected response fields
- mapping frontend files to the selected feature

### Backend Analyst

Responsible for:

- finding backend API routes
- detecting request DTOs
- detecting response DTOs
- detecting auth hints

### Contract Reviewer

Responsible for:

- comparing frontend and backend contracts
- detecting mismatches
- assigning risk levels
- creating fix suggestions

### Report Writer

Responsible for:

- producing a clean Markdown report
- adding GitHub issue draft text
- adding tooling notes

If CrewAI can run without paid API setup, use real CrewAI Agent and Task objects.

If CrewAI requires an LLM provider and no API key is configured, use deterministic fallback mode.

Fallback mode must still be meaningful:

- Frontend Analyst calls the real frontend scanner.
- Backend Analyst calls the real backend scanner.
- Contract Reviewer calls the real comparator.
- Report Writer calls the real Markdown report writer.

Do not return hardcoded fake results from agents.

It is acceptable for the sample project to contain intentional mismatches.

The report must include the CrewAI agent trace.

---

## Scanner Requirements

The scanner must inspect actual files.

Do not rely only on hardcoded report text.

---

## Frontend Scanner

Create:

```text
contractlens/scanner/frontend_scanner.py
```

Scan files with these extensions:

```text
.ts
.tsx
.js
.jsx
.vue
```

Detect patterns:

```text
fetch(...)
axios.get(...)
axios.post(...)
axios.put(...)
axios.delete(...)
apiClient.get(...)
apiClient.post(...)
apiClient.put(...)
apiClient.delete(...)
```

Extract when possible:

- HTTP method
- API path
- request fields
- expected response fields
- source file
- source line

Example result:

```json
{
  "method": "POST",
  "path": "/api/projects/{id}/files",
  "request_fields": ["file"],
  "response_fields": ["id", "thumbnailUrl"],
  "source": "examples/sample_project/frontend/projectApi.ts",
  "line": 18
}
```

---

## Backend Scanner

Create:

```text
contractlens/scanner/backend_scanner.py
```

Prioritize ASP.NET Core style controllers for the demo.

Detect patterns:

```text
[Route("api/projects")]
[HttpGet]
[HttpPost]
[HttpPut]
[HttpDelete]
[Authorize]
[AllowAnonymous]
```

Also support simple Express/FastAPI detection if easy.

Extract when possible:

- HTTP method
- API path
- request DTO
- response DTO
- auth hint
- source file
- source line

Example result:

```json
{
  "method": "POST",
  "path": "/api/projects/{projectId}/models",
  "request_dto": "IFormFile",
  "response_dto": "ModelUploadResponse",
  "auth": "Authorize",
  "source": "examples/sample_project/backend/ProjectsController.cs",
  "line": 24
}
```

---

## Contract Models

Create Pydantic models in:

```text
contractlens/contracts/models.py
```

Use models similar to:

```python
from pydantic import BaseModel, Field

class ApiContract(BaseModel):
    method: str
    path: str
    source: str
    line: int | None = None
    request_fields: list[str] = Field(default_factory=list)
    response_fields: list[str] = Field(default_factory=list)
    request_dto: str | None = None
    response_dto: str | None = None
    auth: str | None = None

class ContractMismatch(BaseModel):
    area: str
    frontend_expects: str
    backend_provides: str
    risk: str
    suggestion: str
```

---

## Comparator Requirements

Create:

```text
contractlens/contracts/comparator.py
```

Detect mismatches such as:

```text
/api/projects/{id}/files vs /api/projects/{projectId}/models
id vs projectId
thumbnailUrl vs thumbnail_path
name vs title
createdAt vs created_at
missing endpoint
method mismatch
auth hint mismatch
```

Risk levels:

```text
High
Medium
Low
Unknown
```

Rule of thumb:

```text
High = likely breaks feature
Medium = may cause partial UI/API failure
Low = minor naming or documentation issue
Unknown = not enough information
```

The comparator does not need to be perfect.

It must reliably detect the intentional mismatches in the sample project.

---

## Sample Project Requirement

Create:

```text
examples/sample_project/
```

Required sample files:

```text
examples/sample_project/frontend/projectApi.ts
examples/sample_project/frontend/UploadModal.tsx
examples/sample_project/backend/ProjectsController.cs
```

The sample project must intentionally contain mismatches.

Frontend should include something like:

```typescript
await apiClient.post(`/api/projects/${projectId}/files`, formData);

return {
  id: response.data.id,
  thumbnailUrl: response.data.thumbnailUrl
};
```

Backend should include something like:

```csharp
[HttpPost("{projectId}/models")]
public IActionResult UploadModel(Guid projectId, IFormFile file)
{
    return Ok(new {
        projectId = projectId,
        thumbnail_path = "/thumbnails/model.png"
    });
}
```

This ensures the demo always produces visible mismatches.

---

## Report Requirements

Create:

```text
contractlens/reporting/markdown_report.py
```

Reports must be saved under:

```text
contractlens-reports/
```

Filename format:

```text
contractlens-report-create-project-upload-file.md
```

The report must include:

```md
# ContractLens AI Report

## Feature

## Scan Summary

## MCP Tool Usage

## LangGraph Execution Trace

## CrewAI Agent Trace

## Frontend Expectations

## Backend Reality

## API Contract Table

## Mismatch Report

## Risk Assessment

## Suggested Fix Plan

## Optional GitHub Issue Draft

## Current Limitations
```

The report should be readable and suitable for a GitHub portfolio.

Avoid vague suggestions.

Bad:

```text
Fix backend.
```

Good:

```text
Align the frontend upload call `/api/projects/{id}/files` with the backend route `/api/projects/{projectId}/models`, or add a backend alias endpoint that supports the frontend path.
```

---

## README Requirements

Update or create:

```text
README.md
```

README must explain:

- What ContractLens AI is
- What frontend-backend contract drift means
- Why this problem matters
- How MCP is used
- How LangGraph is used
- How CrewAI is used
- Why deterministic fallback exists
- How to run the main demo
- How to run MCP tools demo
- How to run the MCP server
- Where reports are generated
- Current limitations
- Phase 2 roadmap

README should include these commands:

```bash
pip install -r requirements.txt
```

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --verbose
```

```bash
python -m contractlens.mcp_server.tools_demo
```

```bash
python -m contractlens.mcp_server.server
```

---

## Documentation Requirements

Create:

```text
docs/CONTRACTLENS_MVP.md
docs/ARCHITECTURE.md
docs/EXAMPLE_REPORT.md
```

The docs should be short but clear.

They should help explain the project during a presentation.

---

## Presentation Explanation

The project should support this explanation:

```text
ContractLens AI is a multi-agent contract auditing tool.

MCP provides controlled local repository tools such as listing files, reading files, searching code, and writing reports.

LangGraph controls the workflow as a state graph. Each node receives the current state, performs one step, and passes the updated state forward.

CrewAI represents the specialist agent layer. The Frontend Analyst, Backend Analyst, Contract Reviewer, and Report Writer each own a specific responsibility.

For demo reliability, the MVP uses deterministic static analysis instead of depending on paid LLM calls. However, the agent workflow is structured so LLM reasoning can be added in Phase 2.
```

---

## Current Limitations Section

The README and report must honestly mention:

```md
## Current Limitations

- Static analysis is heuristic-based.
- Complex dynamic API paths may not be fully resolved.
- Response field extraction is limited in the MVP.
- CrewAI may run in deterministic fallback mode if no LLM provider is configured.
- MCP tools are minimal and local in the first version.
- The sample project is intentionally small for presentation reliability.
```

---

## Phase 2 Roadmap

Mention these possible improvements:

```md
## Phase 2 Roadmap

- Real LLM-powered CrewAI reasoning
- OpenAPI/Swagger parsing
- GitHub issue creation
- Pull request comments
- Auth and role policy comparison
- Frontend route/page analysis
- Documentation drift detection
- Test runner integration
- CI mode for GitHub Actions
- HTML report output
- Persistent audit history
```

---

## Final Instruction for Codex

Before making changes:

1. Inspect the repository.
2. Identify the current structure.
3. Create a short implementation plan.
4. Then implement the smallest reliable presentation-ready MVP.

During implementation:

- Prioritize visible demo output.
- Do not overengineer.
- Do not create fake analysis.
- Use real file scanning.
- Use clear terminal logs.
- Make the sample project produce guaranteed mismatches.
- Keep the project runnable without paid API keys.
- If CrewAI, LangGraph, or MCP needs fallback behavior, document it honestly.

After implementation, report:

- files created
- files changed
- dependencies added
- how to run the main demo
- how to run the MCP tools demo
- how to run the MCP server
- where the generated report is located
- how CrewAI is used
- how LangGraph is used
- how MCP is used
- current limitations
- next recommended improvements