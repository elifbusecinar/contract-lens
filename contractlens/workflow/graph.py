"""LangGraph StateGraph when reducers work; otherwise sequential orchestration (same logs)."""

from __future__ import annotations

from operator import add
from pathlib import Path
from typing import Annotated, Any, TypedDict

from contractlens.agents.crew import run_agent_pipeline
from contractlens.auth import compare_auth_contracts as compare_auth_contract_signals
from contractlens.auth import scan_backend_auth, scan_frontend_auth
from contractlens.git.diff import resolve_changed_only_scan_files
from contractlens.config import default_html_report_path, default_report_path
from contractlens.contracts.comparator import compare_contracts, summarize_risk_from_mismatches
from contractlens.contracts.models import ApiContract
from contractlens.docs_analyzer import compare_documentation_drift, scan_documentation
from contractlens.openapi import collect_openapi_contracts, compare_backend_to_openapi
from contractlens.mcp_server import tools as mcp_tools
from contractlens.reporting.html_report import build_html_report
from contractlens.reporting.markdown_report import build_markdown_report
from contractlens.reporting.runtime_probe import run_runtime_http_probe
from contractlens.scanner.backend_scanner import scan_backend
from contractlens.scanner.frontend_scanner import scan_frontend


class LGState(TypedDict, total=False):
    feature_name: str
    root_path: str
    verbose: bool
    mode: str
    report_output_dir: str
    use_llm_agents: bool
    mcp_allow_write: bool
    run_id: str
    run_started_at: str

    files: list[str]
    openapi_limit_to_scan_files: bool
    changed_only: bool
    fallback_full_scan: bool
    git_changed_only_requested: bool
    git_is_repository: bool
    git_graceful_full_scan_not_git: bool
    git_fallback_full_scan_used: bool
    git_changed_files_count: int
    git_diff_notes: list[str]
    git_files_considered: list[str]
    frontend_findings: list[dict[str, Any]]
    backend_findings: list[dict[str, Any]]
    openapi_spec_paths: list[str]
    openapi_contracts: list[dict[str, Any]]
    openapi_notes: list[str]
    frontend_auth_findings: list[dict[str, Any]]
    backend_auth_findings: list[dict[str, Any]]
    auth_mismatches: list[dict[str, Any]]
    documentation_claims: list[dict[str, Any]]
    documentation_drift: list[dict[str, Any]]
    mismatches: list[dict[str, Any]]
    risk_summary: dict[str, int]
    report_path: str
    report_markdown: str
    generate_html: bool
    html_report_path: str
    runtime_probe_base_url: str
    runtime_probe_result: dict[str, Any]
    scan_cache_enabled: bool

    execution_trace: Annotated[list[str], add]
    mcp_trace: Annotated[list[str], add]
    agent_trace: Annotated[list[str], add]
    agent_events: Annotated[list[dict[str, Any]], add]
    errors: Annotated[list[str], add]


def _log_langgraph(verbose: bool, node: str) -> None:
    if verbose:
        print(f"[LangGraph] {node}")


def node_select_feature(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "select_feature")
    fe = state.get("feature_name", "")
    return {"execution_trace": [f"[LangGraph] select_feature: feature={fe!r}"]}


def node_scan_repository(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    root = state["root_path"]
    res = mcp_tools.list_project_files(root, verbose_log=verbose)
    _log_langgraph(verbose, "scan_repository")
    files = res.get("files") or []
    msg = f"list_project_files root={root!r} -> {len(files)} files"
    err = res.get("error")
    out: dict[str, Any] = {
        "files": files,
        "execution_trace": [f"[LangGraph] scan_repository: {len(files)} files"],
        "mcp_trace": [msg],
    }
    if err:
        out["errors"] = [str(err)]
    return out


def node_apply_git_changed_filter(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "apply_git_changed_filter")
    root = Path(state["root_path"]).resolve()
    full_files = list(state.get("files") or [])
    decision = resolve_changed_only_scan_files(
        root,
        full_files,
        changed_only=bool(state.get("changed_only")),
        fallback_full_scan=bool(state.get("fallback_full_scan")),
        include_cached=True,
        verbose=verbose,
    )
    trace = [
        f"[LangGraph] apply_git_changed_filter: "
        f"changed_only={decision.git_changed_only_requested} "
        f"narrow_openapi={decision.openapi_limit_to_scan_files} "
        f"scan_files={len(decision.files_for_scanners)}",
    ]
    trace.extend(f"[LangGraph] git note: {n}" for n in decision.notes)
    return {
        "files": decision.files_for_scanners,
        "openapi_limit_to_scan_files": decision.openapi_limit_to_scan_files,
        "git_changed_only_requested": decision.git_changed_only_requested,
        "git_is_repository": decision.git_is_repository,
        "git_graceful_full_scan_not_git": decision.git_graceful_full_scan_not_git,
        "git_fallback_full_scan_used": decision.git_fallback_full_scan_used,
        "git_changed_files_count": decision.git_changed_files_count,
        "git_diff_notes": list(decision.notes),
        "git_files_considered": list(decision.files_for_scanners),
        "execution_trace": trace,
    }


def node_scan_openapi(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "scan_openapi")
    root = state["root_path"]
    limit: frozenset[str] | None = None
    if bool(state.get("openapi_limit_to_scan_files")):
        limit = frozenset(state.get("files") or [])
    oa_contracts, rel_specs, notes = collect_openapi_contracts(root, allowed_spec_relative_paths=limit)
    payload = [c.model_dump() for c in oa_contracts]
    trace = [
        f"[LangGraph] scan_openapi: {len(rel_specs)} spec file(s), {len(payload)} operation(s) parsed",
    ]
    trace.extend(f"[LangGraph] scan_openapi note: {n}" for n in notes)
    if verbose:
        for n in notes:
            print(f"[LangGraph] scan_openapi: {n}")
    return {
        "openapi_spec_paths": rel_specs,
        "openapi_contracts": payload,
        "openapi_notes": notes,
        "execution_trace": trace,
    }


def node_analyze_frontend(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "analyze_frontend")
    root = state["root_path"]
    files = state.get("files") or []

    def run_scan() -> list[ApiContract]:
        return scan_frontend(root, files, use_scan_cache=bool(state.get("scan_cache_enabled")))

    findings, agent_messages, agent_events = run_agent_pipeline(
        state,
        phase="frontend",
        run_scan=run_scan,
        verbose=verbose,
    )
    payload = [f.model_dump() for f in findings]
    trace = [f"[LangGraph] analyze_frontend: {len(payload)} API call(s)"]
    trace.extend(agent_messages)
    return {
        "frontend_findings": payload,
        "execution_trace": trace,
        "agent_trace": agent_messages,
        "agent_events": agent_events,
    }


def node_analyze_backend(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "analyze_backend")
    root = state["root_path"]
    files = state.get("files") or []

    def run_scan() -> list[ApiContract]:
        return scan_backend(root, files, use_scan_cache=bool(state.get("scan_cache_enabled")))

    findings, agent_messages, agent_events = run_agent_pipeline(
        state,
        phase="backend",
        run_scan=run_scan,
        verbose=verbose,
    )
    payload = [f.model_dump() for f in findings]
    trace = [f"[LangGraph] analyze_backend: {len(payload)} route(s)"]
    trace.extend(agent_messages)
    return {
        "backend_findings": payload,
        "execution_trace": trace,
        "agent_trace": agent_messages,
        "agent_events": agent_events,
    }


def node_analyze_auth(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "analyze_auth")
    root = state["root_path"]
    files = state.get("files") or []
    fe_auth = scan_frontend_auth(root, files)
    be_auth = scan_backend_auth(root, files)
    fe_c = [ApiContract.model_validate(x) for x in state.get("frontend_findings") or []]
    be_c = [ApiContract.model_validate(x) for x in state.get("backend_findings") or []]
    auth_mm = compare_auth_contract_signals(fe_c, be_c, fe_auth, be_auth)
    trace = [
        f"[LangGraph] analyze_auth: frontend_auth_signals={len(fe_auth)} "
        f"backend_auth_signals={len(be_auth)} auth_mismatch_rows={len(auth_mm)}",
    ]
    return {
        "frontend_auth_findings": [x.model_dump() for x in fe_auth],
        "backend_auth_findings": [x.model_dump() for x in be_auth],
        "auth_mismatches": [x.model_dump() for x in auth_mm],
        "execution_trace": trace,
    }


def node_compare_contracts(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "compare_contracts")

    def run_compare() -> tuple[list, Any]:
        fe = [ApiContract.model_validate(x) for x in state.get("frontend_findings") or []]
        be = [ApiContract.model_validate(x) for x in state.get("backend_findings") or []]
        base_mm, _base_summary = compare_contracts(fe, be)
        oa_payload = state.get("openapi_contracts") or []
        oa = [ApiContract.model_validate(x) for x in oa_payload]
        drift_mm = compare_backend_to_openapi(be, oa) if oa else []
        merged_mm = list(base_mm) + drift_mm
        summary = summarize_risk_from_mismatches(merged_mm)
        return merged_mm, summary

    (_mismatches, _summary), agent_messages, agent_events = run_agent_pipeline(
        state,
        phase="compare",
        run_compare=run_compare,
        verbose=verbose,
    )
    mismatches = [m.model_dump() for m in _mismatches]
    risk = _summary.model_dump()
    drift_n = sum(
        1
        for m in mismatches
        if isinstance(m, dict) and str(m.get("area", "")).startswith("openapi_vs_code")
    )
    trace = [
        f"[LangGraph] compare_contracts: {len(mismatches)} mismatch(es) "
        f"({drift_n} OpenAPI/code drift); "
        f"risk High={risk['high']} Medium={risk['medium']} Low={risk['low']}"
    ]
    trace.extend(agent_messages)
    return {
        "mismatches": mismatches,
        "risk_summary": risk,
        "execution_trace": trace,
        "agent_trace": agent_messages,
        "agent_events": agent_events,
    }


def node_analyze_documentation(state: LGState) -> dict[str, Any]:
    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "analyze_documentation")
    root = state["root_path"]
    files = state.get("files") or []
    claims = scan_documentation(root, files)
    fe_c = [ApiContract.model_validate(x) for x in state.get("frontend_findings") or []]
    be_c = [ApiContract.model_validate(x) for x in state.get("backend_findings") or []]
    oa_c = [ApiContract.model_validate(x) for x in state.get("openapi_contracts") or []]
    drift = compare_documentation_drift(fe_c, be_c, oa_c, claims, repo_root=root)
    trace = [
        f"[LangGraph] analyze_documentation: doc_claims={len(claims)} documentation_drift_rows={len(drift)}",
    ]
    return {
        "documentation_claims": [c.model_dump() for c in claims],
        "documentation_drift": [d.model_dump() for d in drift],
        "execution_trace": trace,
    }


def node_generate_report(state: LGState) -> dict[str, Any]:
    import sys

    verbose = bool(state.get("verbose"))
    _log_langgraph(verbose, "generate_report")

    from pathlib import Path

    ro = state.get("report_output_dir")
    report_dir = Path(ro).resolve() if ro else default_report_path(state["feature_name"]).parent
    path = str(default_report_path(state["feature_name"], report_dir))

    probe_base = (state.get("runtime_probe_base_url") or "").strip()
    probe_result = run_runtime_http_probe(probe_base) if probe_base else {"configured": False}
    trace_probe: list[str] = []
    if probe_base:
        trace_probe = [
            f"[LangGraph] runtime_probe: GET {probe_base!r} "
            f"ok={bool(probe_result.get('ok'))} "
            f"status={probe_result.get('status_code')!r}",
        ]
        if probe_result.get("ok"):
            print(f"[Probe] Reachable: {probe_base}")
        else:
            err = probe_result.get("error") or "unknown error"
            print(f"[Probe] Failed ({probe_base}): {err}", file=sys.stderr)

    state_for_report: dict[str, Any] = {
        **dict(state),
        "runtime_probe_base_url": probe_base,
        "runtime_probe_result": probe_result,
        "execution_trace": list(state.get("execution_trace") or []) + trace_probe,
    }

    def preview(
        extra_mcp_line: str,
        *,
        agent_events_extra: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        base_exec = list(state_for_report.get("execution_trace") or [])
        base_ag = list(state_for_report.get("agent_trace") or [])
        base_mcp = list(state_for_report.get("mcp_trace") or [])
        pending_agent = ["[CrewAI] Report Writer running"]
        exec_preview = base_exec + [f"[LangGraph] generate_report -> {path}", *pending_agent]
        agent_preview = base_ag + pending_agent
        mcp_preview = base_mcp + [extra_mcp_line]
        ae = list(state_for_report.get("agent_events") or [])
        if agent_events_extra is not None:
            ae = ae + agent_events_extra
        return {
            **dict(state_for_report),
            "execution_trace": exec_preview,
            "agent_trace": agent_preview,
            "mcp_trace": mcp_preview,
            "agent_events": ae,
        }

    def run_report() -> tuple[str, str]:
        md = build_markdown_report(preview(f"write_report path={path!r}"))
        return path, md

    (written_path, md), agent_messages, agent_events = run_agent_pipeline(
        state,
        phase="report",
        run_report=run_report,
        verbose=verbose,
    )
    path = written_path or path

    allow_w = bool(state.get("mcp_allow_write", True))
    wr = mcp_tools.write_report(path, md, verbose_log=verbose, allow_write=allow_w)
    ok = wr.get("success")

    md_final = build_markdown_report(
        preview(
            f"write_report path={path!r} success={ok}",
            agent_events_extra=agent_events,
        )
    )
    if md_final != md:
        mcp_tools.write_report(path, md_final, verbose_log=False, allow_write=allow_w)
        md = md_final

    trace_tail = [f"[LangGraph] generate_report -> {path}"]
    trace_tail.extend(agent_messages)

    exec_snap = list(state_for_report.get("execution_trace") or []) + trace_tail
    agent_trace_snap = list(state_for_report.get("agent_trace") or []) + agent_messages

    html_path_str = ""
    mcp_lines = [f"write_report path={path!r} success={ok}"]
    if state.get("generate_html"):
        html_path = default_html_report_path(state["feature_name"], report_dir)
        html_path_str = str(html_path)
        merged_for_html = {
            **state_for_report,
            "report_path": path,
            "report_markdown": md,
            "execution_trace": exec_snap,
            "agent_trace": agent_trace_snap,
            "mcp_trace": list(state_for_report.get("mcp_trace") or []) + mcp_lines,
            "html_report_path": html_path_str,
        }
        html_doc = build_html_report(merged_for_html)
        wr_html = mcp_tools.write_report(html_path_str, html_doc, verbose_log=verbose, allow_write=allow_w)
        ok_html = wr_html.get("success")
        mcp_lines.append(f"write_report path={html_path_str!r} success={ok_html}")

    from contractlens.mcp_server import run_store

    try:
        run_store.snapshot_run(
            feature_name=state.get("feature_name", ""),
            root_path=state.get("root_path", ""),
            execution_trace=exec_snap,
            agent_trace=agent_trace_snap,
            frontend_contracts=list(state.get("frontend_findings") or []),
            backend_contracts=list(state.get("backend_findings") or []),
            mismatches=list(state.get("mismatches") or []),
            report_path=path,
            report_markdown=md,
            run_id=state.get("run_id"),
            started_at=state.get("run_started_at"),
            runtime_probe_base_url=probe_base,
            runtime_probe_result=probe_result,
        )
    except OSError:
        pass

    return {
        "report_path": path,
        "report_markdown": md,
        "execution_trace": trace_probe + trace_tail,
        "agent_trace": agent_messages,
        "agent_events": agent_events,
        "mcp_trace": mcp_lines,
        "html_report_path": html_path_str,
        "runtime_probe_base_url": probe_base,
        "runtime_probe_result": probe_result,
    }


def _merge_lists(existing: list[Any], new_items: list[Any]) -> list[Any]:
    return existing + new_items


def _reduce_state(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    out = {**left}
    for k, v in right.items():
        if k in ("execution_trace", "mcp_trace", "agent_trace", "agent_events", "errors") and isinstance(v, list):
            out[k] = _merge_lists(list(left.get(k) or []), v)
        else:
            out[k] = v
    return out


def _run_sequential(initial: dict[str, Any]) -> dict[str, Any]:
    state = {**initial}
    steps = [
        node_select_feature,
        node_scan_repository,
        node_apply_git_changed_filter,
        node_scan_openapi,
        node_analyze_frontend,
        node_analyze_backend,
        node_analyze_auth,
        node_compare_contracts,
        node_analyze_documentation,
        node_generate_report,
    ]
    for fn in steps:
        try:
            patch = fn(state)  # type: ignore[arg-type]
            state = _reduce_state(state, patch)
        except Exception as exc:
            err = f"{fn.__name__}: {exc}"
            state = _reduce_state(state, {"errors": [err]})
            break
    return state


def _seed_run_meta(initial: dict[str, Any]) -> dict[str, Any]:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    rid = initial.get("run_id") or f"run-{now.strftime('%Y%m%d-%H%M%S')}"
    started = initial.get("run_started_at") or now.isoformat()
    return {**initial, "run_id": rid, "run_started_at": started}


def run_workflow(initial: dict[str, Any]) -> dict[str, Any]:
    from contractlens.mcp_server import audit_log

    seeded = _seed_run_meta(initial)
    tok = audit_log.attach_run_context(str(seeded["run_id"]))
    try:
        return _run_workflow_body(seeded)
    finally:
        audit_log.detach_run_context(tok)


def _run_workflow_body(initial: dict[str, Any]) -> dict[str, Any]:
    """Prefer LangGraph StateGraph with list reducers for traces; fall back to sequential."""
    verbose = bool(initial.get("verbose"))
    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except Exception:
        if verbose:
            print("[LangGraph] Sequential workflow (LangGraph import unavailable)")
        return _run_sequential(initial)

    graph = StateGraph(LGState)
    graph.add_node("select_feature", node_select_feature)
    graph.add_node("scan_repository", node_scan_repository)
    graph.add_node("apply_git_changed_filter", node_apply_git_changed_filter)
    graph.add_node("scan_openapi", node_scan_openapi)
    graph.add_node("analyze_frontend", node_analyze_frontend)
    graph.add_node("analyze_backend", node_analyze_backend)
    graph.add_node("analyze_auth", node_analyze_auth)
    graph.add_node("compare_contracts", node_compare_contracts)
    graph.add_node("analyze_documentation", node_analyze_documentation)
    graph.add_node("generate_report", node_generate_report)

    graph.set_entry_point("select_feature")
    graph.add_edge("select_feature", "scan_repository")
    graph.add_edge("scan_repository", "apply_git_changed_filter")
    graph.add_edge("apply_git_changed_filter", "scan_openapi")
    graph.add_edge("scan_openapi", "analyze_frontend")
    graph.add_edge("analyze_frontend", "analyze_backend")
    graph.add_edge("analyze_backend", "analyze_auth")
    graph.add_edge("analyze_auth", "compare_contracts")
    graph.add_edge("compare_contracts", "analyze_documentation")
    graph.add_edge("analyze_documentation", "generate_report")
    graph.add_edge("generate_report", END)

    try:
        app = graph.compile()
    except Exception:
        if verbose:
            print("[LangGraph] Sequential workflow (LangGraph compile failed)")
        return _run_sequential(initial)

    if verbose:
        print("[LangGraph] StateGraph active")

    seed: LGState = {  # type: ignore[assignment]
        **initial,
        "execution_trace": [],
        "mcp_trace": [],
        "agent_trace": [],
        "agent_events": [],
        "errors": [],
    }

    try:
        result = app.invoke(seed)
    except Exception:
        if verbose:
            print("[LangGraph] Sequential workflow (LangGraph invoke failed; linear fallback)")
        return _run_sequential(initial)

    if isinstance(result, dict):
        return dict(result)
    return result
