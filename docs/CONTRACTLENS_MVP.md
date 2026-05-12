# MVP presenter cheat sheet

**Story:** MCP tools touch the repo → LangGraph (or linear fallback) walks nodes → CrewAI-shaped roles each run real Python steps → Markdown report.

**Commands:**

```bash
pip install -r requirements.txt
python -m contractlens.mcp_server.tools_demo
python -m contractlens.main --feature "Create Project + Upload File" --root examples/sample_project --verbose
python -m contractlens.mcp_server.server   # blocks — MCP client on stdio
```

**Honesty:** without `OPENAI_API_KEY`, agents stay deterministic. With the key, CrewAI runs real LLMs but calls ContractLens tools for factual scans.

**Offline demo:** pass `--deterministic-agents` so behaviour stays deterministic even if a key is present.

**Sample drift:** upload path `/files` vs `/models`, fields `id`/`thumbnailUrl` vs `projectId`/`thumbnail_path`, detail `name` vs `title`.
