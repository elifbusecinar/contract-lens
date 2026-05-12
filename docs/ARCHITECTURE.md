# Architecture (one slide)

```text
main.py
  → LangGraph StateGraph OR same nodes sequentially (stdio MCP tools unchanged)
      → Agents: CrewAI + LLM + ContractLens tools (if OPENAI_API_KEY), else deterministic specialists
      → contractlens-reports/*.md
```

- **MCP:** `mcp_server/tools.py` (workflow imports directly); optional stdio server wraps the same functions.
- **LangGraph:** `workflow/graph.py`; falls back sequentially if import/invoke fails (`--verbose` shows why).
- **Agents:** `agents/crew.py` — LLM path runs **one agent / one task per phase**, each tool calling **real** scanners/comparator/report builder.
