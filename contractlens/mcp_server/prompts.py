"""Reusable MCP-style prompt templates (strings only; no LLM calls)."""

from __future__ import annotations

import json
from typing import Any


def audit_feature_contract(*, feature_name: str, frontend_contracts: list[Any], backend_contracts: list[Any]) -> str:
    return (
        f"You are auditing API drift for feature: {feature_name!r}.\n\n"
        f"Frontend contracts (JSON):\n{json.dumps(frontend_contracts, indent=2)}\n\n"
        f"Backend contracts (JSON):\n{json.dumps(backend_contracts, indent=2)}\n\n"
        "Compare paths, methods, payloads, response shapes, and auth expectations.\n"
    )


def explain_contract_mismatch(*, mismatch: dict[str, Any]) -> str:
    return (
        "Explain this contract mismatch to an engineer.\n\n"
        f"{json.dumps(mismatch, indent=2)}\n\n"
        "Cover risk to runtime behaviour and whether clients break silently.\n"
    )


def generate_safe_fix_plan(*, mismatches: list[dict[str, Any]]) -> str:
    return (
        "Produce an incremental fix plan ordered by severity.\n\n"
        f"{json.dumps(mismatches, indent=2)}\n\n"
        "Prefer backwards-compatible aliases, schema versioning, or small coordinated edits.\n"
    )


def create_pr_review_comment(*, report_summary: str, mismatches: list[dict[str, Any]]) -> str:
    return (
        "Draft a concise PR review comment.\n\n"
        f"Summary:\n{report_summary}\n\n"
        f"Mismatches:\n{json.dumps(mismatches, indent=2)}\n"
    )


def summarize_agent_run(
    *,
    execution_trace: list[Any],
    mcp_trace: list[Any],
    agent_trace: list[Any],
) -> str:
    return (
        "Summarize how this ContractLens run behaved.\n\n"
        f"LangGraph trace:\n{json.dumps(execution_trace, indent=2)}\n\n"
        f"MCP trace:\n{json.dumps(mcp_trace, indent=2)}\n\n"
        f"Agent trace (legacy strings):\n{json.dumps(agent_trace, indent=2)}\n"
    )


PROMPT_NAMES = [
    "audit_feature_contract",
    "explain_contract_mismatch",
    "generate_safe_fix_plan",
    "create_pr_review_comment",
    "summarize_agent_run",
]

_JSON_ARGUMENT_KEYS = frozenset(
    {
        "frontend_contracts",
        "backend_contracts",
        "mismatch",
        "mismatches",
        "execution_trace",
        "mcp_trace",
        "agent_trace",
    }
)


def coerce_prompt_arguments_from_strings(arguments: dict[str, str] | None) -> dict[str, Any]:
    """MCP prompts/get passes arguments as dict[str, str]; parse embedded JSON where needed."""
    if not arguments:
        return {}
    out: dict[str, Any] = {}
    for k, v in arguments.items():
        if k in _JSON_ARGUMENT_KEYS or (isinstance(v, str) and v.strip().startswith(("{", "["))):
            try:
                out[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                out[k] = v
        else:
            out[k] = v
    return out


def render_named_prompt(name: str, arguments: dict[str, Any] | None) -> str:
    """Return prompt template text for a registered prompt name (no LLM)."""
    args = arguments or {}
    if name == "audit_feature_contract":
        fe = args.get("frontend_contracts") or []
        be = args.get("backend_contracts") or []
        if not isinstance(fe, list):
            fe = []
        if not isinstance(be, list):
            be = []
        return audit_feature_contract(
            feature_name=str(args.get("feature_name", "")),
            frontend_contracts=fe,
            backend_contracts=be,
        )
    if name == "explain_contract_mismatch":
        mm = args.get("mismatch") if isinstance(args.get("mismatch"), dict) else {}
        return explain_contract_mismatch(mismatch=mm)
    if name == "generate_safe_fix_plan":
        ms = args.get("mismatches") or []
        if not isinstance(ms, list):
            ms = []
        ms_dicts = [x for x in ms if isinstance(x, dict)]
        return generate_safe_fix_plan(mismatches=ms_dicts)
    if name == "create_pr_review_comment":
        ms = args.get("mismatches") or []
        if not isinstance(ms, list):
            ms = []
        ms_dicts = [x for x in ms if isinstance(x, dict)]
        return create_pr_review_comment(
            report_summary=str(args.get("report_summary", "")),
            mismatches=ms_dicts,
        )
    if name == "summarize_agent_run":
        et = args.get("execution_trace") or []
        mt = args.get("mcp_trace") or []
        at = args.get("agent_trace") or []
        if not isinstance(et, list):
            et = []
        if not isinstance(mt, list):
            mt = []
        if not isinstance(at, list):
            at = []
        return summarize_agent_run(execution_trace=et, mcp_trace=mt, agent_trace=at)
    raise ValueError(f"unknown prompt: {name!r}")
