"""Print MCP registration summary and latest artifact hints."""

from __future__ import annotations

from contractlens.config import DEFAULT_REPORT_DIR, PACKAGE_ROOT

from contractlens.mcp_server import audit_log
from contractlens.mcp_server import capabilities as cap
from contractlens.mcp_server import prompts as pr
from contractlens.mcp_server import resources as res
from contractlens.mcp_server import server as srv
from contractlens.mcp_server import tools
from contractlens.mcp_server.capability_manifest import build_capability_manifest


def _latest_md_status() -> str:
    rd = DEFAULT_REPORT_DIR.resolve()
    if not rd.is_dir():
        return "missing dir"
    mds = sorted(rd.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return "found" if mds else "none"


def _trace_status() -> str:
    p = PACKAGE_ROOT / "contractlens-runs" / "latest" / "execution_trace.json"
    return "found" if p.is_file() else "missing"


def _run_summary_status() -> str:
    p = PACKAGE_ROOT / "contractlens-runs" / "latest" / "run_summary.json"
    return "found" if p.is_file() else "missing"


def _manifest_ok() -> bool:
    try:
        build_capability_manifest()
        return True
    except Exception:
        return False


def _docs_ok() -> bool:
    return (PACKAGE_ROOT / "docs" / "MCP_CAPABILITIES.md").is_file()


def main() -> None:
    sdk_active = cap.native_resources_prompts_available()
    sdk_label = "active" if sdk_active else "fallback"

    print("[MCP] ContractLens MCP Server")
    print(f"[MCP] Tools: {len(tools.MCP_TOOL_NAMES)}")
    print(f"[MCP] Resources: {len(res.RESOURCE_REGISTRY)}")
    print(f"[MCP] Prompts: {len(pr.PROMPT_NAMES)}")
    print(f"[MCP] SDK registration: {sdk_label}")
    print(f"[MCP] Latest report: {_latest_md_status()}")
    print(f"[MCP] Audit log: {'found' if audit_log.tool_audit_log_path().is_file() else 'missing'}")
    print(f"[MCP] Execution trace: {_trace_status()}")
    print(f"[MCP] Run summary: {_run_summary_status()}")
    print(f"[MCP] Capability manifest: {'available' if _manifest_ok() else 'error'}")
    print(f"[MCP] Docs export: {'docs/MCP_CAPABILITIES.md' if _docs_ok() else 'missing — run export_docs'}")
    if srv.RESOURCE_PROMPT_PROBE_ERROR:
        print(f"[MCP] Registration probe detail: {srv.RESOURCE_PROMPT_PROBE_ERROR}")


if __name__ == "__main__":
    main()
