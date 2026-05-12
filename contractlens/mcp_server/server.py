"""Optional MCP stdio server exposing tools, resources, and prompts; fallbacks if initialization fails."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from contractlens.mcp_server import prompts as mcp_prompts
from contractlens.mcp_server import resources as mcp_resources
from contractlens.mcp_server import tools

RESOURCE_PROMPT_PROBE_ERROR: str | None = None


def _run_resource_prompt_probe() -> tuple[bool, str | None]:
    """Try attaching resource/prompt handlers to a throwaway Server (for inspect_mcp)."""
    global RESOURCE_PROMPT_PROBE_ERROR
    RESOURCE_PROMPT_PROBE_ERROR = None
    try:
        import mcp.types as mtypes
        from mcp.server import Server

        probe = Server("contractlens-register-probe")
        _register_resources(probe, mtypes)
        _register_prompts(probe, mtypes)
        return True, None
    except Exception as exc:
        RESOURCE_PROMPT_PROBE_ERROR = str(exc)
        return False, RESOURCE_PROMPT_PROBE_ERROR


def probe_sdk_registration_ok() -> bool:
    ok, _ = _run_resource_prompt_probe()
    return ok


def _fallback_message() -> None:
    print(
        "[MCP] Full stdio MCP server unavailable (import/initialization failed).\n"
        "[MCP] Fallback: use the local tool layer directly:\n"
        "  - python -m contractlens.mcp_server.tools_demo\n"
        "  - python -m contractlens.mcp_server.inspect_mcp\n"
        "  - python -m contractlens.mcp_server.client_smoke_test\n"
        "  - python -m contractlens.verify_demo\n"
        "See README.md for MCP-first usage vs this optional server.",
        file=sys.stderr,
    )


def _dispatch_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "list_project_files":
        root = args.get("root", ".")
        rr = args.get("repo_root")
        return tools.list_project_files(root, verbose_log=False, repo_root=rr if rr is not None else None)
    if name == "read_project_file":
        return tools.read_project_file(
            args.get("path", ""),
            repo_root=args.get("repo_root", "."),
            verbose_log=False,
        )
    if name == "search_in_files":
        root = args.get("root", ".")
        rr = args.get("repo_root")
        return tools.search_in_files(
            root,
            args.get("query", ""),
            verbose_log=False,
            repo_root=rr if rr is not None else None,
        )
    if name == "write_report":
        return tools.write_report(
            args.get("path", ""),
            args.get("content", ""),
            verbose_log=False,
            allow_write=bool(args.get("allow_write", False)),
        )
    if name == "find_openapi_specs":
        return tools.find_openapi_specs(args.get("root", "."), verbose_log=False)
    if name == "get_changed_files":
        return tools.get_changed_files(
            args.get("root", "."),
            include_cached=bool(args.get("include_cached", True)),
            verbose_log=False,
        )
    if name == "parse_openapi_contracts":
        return tools.parse_openapi_contracts(args.get("root", "."), verbose_log=False)
    if name == "compare_backend_to_openapi":
        raw_be = args.get("backend_contracts")
        raw_oa = args.get("openapi_contracts")
        be_list = raw_be if isinstance(raw_be, list) else None
        oa_list = raw_oa if isinstance(raw_oa, list) else None
        return tools.compare_backend_to_openapi(
            args.get("root", "."),
            backend_contracts=be_list,
            openapi_contracts=oa_list,
            verbose_log=False,
        )
    if name == "scan_frontend_contracts":
        return tools.scan_frontend_contracts(args.get("root", "."), verbose_log=False)
    if name == "scan_backend_routes":
        return tools.scan_backend_routes(args.get("root", "."), verbose_log=False)
    if name == "scan_frontend_auth":
        return tools.scan_frontend_auth(args.get("root", "."), verbose_log=False)
    if name == "scan_backend_auth":
        return tools.scan_backend_auth(args.get("root", "."), verbose_log=False)
    if name == "compare_contracts":
        fe = args.get("frontend_contracts") or []
        be = args.get("backend_contracts") or []
        if not isinstance(fe, list):
            fe = []
        if not isinstance(be, list):
            be = []
        return tools.compare_contracts(fe, be, verbose_log=False)
    if name == "compare_auth_contracts":
        fe = args.get("frontend_contracts") or []
        be = args.get("backend_contracts") or []
        fa = args.get("frontend_auth_findings") or []
        ba = args.get("backend_auth_findings") or []
        if not isinstance(fe, list):
            fe = []
        if not isinstance(be, list):
            be = []
        if not isinstance(fa, list):
            fa = []
        if not isinstance(ba, list):
            ba = []
        return tools.compare_auth_contracts(fe, be, fa, ba, verbose_log=False)
    if name == "scan_documentation_contracts":
        return tools.scan_documentation_contracts(args.get("root", "."), verbose_log=False)
    if name == "compare_documentation_drift":
        fe = args.get("frontend_contracts") or []
        be = args.get("backend_contracts") or []
        oa = args.get("openapi_contracts") or []
        dc = args.get("documentation_claims") or []
        if not isinstance(fe, list):
            fe = []
        if not isinstance(be, list):
            be = []
        if not isinstance(oa, list):
            oa = []
        if not isinstance(dc, list):
            dc = []
        return tools.compare_documentation_drift(
            args.get("root", "."),
            fe,
            be,
            oa,
            dc,
            verbose_log=False,
        )
    if name == "generate_contract_report":
        return tools.generate_contract_report(
            args.get("feature_name", ""),
            args.get("root", "."),
            verbose_log=False,
            allow_write=bool(args.get("allow_write", True)),
            report_dir=args.get("report_dir"),
        )
    if name == "generate_html_report":
        return tools.generate_html_report(
            args.get("feature_name", ""),
            args.get("root", "."),
            verbose_log=False,
            allow_write=bool(args.get("allow_write", True)),
            report_dir=args.get("report_dir"),
        )
    if name == "get_latest_report":
        return tools.get_latest_report(args.get("reports_dir"), verbose_log=False)
    if name == "get_run_trace":
        return tools.get_run_trace(str(args.get("run_id", "latest")), verbose_log=False)
    if name == "list_runs":
        return tools.list_runs(args.get("limit", 50), verbose_log=False)
    if name == "get_run_summary":
        return tools.get_run_summary(str(args.get("run_id", "latest")), verbose_log=False)
    if name == "get_run_artifact":
        return tools.get_run_artifact(
            str(args.get("run_id", "latest")),
            str(args.get("artifact", "")),
            verbose_log=False,
        )
    if name == "explain_mismatch":
        mm = args.get("mismatch") or {}
        if not isinstance(mm, dict):
            mm = {}
        return tools.explain_mismatch(mm, verbose_log=False)
    if name == "evaluate_ci_gate":
        mm = args.get("mismatches") or []
        if not isinstance(mm, list):
            mm = []
        return tools.evaluate_ci_gate(mm, str(args.get("fail_on", "High")), verbose_log=False)
    if name == "list_mcp_resources":
        return tools.list_mcp_resources(verbose_log=False)
    if name == "read_mcp_resource":
        root = args.get("root")
        root_s = str(root) if root not in (None, "") else None
        return tools.read_mcp_resource(args.get("uri", ""), root=root_s, verbose_log=False)
    if name == "list_mcp_prompts":
        return tools.list_mcp_prompts(verbose_log=False)
    if name == "get_mcp_prompt":
        raw_args = args.get("arguments")
        if raw_args is not None and not isinstance(raw_args, dict):
            return {"status": "error", "error": "arguments must be an object"}
        return tools.get_mcp_prompt(args.get("name", ""), raw_args, verbose_log=False)
    return {"status": "error", "error": f"unknown tool: {name}"}


def _resource_slug(uri: str) -> str:
    tail = uri.split("contractlens://", 1)[-1]
    return tail.replace("/", "_").replace("-", "_") or "resource"


def _register_resources(server: Any, mtypes: Any) -> None:
    @server.list_resources()
    async def _list_resources(
        _request: mtypes.ListResourcesRequest | None = None,
    ) -> mtypes.ListResourcesResult:
        rs = []
        for uri in mcp_resources.RESOURCE_REGISTRY:
            rs.append(
                mtypes.Resource(
                    name=_resource_slug(uri),
                    uri=uri,
                    description=mcp_resources.RESOURCE_DESCRIPTIONS.get(uri),
                    mimeType="application/json",
                )
            )
        return mtypes.ListResourcesResult(resources=rs)

    @server.read_resource()
    async def _read_resource(uri: Any) -> mtypes.ReadResourceResult:
        payload = mcp_resources.read_resource_by_uri(str(uri))
        body = json.dumps(payload, indent=2)
        return mtypes.ReadResourceResult(
            contents=[
                mtypes.TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=body,
                )
            ]
        )


def _prompt_argument_specs() -> dict[str, list[dict[str, Any]]]:
    return {
        "audit_feature_contract": [
            {"name": "feature_name", "description": "Human-readable feature label.", "required": True},
            {
                "name": "frontend_contracts",
                "description": "JSON array string of frontend contract objects.",
                "required": True,
            },
            {
                "name": "backend_contracts",
                "description": "JSON array string of backend contract objects.",
                "required": True,
            },
        ],
        "explain_contract_mismatch": [
            {"name": "mismatch", "description": "JSON object string (ContractMismatch fields).", "required": True},
        ],
        "generate_safe_fix_plan": [
            {"name": "mismatches", "description": "JSON array string of mismatch objects.", "required": True},
        ],
        "create_pr_review_comment": [
            {"name": "report_summary", "description": "Short Markdown/text summary.", "required": True},
            {"name": "mismatches", "description": "JSON array string of mismatch objects.", "required": True},
        ],
        "summarize_agent_run": [
            {"name": "execution_trace", "description": "JSON array string (LangGraph trace lines).", "required": True},
            {"name": "mcp_trace", "description": "JSON array string (MCP trace lines).", "required": True},
            {"name": "agent_trace", "description": "JSON array string (legacy agent trace lines).", "required": True},
        ],
    }


def _register_prompts(server: Any, mtypes: Any) -> None:
    specs = _prompt_argument_specs()

    @server.list_prompts()
    async def _list_prompts(_request: mtypes.ListPromptsRequest | None = None) -> mtypes.ListPromptsResult:
        out = []
        for name in mcp_prompts.PROMPT_NAMES:
            raw_args = specs.get(name, [])
            args = [
                mtypes.PromptArgument(
                    name=a["name"],
                    description=a.get("description"),
                    required=a.get("required", False),
                )
                for a in raw_args
            ]
            out.append(
                mtypes.Prompt(
                    name=name,
                    description=f"Deterministic template `{name}` (no LLM call).",
                    arguments=args or None,
                )
            )
        return mtypes.ListPromptsResult(prompts=out)

    @server.get_prompt()
    async def _get_prompt(name: str, arguments: dict[str, str] | None) -> mtypes.GetPromptResult:
        try:
            coerced = mcp_prompts.coerce_prompt_arguments_from_strings(arguments or {})
            text = mcp_prompts.render_named_prompt(name, coerced)
        except Exception as exc:
            err = f"[ContractLens] Prompt render failed: {exc}"
            return mtypes.GetPromptResult(
                description="error",
                messages=[
                    mtypes.PromptMessage(
                        role="user",
                        content=mtypes.TextContent(type="text", text=err),
                    )
                ],
            )
        return mtypes.GetPromptResult(
            description=f"ContractLens prompt template `{name}`",
            messages=[
                mtypes.PromptMessage(
                    role="user",
                    content=mtypes.TextContent(type="text", text=text),
                )
            ],
        )


def _build_tool_list(mtypes: Any) -> list[Any]:
    """Concrete Tool definitions for MCP clients."""
    return [
        mtypes.Tool(
            name="list_project_files",
            description="List repository files under root (honours ignore dirs).",
            inputSchema={
                "type": "object",
                "properties": {
                    "root": {"type": "string"},
                    "repo_root": {"type": "string", "description": "Optional; defaults to root."},
                },
                "required": ["root"],
            },
        ),
        mtypes.Tool(
            name="read_project_file",
            description="Read UTF-8 text relative to repo_root (path traversal blocked).",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "repo_root": {"type": "string"},
                },
                "required": ["path", "repo_root"],
            },
        ),
        mtypes.Tool(
            name="search_in_files",
            description="Search query across text-like files under root.",
            inputSchema={
                "type": "object",
                "properties": {
                    "root": {"type": "string"},
                    "query": {"type": "string"},
                    "repo_root": {"type": "string"},
                },
                "required": ["root", "query"],
            },
        ),
        mtypes.Tool(
            name="write_report",
            description="Write Markdown or text under package workspace. Requires allow_write=true.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "allow_write": {"type": "boolean", "default": False},
                },
                "required": ["path", "content"],
            },
        ),
        mtypes.Tool(
            name="find_openapi_specs",
            description="Find openapi.json/swagger.json/YAML variants under root (respects ignore dirs).",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="get_changed_files",
            description=(
                "List paths changed locally vs HEAD via git diff (plus staged paths when include_cached=true), "
                "restricted to existing files under root."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root": {"type": "string"},
                    "include_cached": {"type": "boolean", "default": True},
                },
                "required": ["root"],
            },
        ),
        mtypes.Tool(
            name="parse_openapi_contracts",
            description="Load discovered specs and return ApiContract-shaped operations plus notes.",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="compare_backend_to_openapi",
            description=(
                "Compare backend scanner routes vs OpenAPI operations for documentation/schema drift "
                "(optional backend_contracts/openapi_contracts arrays override scans)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root": {"type": "string"},
                    "backend_contracts": {"type": "array"},
                    "openapi_contracts": {"type": "array"},
                },
                "required": ["root"],
            },
        ),
        mtypes.Tool(
            name="scan_frontend_contracts",
            description="Run ContractLens frontend scanner; returns contracts[].",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="scan_backend_routes",
            description="Run ContractLens backend scanner; returns routes[].",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="scan_frontend_auth",
            description="Heuristic frontend auth/role/header/withCredentials signals (.ts/.tsx/.js/.jsx/.vue).",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="scan_backend_auth",
            description="Heuristic backend auth annotations (ASP.NET Authorize/AllowAnonymous, light Express/FastAPI).",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="compare_contracts",
            description="Compare frontend vs backend contract rows via comparator.",
            inputSchema={
                "type": "object",
                "properties": {"frontend_contracts": {"type": "array"}, "backend_contracts": {"type": "array"}},
                "required": ["frontend_contracts", "backend_contracts"],
            },
        ),
        mtypes.Tool(
            name="compare_auth_contracts",
            description=(
                "Compare frontend vs backend ApiContract rows using heuristic auth findings "
                "(output mismatches with areas such as backend_requires_auth_frontend_missing_token)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "frontend_contracts": {"type": "array"},
                    "backend_contracts": {"type": "array"},
                    "frontend_auth_findings": {"type": "array"},
                    "backend_auth_findings": {"type": "array"},
                },
                "required": [
                    "frontend_contracts",
                    "backend_contracts",
                    "frontend_auth_findings",
                    "backend_auth_findings",
                ],
            },
        ),
        mtypes.Tool(
            name="scan_documentation_contracts",
            description="Extract heuristic claims (endpoints, fields, npm scripts, headings) from Markdown under root.",
            inputSchema={"type": "object", "properties": {"root": {"type": "string"}}, "required": ["root"]},
        ),
        mtypes.Tool(
            name="compare_documentation_drift",
            description=(
                "Compare scan_documentation_contracts output vs frontend/backend/OpenAPI contract rows "
                "(pass repo root for package.json script checks)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root": {"type": "string"},
                    "frontend_contracts": {"type": "array"},
                    "backend_contracts": {"type": "array"},
                    "openapi_contracts": {"type": "array"},
                    "documentation_claims": {"type": "array"},
                },
                "required": [
                    "root",
                    "frontend_contracts",
                    "backend_contracts",
                    "openapi_contracts",
                    "documentation_claims",
                ],
            },
        ),
        mtypes.Tool(
            name="generate_contract_report",
            description="Run full ContractLens workflow (scanners + comparator + Markdown report).",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string"},
                    "root": {"type": "string"},
                    "report_dir": {"type": "string"},
                    "allow_write": {"type": "boolean", "default": True},
                },
                "required": ["feature_name", "root"],
            },
        ),
        mtypes.Tool(
            name="generate_html_report",
            description=(
                "Run full ContractLens workflow and write Markdown plus standalone HTML "
                "(embedded CSS; same slug as .md beside contractlens-reports/)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string"},
                    "root": {"type": "string"},
                    "report_dir": {"type": "string"},
                    "allow_write": {"type": "boolean", "default": True},
                },
                "required": ["feature_name", "root"],
            },
        ),
        mtypes.Tool(
            name="get_latest_report",
            description="Return newest *.md from reports directory.",
            inputSchema={"type": "object", "properties": {"reports_dir": {"type": "string"}}},
        ),
        mtypes.Tool(
            name="get_run_trace",
            description=(
                "Load execution_trace.json for run_id `latest` or a stamped folder name run-YYYYMMDD-HHMMSS."
            ),
            inputSchema={"type": "object", "properties": {"run_id": {"type": "string", "default": "latest"}}},
        ),
        mtypes.Tool(
            name="list_runs",
            description=(
                "List stamped run directories under contractlens-runs/ (newest first) plus latest run_summary snapshot."
            ),
            inputSchema={
                "type": "object",
                "properties": {"limit": {"type": "integer", "default": 50, "minimum": 1, "maximum": 500}},
            },
        ),
        mtypes.Tool(
            name="get_run_summary",
            description="Read run_summary.json for `latest` or run-YYYYMMDD-HHMMSS.",
            inputSchema={
                "type": "object",
                "properties": {"run_id": {"type": "string", "default": "latest"}},
            },
        ),
        mtypes.Tool(
            name="get_run_artifact",
            description=(
                "Fetch one canonical artifact file from a run dir (run_summary.json, tool_audit_log.json, "
                "execution_trace.json, agent_trace.json, frontend_contracts.json, backend_contracts.json, "
                "mismatches.json, or report.md)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {"type": "string", "default": "latest"},
                    "artifact": {"type": "string"},
                },
                "required": ["artifact"],
            },
        ),
        mtypes.Tool(
            name="explain_mismatch",
            description="Deterministic explanation for one mismatch dict.",
            inputSchema={
                "type": "object",
                "properties": {"mismatch": {"type": "object"}},
                "required": ["mismatch"],
            },
        ),
        mtypes.Tool(
            name="evaluate_ci_gate",
            description=(
                "Given mismatch rows (risk fields), decide CI pass/fail and exit_code using fail_on threshold "
                "(High/Medium/Low)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "mismatches": {"type": "array"},
                    "fail_on": {"type": "string", "enum": ["High", "Medium", "Low"], "default": "High"},
                },
                "required": ["mismatches"],
            },
        ),
        mtypes.Tool(
            name="list_mcp_resources",
            description="List contractlens:// resources (fallback/introspection for clients without resources support).",
            inputSchema={"type": "object", "properties": {}},
        ),
        mtypes.Tool(
            name="read_mcp_resource",
            description="Read a contractlens:// resource as JSON (optional root for repo/tree).",
            inputSchema={
                "type": "object",
                "properties": {
                    "uri": {"type": "string"},
                    "root": {"type": "string", "description": "Override repo root for contractlens://repo/tree"},
                },
                "required": ["uri"],
            },
        ),
        mtypes.Tool(
            name="list_mcp_prompts",
            description="List deterministic prompt template names.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mtypes.Tool(
            name="get_mcp_prompt",
            description="Render a prompt template by name (arguments match prompts/get JSON-string conventions).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "arguments": {"type": "object", "additionalProperties": True},
                },
                "required": ["name"],
            },
        ),
    ]


async def _stdio_main() -> None:
    try:
        import mcp.types as mtypes
        from mcp.server import InitializationOptions, NotificationOptions, Server
        from mcp.server.stdio import stdio_server
    except Exception as exc:
        print(f"[MCP] Could not import Python MCP server packages: {exc!r}", file=sys.stderr)
        _fallback_message()
        return

    server = Server("contractlens-repo-tools")

    tool_defs = _build_tool_list(mtypes)

    @server.list_tools()
    async def _list_tools(_request: mtypes.ListToolsRequest | None = None) -> mtypes.ListToolsResult:
        return mtypes.ListToolsResult(tools=tool_defs)

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any] | None) -> list[mtypes.TextContent]:
        args = arguments or {}
        payload = _dispatch_tool(name, args)
        return [mtypes.TextContent(type="text", text=json.dumps(payload, indent=2))]

    try:
        _register_resources(server, mtypes)
        _register_prompts(server, mtypes)
    except Exception as exc:
        print(
            f"[MCP] Warning: resource/prompt handlers not attached ({exc!r}). "
            "Use list_mcp_resources / get_mcp_prompt tools.",
            file=sys.stderr,
        )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="contractlens-repo-tools",
                server_version="0.4.4",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main() -> None:
    print(
        "[MCP] Starting ContractLens stdio MCP server.\n"
        "[MCP] This process waits on stdin for MCP JSON-RPC (use an MCP client). Ctrl+C to exit.",
        file=sys.stderr,
    )
    try:
        asyncio.run(_stdio_main())
    except KeyboardInterrupt:
        print("[MCP] stopped", file=sys.stderr)


if __name__ == "__main__":
    main()
