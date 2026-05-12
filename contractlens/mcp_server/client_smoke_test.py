"""Local MCP dispatch smoke test (does not launch a stdio MCP session)."""

from __future__ import annotations

import json
import sys

from contractlens.mcp_server import resources as mcp_resources
from contractlens.mcp_server.server import _dispatch_tool


def main(argv: list[str] | None = None) -> int:
    _ = argv
    errors: list[str] = []

    print("[client_smoke_test] Local server dispatch + registry checks (no JSON-RPC client).")

    ex = _dispatch_tool(
        "explain_mismatch",
        {
            "mismatch": {
                "area": "path",
                "frontend_expects": "/a",
                "backend_provides": "/b",
                "risk": "High",
                "suggestion": "Align routes.",
            }
        },
    )
    if not isinstance(ex, dict) or "explanation" not in ex:
        errors.append(f"explain_mismatch unexpected: {ex!r}")

    lr = _dispatch_tool("list_mcp_resources", {})
    if lr.get("count") != len(mcp_resources.RESOURCE_REGISTRY):
        errors.append(f"list_mcp_resources count mismatch: {lr!r}")

    rr = _dispatch_tool("read_mcp_resource", {"uri": "contractlens://reports/latest"})
    if "requested_uri" not in rr:
        errors.append(f"read_mcp_resource missing requested_uri: {rr!r}")

    rs_uri = _dispatch_tool("read_mcp_resource", {"uri": "contractlens://runs/latest/summary"})
    if rs_uri.get("requested_uri") != "contractlens://runs/latest/summary":
        errors.append(f"read_mcp_resource runs/latest/summary bad uri: {rs_uri!r}")

    ls_runs = _dispatch_tool("list_runs", {"limit": 10})
    if not isinstance(ls_runs.get("runs"), list):
        errors.append(f"list_runs missing runs list: {ls_runs!r}")

    lp = _dispatch_tool("list_mcp_prompts", {})
    if lp.get("count") != 5:
        errors.append(f"list_mcp_prompts: {lp!r}")

    mm_json = json.dumps(
        {"area": "path", "frontend_expects": "x", "backend_provides": "y", "risk": "Low", "suggestion": "z"}
    )
    gp = _dispatch_tool(
        "get_mcp_prompt",
        {"name": "explain_contract_mismatch", "arguments": {"mismatch": mm_json}},
    )
    if not isinstance(gp, dict) or "prompt" not in gp:
        errors.append(f"get_mcp_prompt: {gp!r}")

    tree = mcp_resources.read_resource_by_uri("contractlens://repo/tree")
    if tree.get("status") not in ("ok", "error"):
        errors.append(f"read_resource_by_uri tree: {tree!r}")

    if errors:
        print("[client_smoke_test] FAILED")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("[client_smoke_test] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
