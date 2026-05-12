# ContractLens AI

## What it is

ContractLens AI is **MCP-first**: a local, deterministic **repository intelligence** layer that scans frontend HTTP usage and backend routes, compares them, and writes a Markdown drift report. **LangGraph** orchestrates the workflow; **CrewAI-compatible** agents call the same MCP-style tools the CLI uses; **tool audit logs** make each run observable.

## Why this is MCP-first

ContractLens does **not** hand agents an unconstrained view of your filesystem. Repository reads, scans, comparisons, report emission, curated resources (latest contracts/traces/reports), and deterministic prompts all flow through a **controlled MCP-compatible surface**: explicit tools with audit trails, permission checks, optional native MCP resources/prompts on the stdio server, and portfolio-ready manifests/documentation generators.

This keeps demos reproducible, observable, and easy to explain as serious AI-engineering hygiene—not “LLM vibes.”

## OpenAPI / Swagger support

ContractLens optionally discovers **`openapi.json`**, **`swagger.json`**, and common **`*.yaml` / `*.yml`** variants under the analyzed `--root`. Parsed operations become **`ApiContract`** rows (same shape as scanners), then:

1. **Workflow (`scan_openapi` node)** loads specs immediately after the repository listing step.
2. **`compare_contracts`** merges normal frontend-vs-backend findings with **OpenAPI vs backend code** drift (`openapi_vs_code_*` mismatch areas).
3. **Reports** include **OpenAPI / Swagger Analysis** (spec paths, parsed operation counts, drift table, parsing limitations).

This improves **backend-side accuracy** by treating the published contract as a second truth source: when docs promise `/files` but `[HttpPost("{projectId}/models")]` serves `/models`, or when documented JSON fields differ from anonymous response shapes inferred from C#, ContractLens surfaces **documentation/schema drift** deterministically (no LLM).

**MCP tools:** `find_openapi_specs`, `parse_openapi_contracts`, `compare_backend_to_openapi` (optional `backend_contracts` / `openapi_contracts` overrides).

If PyYAML is missing, JSON specs still load and YAML files are reported as skipped in workflow notes.

## Auth / role contract drift

ContractLens pairs scanned frontend HTTP calls with backend routes and applies a **deterministic auth-layer pass**: regex/heuristic extraction of role hints (`hasRole`, `can(...)`, `isAdmin`-style flags), `Authorization` / bearer-ish tokens, `withCredentials`, plus backend `[Authorize]`, `[Authorize(Roles=...)]`, `[Authorize(Policy=...)]`, `[AllowAnonymous]`, and light Express/FastAPI middleware patterns. The Markdown report includes **Auth / Role Contract Analysis** with rows such as `backend_requires_auth_frontend_missing_token` and `frontend_allows_role_backend_blocks`.

**MCP tools:** `scan_frontend_auth`, `scan_backend_auth`, `compare_auth_contracts` (pass contract arrays from `scan_frontend_contracts` / `scan_backend_routes` plus the auth finding arrays).

## Documentation drift

Markdown files discovered under `--root` are mined for **endpoint mentions**, **quoted JSON-like property names**, fenced JSON code blocks, **`npm run …`** hints, and simple env-assignment patterns. Those claims are compared deterministically to scanned frontend/backend contracts for routes (with OpenAPI operations included for similarity/tie-break hints). **JSON property names** prefer **backend controller payloads** when `.cs` routes exist so optimistic FE/OpenAPI docs cannot hide stale prose. Shallow **`package.json`** `scripts` maps are checked when manifests exist.

**MCP tools:** `scan_documentation_contracts`, `compare_documentation_drift`.

## MCP Server Capabilities

The stdio server (`python -m contractlens.mcp_server.server`) exposes:

- **Tools** — filesystem + scanners + comparator + report pipeline + inspection helpers (`list_mcp_resources`, `read_mcp_resource`, `list_mcp_prompts`, `get_mcp_prompt`).
- **Resources** — MCP `resources/list` + `resources/read` for seven registered `contractlens://…` URIs (JSON payloads via `resources.py`). `contractlens://runs/run-YYYYMMDD-HHMMSS/summary` is readable the same way but is not enumerated in `resources/list`. Optional query `?root=` applies to `contractlens://repo/tree`.
- **Prompts** — MCP `prompts/list` + `prompts/get` for five deterministic templates (`prompts.py`; arguments are strings, often JSON-encoded blobs).

If native registration fails on your SDK build, the server keeps running and the helper tools above expose the same data without relying on MCP resource/prompt methods.

Inspect registration + artifact hints:

```bash
python -m contractlens.mcp_server.inspect_mcp
```

Local dispatch smoke test (no interactive MCP client session):

```bash
python -m contractlens.mcp_server.client_smoke_test
```

JSON capability manifest (for clients/portfolios):

```bash
python -m contractlens.mcp_server.capability_manifest
```

Generate MCP docs (`docs/MCP_CAPABILITIES.md`):

```bash
python -m contractlens.mcp_server.export_docs
```

Optional **stdio protocol** exercise (spawns the server subprocess + MCP `ClientSession`; exits 0 even when falling back to explanation-only mode):

```bash
python -m contractlens.mcp_server.stdio_client_test
```

## MCP surface

| Layer | Role |
| --- | --- |
| **Tools** | Repository ops plus analysis (`scan_*`, `compare_contracts`, OpenAPI tools, `evaluate_ci_gate`, `generate_contract_report`, `generate_html_report`, run history (`list_runs`, `get_run_summary`, `get_run_artifact`, `get_run_trace`), …) and MCP introspection helpers. |
| **Resources** | Seven registered `contractlens://…` URIs (repo tree, latest contracts/mismatches/report, execution trace, run summary); stamped `contractlens://runs/run-…/summary` is readable via `resources/read` but omitted from `resources/list`. |
| **Prompts** | Audit/review templates — registered on the stdio server when supported; otherwise use `list_mcp_prompts` / `get_mcp_prompt`. |
| **Permissions** | `contractlens/mcp_server/permissions.py` — reads confined to the chosen root; writes require `allow_write`; ignores `node_modules`, `.git`, build dirs, etc. |
| **Audit** | Every tool call appends to `contractlens-runs/latest/tool_audit_log.json`. |

## Install

```bash
pip install -r requirements.txt
```

## Configuration (optional)

Place **`contractlens.toml`** or **`contractlens.yaml`** in the analyzed **`--root`** repo (or in the ContractLens package root when dogfooding this repo). First matching file wins.

Supported keys (under a `[contractlens]` table / `contractlens:` mapping):

| Key | Meaning |
| --- | --- |
| `extra_ignore_dirs` | Extra directory **names** skipped during scans (same idea as `node_modules`). |
| `emit_html_by_default` | Also write `.html` reports without `--html`. |
| `openapi_max_ref_chain` | OpenAPI local `$ref` walk depth (4–96; code default 32). |
| `probe_base_url` | Before the report is written: single **GET**; result appears under **Runtime HTTP probe** in Markdown/HTML (stdout/stderr still mirrors reachability). |
| `scan_cache` | When `true`, reuse per-file scanner cache under **`<root>/.contractlens/scan-cache/`** (same idea as `--scan-cache`; env can override). |

YAML needs PyYAML (already a dependency). TOML uses `tomllib` on Python 3.11+ or **`tomli`** on older versions (`requirements.txt`).

Example: `examples/contractlens.example.toml`.

**CLI:** `--issue-draft PATH` writes a GitHub issue **draft** Markdown file (no GitHub API).

**GitHub REST (optional PAT):** `--github-repo OWNER/REPO` (or `GITHUB_REPOSITORY`), `--github-token-env VAR` (default `GITHUB_TOKEN`), **`--github-create-issue`**, **`--github-issue-comment N`** (timeline comment on issue or PR), **`--github-pr-review N`** (PR **review** with `event=COMMENT` — summary on the review UI), **`--github-pr-inline-comments N`** (line-specific review comments on PR `N`, capped by **`--github-inline-max`**; uses mismatch `comment_path` / `comment_line` from the frontend scanner). Requires token scopes for Issues + Pull requests (classic: `repo`; fine-grained: matching write caps).

For **`--github-pr-inline-comments`**, point **`--root` at the same folder GitHub treats as the repository root** (your monorepo/checkout root). Paths and line numbers come from the frontend scanner relative to that root so they can match files/lines on the PR head; analyzing only a subfolder can misalign paths vs GitHub.

**Scan cache:** `--scan-cache` enables; **`--no-scan-cache`** disables (overrides config/env). Cached entries store **`content_sha256`** so identical size/mtime clones still miss when bytes differ; older cache files without that field fall back to fingerprint-only matching until rewritten.

**Environment:** `CONTRACTLENS_PROBE_BASE_URL` overrides `probe_base_url` when set. **`CONTRACTLENS_SCAN_CACHE`**=`1|true|yes|on` enables cache; `0|false|no|off` disables it (CLI `--scan-cache` / `--no-scan-cache` still wins).

## Commands

Main demo (unchanged):

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --verbose
```

On **your own codebase**, use **`--root .`** (or the absolute path to the repo root) so scans and optional GitHub inline comments line up with paths in GitHub’s UI—especially in a monorepo.

Standalone **HTML** report (embedded dark-theme stylesheet; written beside the Markdown file):

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --verbose --html
```

Git **changed-only** mode restricts scanners (and OpenAPI loads when narrowed) to paths reported by local **`git diff --name-only`** plus **`git diff --cached --name-only`** under `--root`. **Untracked files are omitted** unless staged; **`git`** must be on `PATH`. If the intersect is empty, pass **`--fallback-full-scan`** to keep the full discovered listing:

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --changed-only --verbose
python -m contractlens.main --feature "Create Project + Upload File" --root . --changed-only --fallback-full-scan --verbose
```

The MCP tool **`get_changed_files`** mirrors this discovery (`include_cached` controls staged paths).

MCP tools walkthrough:

```bash
python -m contractlens.mcp_server.tools_demo
```

Stdio MCP server (needs `mcp` installed; blocks until a client connects):

```bash
python -m contractlens.mcp_server.server
```

Quick verification (sample project, scanners, comparator, workflow artifacts, manifest + docs export):

```bash
python -m contractlens.verify_demo
```

### Local dashboard

Minimal **read-only** UI for the latest audit artifacts under **`contractlens-runs/latest/`** (plus opening mirrored Markdown/HTML reports under **`contractlens-reports/`**). It does **not** run the analysis pipeline and does **not** use a database.

Implementation: **FastAPI** backend. Production-like UI: **React + Vite** under `dashboard-ui/` (build writes into `contractlens/dashboard/static_built/`). If that folder is missing, the server falls back to legacy **vanilla JS** under `contractlens/dashboard/static/`.

```bash
pip install -r requirements.txt
cd dashboard-ui && npm ci && npm run build && cd ..
python -m contractlens.dashboard.server
```

Then open **http://127.0.0.1:8765/** (override host/port with **`CONTRACTLENS_DASHBOARD_HOST`** / **`CONTRACTLENS_DASHBOARD_PORT`**). Run **`python -m contractlens.main …`** at least once so `run_summary.json`, traces, contracts, and `report.md` exist.

**Reads:** `contractlens-runs/latest/run_summary.json`, stamped `run-*` snapshots via the run picker, traces, contracts, mismatches, mirrored `report.md`, and optional HTML under **`contractlens-reports/`**.

**API:** `GET /api/runs`, `GET /api/snapshot?run_id=latest|run-…`, `GET /api/diff?left=&right=`, report routes accept `run_id` as well.

**Does not:** rerun scanners, authenticate dashboard users. GitHub calls happen only from **`contractlens.main`** when you pass the REST flags above.

### CI mode

Use **`--ci`** after the audit to set the process exit code from mismatch severity (report is still written first). **`--fail-on`** defaults to **`High`**.

```bash
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --ci --fail-on High --verbose
```

With drift present (e.g. the intentional sample mismatches), **`exit code 1` is expected** — treat that as a failed gate, not a crash. Use **`--fail-on Medium`** or **`Low`** for stricter pipelines. Details and a GitHub Actions snippet: [`docs/CI_MODE.md`](docs/CI_MODE.md).

The MCP tool **`evaluate_ci_gate`** applies the same threshold logic to an arbitrary `mismatches` array.

## Artifacts

| Path | Contents |
| --- | --- |
| `contractlens-reports/` | Markdown reports (`contractlens-report-<feature-slug>.md`). With **`--html`**, also `contractlens-report-<feature-slug>.html` (static file, no server). |
| `contractlens-runs/latest/` | Rolling snapshot of the **most recent** audit (mirrored under `contractlens-runs/run-YYYYMMDD-HHMMSS/`). Standard files: `run_summary.json`, `tool_audit_log.json`, `execution_trace.json`, `agent_trace.json`, `frontend_contracts.json`, `backend_contracts.json`, `mismatches.json`, `report.md`. Optional **`<repo>/.contractlens/scan-cache/`** appears when scan caching is enabled. |
| `contractlens-runs/run-*` | Immutable copy of the same eight files after each completed workflow run. |

**Run summary (`run_summary.json`)** includes `run_id`, `feature_name`, `root_path`, `started_at`, `completed_at`, `duration_ms`, frontend/backend counts, mismatch counts, `high_risk_count`, `report_path`, plus optional **`runtime_probe_base_url`** and **`runtime_probe`** (GET outcome when configured).

**MCP:** `list_runs`, `get_run_summary`, `get_run_artifact`; resources `contractlens://runs/latest/summary` and `contractlens://runs/run-YYYYMMDD-HHMMSS/summary`.

Optional LLM CrewAI: set `OPENAI_API_KEY` or force offline steps with `--deterministic-agents`.

## Current limitations

- Heuristic static parsing; **no full AST / router graph** — see **Route prefix graph** sections for a shallow clustering hint only.
- MCP `prompts/get` arguments are string-keyed per the MCP spec (embed JSON arrays/objects as strings).
- `write_report` over MCP requires `allow_write: true` in tool arguments.

## Phase 2 (ideas — beyond MVP)

Optional extensions, not required for the shipped demo: **full AST / router-aware scanning**, **stronger OpenAPI handling** (export parity, deeper `$ref`, external refs), **richer auth/policy comparison**, **full LLM CrewAI reasoning** (beyond deterministic fallback), **opening PRs automatically** from audit results, HTML/dashboard polish, CI/GitHub Apps integrations. Inline PR review comments and timeline/issue/review hooks above are already part of the current CLI.

Presenter notes: `docs/CONTRACTLENS_MVP.md`, `docs/ARCHITECTURE.md`.

GitHub Actions workflow (verify demo + CLI + pytest): `.github/workflows/contractlens-ci.yml`.

Local tests: `pytest -q` (repo `pytest.ini` adds the package root to `pythonpath`).
