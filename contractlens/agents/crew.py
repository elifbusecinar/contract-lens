"""Agent orchestration: full CrewAI (LLM + tools) when configured; else MCP-backed deterministic steps."""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Callable
from typing import Any

from contractlens.contracts.models import ApiContract, ContractMismatch, RiskSummary
from contractlens.mcp_server import tools as lens_tools

_FALLBACK_ANNOUNCED = False

DET_MSG = "[CrewAI] CrewAI-shaped deterministic fallback enabled (no LLM)"
LLM_MSG = "[CrewAI] Full CrewAI execution enabled (LLM agents + ContractLens tools)"

_REPORT_FN_HOLDER: dict[str, Callable[[], tuple[str, str]]] = {}


def reset_fallback_banner() -> None:
    global _FALLBACK_ANNOUNCED
    _FALLBACK_ANNOUNCED = False


def _crew_import_ok() -> bool:
    try:
        import crewai  # noqa: F401

        return True
    except Exception:
        return False


def should_use_llm_agents(state: dict[str, Any]) -> bool:
    if not state.get("use_llm_agents", False):
        return False
    if not os.getenv("OPENAI_API_KEY", "").strip():
        return False
    return _crew_import_ok()


def _announce_once(trace: list[str], llm: bool) -> None:
    global _FALLBACK_ANNOUNCED
    if _FALLBACK_ANNOUNCED:
        return
    msg = LLM_MSG if llm else DET_MSG
    print(msg)
    trace.append(msg)
    _FALLBACK_ANNOUNCED = True


def _strip_code_fence(raw: str) -> str:
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def _parse_json_loose(raw: str) -> Any:
    s = _strip_code_fence(raw)
    return json.loads(s)


def _crew_final_text(result: Any) -> str:
    if hasattr(result, "tasks_output") and result.tasks_output:
        last = result.tasks_output[-1]
        if getattr(last, "json_dict", None):
            return json.dumps(last.json_dict)
        pyd = getattr(last, "pydantic", None)
        if pyd is not None:
            return pyd.model_dump_json()
        raw = getattr(last, "raw", "") or ""
        if raw:
            return str(raw)
    if hasattr(result, "raw") and result.raw:
        return str(result.raw)
    return str(result)


def _kickoff_single_task_crew(
    *,
    role: str,
    goal: str,
    backstory: str,
    task_description: str,
    expected_output: str,
    tools: list[Any],
    verbose: bool,
) -> str:
    from crewai import Agent, Crew, Process, Task

    agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools,
        verbose=verbose,
        allow_delegation=False,
    )
    task = Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
        tools=tools,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=verbose,
    )
    result = crew.kickoff()
    return _crew_final_text(result)


def run_agent_pipeline(
    state: dict[str, Any],
    *,
    phase: str,
    verbose: bool = False,
    run_scan: Callable[[], list[ApiContract]] | None = None,
    run_compare: Callable[[], tuple[list[ContractMismatch], RiskSummary]] | None = None,
    run_report: Callable[[], tuple[str, str]] | None = None,
) -> tuple[Any, list[str], list[dict[str, Any]]]:
    trace: list[str] = []
    events: list[dict[str, Any]] = []
    use_llm = should_use_llm_agents(state)

    if use_llm:
        _announce_once(trace, llm=True)
    else:
        _announce_once(trace, llm=False)

    if use_llm:
        try:
            return _run_llm_phase(state, phase, verbose, trace, run_scan, run_compare, run_report)
        except Exception as exc:
            print(f"[CrewAI] LLM crew failed ({exc!r}); running deterministic step.")
            trace.append(f"[CrewAI] LLM crew failed; deterministic fallback: {exc!r}")

    return _run_deterministic_phase(state, phase, trace, events, run_scan, run_compare, run_report)


def _run_deterministic_phase(
    state: dict[str, Any],
    phase: str,
    trace: list[str],
    events: list[dict[str, Any]],
    run_scan: Callable[[], list[ApiContract]] | None,
    run_compare: Callable[[], tuple[list[ContractMismatch], RiskSummary]] | None,
    run_report: Callable[[], tuple[str, str]] | None,
) -> tuple[Any, list[str], list[dict[str, Any]]]:
    root = state.get("root_path", "")

    if phase == "frontend":
        print("[CrewAI] Frontend Analyst running")
        trace.append("[CrewAI] Frontend Analyst running")
        t0 = time.perf_counter()
        res = lens_tools.scan_frontend_contracts(root, verbose_log=False)
        ms = (time.perf_counter() - t0) * 1000
        if res.get("status") == "error" or res.get("error"):
            events.append(
                _evt(
                    "Frontend Analyst",
                    "Extract frontend API expectations",
                    "scan_frontend_contracts",
                    f"root={root}",
                    f"error: {res.get('error')}",
                    ms,
                )
            )
            assert run_scan is not None
            out = run_scan()
            return out, trace, events
        contracts = res.get("contracts") or []
        findings = [ApiContract.model_validate(x) for x in contracts]
        events.append(
            _evt(
                "Frontend Analyst",
                "Extract frontend API expectations",
                "scan_frontend_contracts",
                f"root={root}",
                f"Detected {len(findings)} frontend API calls",
                ms,
            )
        )
        return findings, trace, events

    if phase == "backend":
        print("[CrewAI] Backend Analyst running")
        trace.append("[CrewAI] Backend Analyst running")
        t0 = time.perf_counter()
        res = lens_tools.scan_backend_routes(root, verbose_log=False)
        ms = (time.perf_counter() - t0) * 1000
        if res.get("status") == "error" or res.get("error"):
            events.append(
                _evt(
                    "Backend Analyst",
                    "Extract backend routes/DTOs",
                    "scan_backend_routes",
                    f"root={root}",
                    f"error: {res.get('error')}",
                    ms,
                )
            )
            assert run_scan is not None
            return run_scan(), trace, events
        routes = res.get("routes") or []
        findings = [ApiContract.model_validate(x) for x in routes]
        events.append(
            _evt(
                "Backend Analyst",
                "Extract backend routes/DTOs",
                "scan_backend_routes",
                f"root={root}",
                f"Detected {len(findings)} backend routes",
                ms,
            )
        )
        return findings, trace, events

    if phase == "compare":
        print("[CrewAI] Contract Reviewer running")
        trace.append("[CrewAI] Contract Reviewer running")
        fe_d = state.get("frontend_findings") or []
        be_d = state.get("backend_findings") or []
        assert run_compare is not None
        t0 = time.perf_counter()
        ms_list, rs = run_compare()
        ms = (time.perf_counter() - t0) * 1000
        drift_n = sum(1 for m in ms_list if str(m.area).startswith("openapi_vs_code"))
        events.append(
            _evt(
                "Contract Reviewer",
                "Compare contracts (+ OpenAPI drift)",
                "compare_contracts",
                f"fe={len(fe_d)} be={len(be_d)}",
                f"{len(ms_list)} mismatch(es); openapi drift={drift_n}",
                ms,
            )
        )
        return (ms_list, rs), trace, events

    if phase == "report":
        print("[CrewAI] Report Writer running")
        trace.append("[CrewAI] Report Writer running")
        assert run_report is not None
        t0 = time.perf_counter()
        path_md = run_report()
        ms = (time.perf_counter() - t0) * 1000
        path, md = path_md
        events.append(
            _evt(
                "Report Writer",
                "Build Markdown audit report",
                "build_markdown_report",
                f"path={path}",
                f"{len(md)} chars",
                ms,
            )
        )
        return path_md, trace, events

    raise ValueError(f"unknown phase: {phase}")


def _evt(
    agent_name: str,
    role: str,
    tool_used: str,
    input_summary: str,
    output_summary: str,
    duration_ms: float,
) -> dict[str, Any]:
    return {
        "agent_name": agent_name,
        "role": role,
        "tool_used": tool_used,
        "input_summary": input_summary[:300],
        "output_summary": output_summary[:300],
        "duration_ms": round(duration_ms, 2),
    }


def _run_llm_phase(
    state: dict[str, Any],
    phase: str,
    verbose: bool,
    trace: list[str],
    run_scan: Callable[[], list[ApiContract]] | None,
    run_compare: Callable[[], tuple[list[ContractMismatch], RiskSummary]] | None,
    run_report: Callable[[], tuple[str, str]] | None,
) -> tuple[Any, list[str], list[dict[str, Any]]]:
    from crewai.tools import BaseTool

    root = state["root_path"]
    files = state.get("files") or []
    paths_json = json.dumps(files)

    class FrontendScanTool(BaseTool):
        name: str = "contractlens_scan_frontend"
        description: str = (
            "Runs ContractLens deterministic frontend scanner on the repository root and file list. "
            "Invoke once with no arguments; returns a JSON array of API contracts."
        )

        root_path: str = root
        paths_json: str = paths_json

        def _run(self) -> str:
            from contractlens.scanner.frontend_scanner import scan_frontend

            rel = json.loads(self.paths_json)
            rows = [c.model_dump() for c in scan_frontend(self.root_path, rel)]
            return json.dumps(rows)

    class BackendScanTool(BaseTool):
        name: str = "contractlens_scan_backend"
        description: str = (
            "Runs ContractLens deterministic backend scanner. Invoke once; returns JSON array of routes."
        )

        root_path: str = root
        paths_json: str = paths_json

        def _run(self) -> str:
            from contractlens.scanner.backend_scanner import scan_backend

            rel = json.loads(self.paths_json)
            rows = [c.model_dump() for c in scan_backend(self.root_path, rel)]
            return json.dumps(rows)

    fe_payload = json.dumps(state.get("frontend_findings") or [])
    be_payload = json.dumps(state.get("backend_findings") or [])
    oa_payload = json.dumps(state.get("openapi_contracts") or [])

    class CompareTool(BaseTool):
        name: str = "contractlens_compare_contracts"
        description: str = (
            "Compares frontend vs backend contracts using ContractLens comparator, "
            "then merges OpenAPI vs backend drift when openapi_contracts exist in workflow state. "
            "Invoke once; returns JSON object with keys mismatches and risk_summary."
        )

        frontend_json: str = fe_payload
        backend_json: str = be_payload
        openapi_json: str = oa_payload

        def _run(self) -> str:
            from contractlens.contracts.comparator import compare_contracts, summarize_risk_from_mismatches
            from contractlens.openapi import compare_backend_to_openapi

            fe = [ApiContract.model_validate(x) for x in json.loads(self.frontend_json)]
            be = [ApiContract.model_validate(x) for x in json.loads(self.backend_json)]
            oa = [ApiContract.model_validate(x) for x in json.loads(self.openapi_json)]
            base_mm, _ignored = compare_contracts(fe, be)
            drift_mm = compare_backend_to_openapi(be, oa) if oa else []
            merged = list(base_mm) + drift_mm
            summary = summarize_risk_from_mismatches(merged)
            return json.dumps(
                {
                    "mismatches": [m.model_dump() for m in merged],
                    "risk_summary": summary.model_dump(),
                }
            )

    holder_key = "report"

    class FinalizeReportTool(BaseTool):
        name: str = "contractlens_finalize_report"
        description: str = (
            "Builds the Markdown audit via ContractLens report pipeline (deterministic writer). "
            "Invoke once; returns JSON with path and markdown."
        )

        holder_slot: str = holder_key

        def _run(self) -> str:
            fn = _REPORT_FN_HOLDER.get(self.holder_slot)
            if fn is None:
                return json.dumps({"error": "report runner not registered"})
            path, md = fn()
            return json.dumps({"path": path, "markdown": md})

    events: list[dict[str, Any]] = []

    if phase == "frontend":
        print("[CrewAI] Frontend Analyst running (LLM + tool)")
        trace.append("[CrewAI] Frontend Analyst running (LLM + tool)")
        assert run_scan is not None
        tool = FrontendScanTool()
        t0 = time.perf_counter()
        raw = _kickoff_single_task_crew(
            role="Frontend Analyst",
            goal="Produce frontend API contract JSON using ContractLens.",
            backstory="Always call contractlens_scan_frontend exactly once. Never invent endpoints.",
            task_description="Use tool contractlens_scan_frontend once. Output ONLY valid JSON array from tool.",
            expected_output="JSON array of contracts.",
            tools=[tool],
            verbose=verbose,
        )
        ms = (time.perf_counter() - t0) * 1000
        try:
            data = _parse_json_loose(raw)
            findings = [ApiContract.model_validate(x) for x in data]
            events.append(
                _evt("Frontend Analyst", "Extract frontend API expectations", "contractlens_scan_frontend", root, f"{len(findings)} calls", ms)
            )
            return findings, trace, events
        except Exception:
            events.append(_evt("Frontend Analyst", "Extract frontend API expectations", "contractlens_scan_frontend", root, "parse fallback", ms))
            return run_scan(), trace, events

    if phase == "backend":
        print("[CrewAI] Backend Analyst running (LLM + tool)")
        trace.append("[CrewAI] Backend Analyst running (LLM + tool)")
        assert run_scan is not None
        tool = BackendScanTool()
        t0 = time.perf_counter()
        raw = _kickoff_single_task_crew(
            role="Backend Analyst",
            goal="Produce backend route JSON using ContractLens.",
            backstory="Always call contractlens_scan_backend exactly once.",
            task_description="Use contractlens_scan_backend once. Output ONLY tool JSON.",
            expected_output="JSON array of backend contracts.",
            tools=[tool],
            verbose=verbose,
        )
        ms = (time.perf_counter() - t0) * 1000
        try:
            data = _parse_json_loose(raw)
            findings = [ApiContract.model_validate(x) for x in data]
            events.append(
                _evt("Backend Analyst", "Extract backend routes/DTOs", "contractlens_scan_backend", root, f"{len(findings)} routes", ms)
            )
            return findings, trace, events
        except Exception:
            events.append(_evt("Backend Analyst", "Extract backend routes/DTOs", "contractlens_scan_backend", root, "parse fallback", ms))
            return run_scan(), trace, events

    if phase == "compare":
        print("[CrewAI] Contract Reviewer running (LLM + tool)")
        trace.append("[CrewAI] Contract Reviewer running (LLM + tool)")
        assert run_compare is not None
        tool = CompareTool()
        t0 = time.perf_counter()
        raw = _kickoff_single_task_crew(
            role="Contract Reviewer",
            goal="Compare frontend vs backend contracts using ContractLens.",
            backstory="Always call contractlens_compare_contracts exactly once.",
            task_description="Use contractlens_compare_contracts once. Output ONLY tool JSON.",
            expected_output='JSON with keys "mismatches" and "risk_summary".',
            tools=[tool],
            verbose=verbose,
        )
        ms = (time.perf_counter() - t0) * 1000
        try:
            data = _parse_json_loose(raw)
            ms_list = [ContractMismatch.model_validate(x) for x in data["mismatches"]]
            rs = RiskSummary.model_validate(data["risk_summary"])
            events.append(
                _evt(
                    "Contract Reviewer",
                    "Compare frontend vs backend contracts",
                    "contractlens_compare_contracts",
                    "FE/BE payloads",
                    f"{len(ms_list)} mismatches",
                    ms,
                )
            )
            return (ms_list, rs), trace, events
        except Exception:
            events.append(
                _evt("Contract Reviewer", "Compare frontend vs backend contracts", "contractlens_compare_contracts", "FE/BE payloads", "fallback", ms)
            )
            return run_compare(), trace, events

    if phase == "report":
        print("[CrewAI] Report Writer running (LLM + tool)")
        trace.append("[CrewAI] Report Writer running (LLM + tool)")
        assert run_report is not None
        try:
            _REPORT_FN_HOLDER[holder_key] = run_report
            tool = FinalizeReportTool()
            t0 = time.perf_counter()
            raw = _kickoff_single_task_crew(
                role="Report Writer",
                goal="Finalize Markdown audit report.",
                backstory="Always call contractlens_finalize_report exactly once.",
                task_description="Use contractlens_finalize_report once. Output ONLY tool JSON.",
                expected_output='JSON with keys "path" and "markdown".',
                tools=[tool],
                verbose=verbose,
            )
            ms = (time.perf_counter() - t0) * 1000
            data = _parse_json_loose(raw)
            events.append(_evt("Report Writer", "Build Markdown audit report", "contractlens_finalize_report", "report", "ok", ms))
            return (data["path"], data["markdown"]), trace, events
        except Exception:
            ms = (time.perf_counter() - t0) * 1000
            events.append(_evt("Report Writer", "Build Markdown audit report", "contractlens_finalize_report", "report", "fallback", ms))
            return run_report(), trace, events
        finally:
            _REPORT_FN_HOLDER.pop(holder_key, None)

    raise ValueError(f"unknown phase: {phase}")
