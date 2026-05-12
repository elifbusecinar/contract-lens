"""Generate human-readable MCP documentation for presentations."""

from __future__ import annotations

import json
from pathlib import Path

from contractlens.config import PACKAGE_ROOT

from contractlens.mcp_server.capability_manifest import build_capability_manifest


def write_mcp_capabilities_md(*, output: Path | None = None) -> Path:
    man = build_capability_manifest()
    dest = output or (PACKAGE_ROOT / "docs" / "MCP_CAPABILITIES.md")
    dest.parent.mkdir(parents=True, exist_ok=True)

    tools_rows = "\n".join(
        f"| `{t['name']}` | {t.get('description', '')} |" for t in man["tools"]
    )
    res_rows = "\n".join(
        f"| `{r['uri']}` | {r.get('description', '')} |" for r in man["resources"]
    )
    pr_rows = "\n".join(
        f"| `{p['name']}` | {p.get('description', '')} |" for p in man["prompts"]
    )

    perm = man["permissions"]
    ign = perm.get("ignored_directory_names") or []
    ign_preview = ", ".join(ign[:12])
    if len(ign) > 12:
        ign_preview += ", …"
    perm_lines = (
        f"- **read_default:** {perm.get('read_default')}\n"
        f"- **write_requires_allow_write:** {perm.get('write_requires_allow_write')}\n"
        f"- **path_traversal_blocked:** {perm.get('path_traversal_blocked')}\n"
        f"- **ignored_directory_names:** {ign_preview}"
    )

    art = man["artifacts"]
    art_lines = "\n".join(f"- `{v}`" for v in art.values())

    lim = "\n".join(f"- {x}" for x in man["limitations"])

    body = f"""# ContractLens — MCP capabilities

Generated reference for the MCP-compatible layer (stdio server + local tools).

## Server

- **Name:** {man['server_name']}
- **Version:** `{man['server_version']}`

## Tools ({len(man['tools'])})

| Tool | Description |
| --- | --- |
{tools_rows}

### Example tool calls (JSON bodies)

**`explain_mismatch`**

```json
{{
  "mismatch": {{
    "area": "endpoint_path",
    "frontend_expects": "/api/projects/{{id}}/files",
    "backend_provides": "/api/projects/{{projectId}}/models",
    "risk": "High",
    "suggestion": "Align route templates or add a compatibility alias."
  }}
}}
```

**`read_mcp_resource`**

```json
{{ "uri": "contractlens://reports/latest" }}
```

## Resources ({len(man['resources'])})

| URI | Description |
| --- | --- |
{res_rows}

## Prompts ({len(man['prompts'])})

| Name | Description |
| --- | --- |
{pr_rows}

## Permission model

{perm_lines}

## Artifact locations (relative to repo root)

{art_lines}

## Current limitations

{lim}

## Commands

```bash
python -m contractlens.mcp_server.capability_manifest
python -m contractlens.mcp_server.export_docs
python -m contractlens.mcp_server.inspect_mcp
python -m contractlens.mcp_server.stdio_client_test
python -m contractlens.mcp_server.client_smoke_test
```
"""

    dest.write_text(body, encoding="utf-8")
    return dest


def main() -> None:
    path = write_mcp_capabilities_md()
    print(f"[export_docs] Wrote {path.relative_to(PACKAGE_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
