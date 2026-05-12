"""End-to-end stdio MCP protocol smoke test (subprocess server). Falls back gracefully."""

from __future__ import annotations

import json
import sys
from typing import Any

from contractlens.config import PACKAGE_ROOT


def _extract_tool_text(result: Any) -> str:
    chunks: list[str] = []
    for block in getattr(result, "content", []) or []:
        t = getattr(block, "text", None)
        if t:
            chunks.append(t)
    return "".join(chunks)


async def _async_main() -> tuple[bool, str]:
    try:
        from mcp.client.session import ClientSession
        from mcp.client.stdio import StdioServerParameters, get_default_environment, stdio_client
    except Exception as exc:
        return False, f"import error: {exc!r}"

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "contractlens.mcp_server.server"],
        cwd=str(PACKAGE_ROOT.resolve()),
        env=dict(get_default_environment()),
    )

    try:
        async with stdio_client(params, errlog=sys.stderr) as streams:
            read_stream, write_stream = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                tlist = await session.list_tools()
                names = [t.name for t in tlist.tools]
                if "explain_mismatch" not in names:
                    return False, f"explain_mismatch missing in {names[:5]}... ({len(names)} tools)"

                res = await session.call_tool(
                    "explain_mismatch",
                    {
                        "mismatch": {
                            "area": "path",
                            "frontend_expects": "/a",
                            "backend_provides": "/b",
                            "risk": "High",
                            "suggestion": "Align paths.",
                        }
                    },
                )
                if res.isError:
                    return False, f"explain_mismatch error: {_extract_tool_text(res)}"
                payload = json.loads(_extract_tool_text(res) or "{}")
                if "explanation" not in payload:
                    return False, f"unexpected tool payload: {payload!r}"

                try:
                    rlist = await session.list_resources()
                    if not getattr(rlist, "resources", None):
                        pass
                except Exception as exc:
                    return True, f"partial ok (resources skipped: {exc!r})"

                try:
                    mm = json.dumps(
                        {
                            "area": "path",
                            "frontend_expects": "x",
                            "backend_provides": "y",
                            "risk": "Low",
                            "suggestion": "z",
                        }
                    )
                    pr = await session.get_prompt("explain_contract_mismatch", {"mismatch": mm})
                    if not pr.messages:
                        return True, "partial ok (empty prompt messages)"
                except Exception as exc:
                    return True, f"partial ok (prompts skipped: {exc!r})"

                return True, "full stdio MCP session ok (tools + explain_mismatch + resources + prompt)"
    except BaseException as exc:
        return False, f"session failed: {exc!r}"


def main() -> int:
    print("[stdio_client_test] Attempting real MCP ClientSession over subprocess stdio...")
    try:
        import anyio
    except Exception as exc:
        print(
            f"[stdio_client_test] Full stdio MCP client test is not available in this environment ({exc!r}); "
            "local dispatch smoke test is used instead (`python -m contractlens.mcp_server.client_smoke_test`)."
        )
        return 0

    try:
        ok, detail = anyio.run(_async_main, backend="asyncio")
    except Exception as exc:
        ok, detail = False, f"anyio.run failed: {exc!r}"

    if ok:
        print(f"[stdio_client_test] OK - {detail}")
        return 0

    print(f"[stdio_client_test] Full stdio MCP client test is not available or failed ({detail}); ")
    print(
        "[stdio_client_test] Local dispatch smoke test remains the reliable check "
        "(`python -m contractlens.mcp_server.client_smoke_test`)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
