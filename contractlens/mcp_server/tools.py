"""MCP-style tools: repository intelligence with audit logs and permission boundaries."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from contractlens.config import DEFAULT_REPORT_DIR, PACKAGE_ROOT, default_report_path
from contractlens.contracts.comparator import (
    compare_contracts as compare_contracts_fn,
    summarize_risk_from_mismatches,
)
from contractlens.ci.gate import evaluate_ci_gate as ci_evaluate_gate
from contractlens.contracts.models import ApiContract, ContractMismatch
from contractlens.git.diff import get_changed_files_relative_to_root
from contractlens.openapi import collect_openapi_contracts
from contractlens.openapi import compare_backend_to_openapi as openapi_drift_compare
from contractlens.openapi.loader import find_openapi_specs_under_root, yaml_supported
from contractlens.mcp_server import audit_log
from contractlens.mcp_server import prompts as mcp_prompts
from contractlens.mcp_server import resources as mcp_resources
from contractlens.mcp_server.permissions import (
    assert_write_allowed,
    path_under_root_has_ignored_dir,
    resolve_repo_root,
    resolve_under_root,
    resolve_write_within_workspace,
)
from contractlens.scanner.backend_scanner import scan_backend
from contractlens.scanner.file_scanner import scan_repository_files
from contractlens.scanner.frontend_scanner import scan_frontend
from contractlens.auth.auth_comparator import compare_auth_contracts_from_dicts
from contractlens.auth.backend_auth_scanner import scan_backend_auth as scan_backend_auth_paths
from contractlens.auth.frontend_auth_scanner import scan_frontend_auth as scan_frontend_auth_paths
from contractlens.docs_analyzer.doc_comparator import compare_documentation_drift_from_dicts
from contractlens.docs_analyzer.doc_scanner import scan_documentation as scan_documentation_paths
from contractlens.runs.run_store import STANDARD_ARTIFACTS

CODE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".cs", ".py", ".json", ".md"}


def _verbose(verbose_log: bool, tool: str) -> None:
    if verbose_log:
        print(f"[MCP] {tool} called")


def _is_dict_error(out: dict[str, Any]) -> tuple[bool, str | None]:
    if out.get("status") == "error":
        return True, str(out.get("error", "error"))
    if out.get("error"):
        return True, str(out["error"])
    if out.get("success") is False:
        return True, str(out.get("error", "failed"))
    return False, None


def _summarize_tool_output(tool: str, out: dict[str, Any]) -> str | None:
    """Short audit line; never embed large payloads."""
    if out.get("status") == "error" or out.get("error"):
        msg = str(out.get("error", out.get("status", "error")))[:200]
        return f"error: {msg}"
    try:
        if tool == "list_project_files":
            return f"{len(out.get('files') or [])} file path(s)"
        if tool == "read_project_file":
            c = out.get("content")
            if isinstance(c, str):
                return f"Returned {len(c)} character(s)"
            return "Returned empty content"
        if tool == "search_in_files":
            return f"{len(out.get('matches') or [])} match(es)"
        if tool == "write_report":
            if out.get("success"):
                return f"Wrote OK -> {Path(str(out.get('path', ''))).name or 'report'}"
            return "write failed"
        if tool == "scan_frontend_contracts":
            return f"{len(out.get('contracts') or [])} contract(s)"
        if tool == "scan_backend_routes":
            return f"{len(out.get('routes') or [])} route(s)"
        if tool == "compare_contracts":
            mm = out.get("mismatches") or []
            rs = out.get("risk_summary") or {}
            if isinstance(rs, dict):
                return f"{len(mm)} mismatch(es); High={rs.get('high', 0)}"
            return f"{len(mm)} mismatch(es)"
        if tool == "generate_contract_report":
            n = out.get("mismatch_count")
            rp = out.get("report_path") or ""
            return f"mismatch_count={n}; report={Path(str(rp)).name or rp}"
        if tool == "generate_html_report":
            n = out.get("mismatch_count")
            rp = out.get("report_path") or ""
            hp = out.get("html_report_path") or ""
            return f"mismatch_count={n}; md={Path(str(rp)).name or rp}; html={Path(str(hp)).name or hp}"
        if tool == "get_latest_report":
            c = out.get("content")
            ln = len(c) if isinstance(c, str) else 0
            return f"Latest report body {ln} character(s)"
        if tool == "get_run_trace":
            tr = out.get("trace") or []
            return f"{len(tr)} trace line(s)"
        if tool == "list_runs":
            return f"{len(out.get('runs') or [])} stamped run(s)"
        if tool == "get_run_summary":
            if isinstance(out.get("summary"), dict):
                summ = out.get("summary") or {}
                return f"run_id={out.get('run_id')}; duration_ms={summ.get('duration_ms')}"
            return str(out.get("error", "empty"))[:100]
        if tool == "get_run_artifact":
            fmt = out.get("format", "")
            if fmt == "markdown":
                c = out.get("content")
                ln = len(c) if isinstance(c, str) else 0
                return f"markdown chars={ln}"
            data = out.get("data")
            if isinstance(data, dict):
                return f"json keys={len(data)}"
            if isinstance(data, list):
                return f"json rows={len(data)}"
            return f"format={fmt or '?'}"
        if tool == "explain_mismatch":
            if "explanation" in out:
                return "Returned explanation + suggested_fix"
            return "Unexpected shape"
        if tool == "list_mcp_resources":
            return f"{out.get('count', 0)} resource URI(s)"
        if tool == "read_mcp_resource":
            st = out.get("status", "ok")
            body = out.get("content")
            if isinstance(body, str):
                return f"status={st}; body {len(body)} character(s)"
            return f"status={st}"
        if tool == "list_mcp_prompts":
            return f"{out.get('count', 0)} prompt template(s)"
        if tool == "get_mcp_prompt":
            p = out.get("prompt")
            if isinstance(p, str):
                return f"Prompt string {len(p)} character(s)"
            return "prompt rendered"
        if tool == "find_openapi_specs":
            return f"{len(out.get('spec_paths') or [])} spec path(s); yaml_supported={out.get('yaml_supported')}"
        if tool == "get_changed_files":
            return f"{len(out.get('files') or [])} path(s); git={out.get('git_repository')}"
        if tool == "parse_openapi_contracts":
            return f"{len(out.get('contracts') or [])} operation(s); specs={len(out.get('spec_paths') or [])}"
        if tool == "compare_backend_to_openapi":
            mm = out.get("mismatches") or []
            rs = out.get("risk_summary") or {}
            if isinstance(rs, dict):
                return f"{len(mm)} openapi drift mismatch(es); High={rs.get('high', 0)}"
            return f"{len(mm)} openapi drift mismatch(es)"
        if tool == "evaluate_ci_gate":
            passed = out.get("passed")
            ec = out.get("exit_code")
            return f"passed={passed}; exit_code={ec}"
        if tool == "scan_frontend_auth":
            return f"{len(out.get('findings') or [])} auth finding(s)"
        if tool == "scan_backend_auth":
            return f"{len(out.get('findings') or [])} auth finding(s)"
        if tool == "compare_auth_contracts":
            return f"{out.get('count', len(out.get('mismatches') or []))} auth mismatch(es)"
        if tool == "scan_documentation_contracts":
            return f"{len(out.get('claims') or [])} doc claim(s)"
        if tool == "compare_documentation_drift":
            return f"{out.get('count', len(out.get('mismatches') or []))} documentation drift row(s)"
        if tool == "list_runs":
            return f"{len(out.get('runs') or [])} stamped run(s)"
        if tool == "get_run_summary":
            return "summary payload" if isinstance(out.get("summary"), dict) else str(out.get("error", "empty"))[:80]
        if tool == "get_run_artifact":
            fmt = out.get("format", "")
            return f"artifact format={fmt}"
    except Exception:
        return "summary unavailable"
    return None


def _audit_wrap(tool: str, input_summary: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        out = fn()
        dur_ms = (time.perf_counter() - t0) * 1000
        bad, err = _is_dict_error(out) if isinstance(out, dict) else (False, None)
        summ = _summarize_tool_output(tool, out) if isinstance(out, dict) else None
        audit_log.log_tool_call(
            tool=tool,
            input_summary=input_summary,
            status="error" if bad else "success",
            duration_ms=dur_ms,
            error=err,
            output_summary=summ,
        )
        return out
    except Exception as exc:
        dur_ms = (time.perf_counter() - t0) * 1000
        audit_log.log_tool_call(
            tool=tool,
            input_summary=input_summary,
            status="error",
            duration_ms=dur_ms,
            error=str(exc),
            output_summary=f"exception: {exc!s}"[:200],
        )
        return {"status": "error", "error": str(exc)}


def _filtered_relative_paths(base: Path) -> list[str]:
    files: list[str] = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(base)
        except ValueError:
            continue
        if path_under_root_has_ignored_dir(rel):
            continue
        files.append(rel.as_posix())
    files.sort()
    return files


def list_project_files(
    root: str = ".",
    *,
    verbose_log: bool = False,
    repo_root: str | None = None,
) -> dict[str, Any]:
    rr = repo_root if repo_root is not None else root

    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "list_project_files")
        base, err = resolve_repo_root(rr)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        return {"files": files}

    return _audit_wrap("list_project_files", f"root={rr!r}", inner)


def read_project_file(
    path: str,
    *,
    repo_root: str,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "read_project_file")
        root, rerr = resolve_repo_root(repo_root)
        if rerr:
            return rerr
        assert root is not None
        resolved, perr = resolve_under_root(root, path)
        if perr:
            return perr
        assert resolved is not None
        if not resolved.is_file():
            return {"content": "", "error": f"not a file: {resolved}"}
        try:
            text = resolved.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return {"content": "", "error": str(e)}
        return {"content": text}

    tail = Path(path).as_posix()
    if len(tail) > 120:
        tail = "…/" + tail.rsplit("/", 1)[-1]
    return _audit_wrap("read_project_file", f"path={tail!r} repo_root={repo_root!r}", inner)


def search_in_files(
    root: str,
    query: str,
    *,
    verbose_log: bool = False,
    repo_root: str | None = None,
) -> dict[str, Any]:
    rr = repo_root if repo_root is not None else root

    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "search_in_files")
        base, err = resolve_repo_root(rr)
        if err:
            return err
        assert base is not None
        matches: list[dict[str, Any]] = []
        q = query.lower()
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            try:
                rel = p.relative_to(base)
            except ValueError:
                continue
            if path_under_root_has_ignored_dir(rel):
                continue
            if p.suffix.lower() not in CODE_EXTENSIONS and p.suffix:
                continue
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            rel_s = rel.as_posix()
            for i, line in enumerate(lines, start=1):
                if q in line.lower():
                    matches.append({"path": rel_s, "line": i, "snippet": line.strip()[:200]})
        return {"matches": matches}

    return _audit_wrap("search_in_files", f"root={rr!r} query={query[:80]!r}", inner)


def write_report(
    path: str,
    content: str,
    *,
    verbose_log: bool = False,
    allow_write: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "write_report")
        werr = assert_write_allowed(allow_write)
        if werr:
            return werr
        resolved, perr = resolve_write_within_workspace(path)
        if perr:
            return perr
        assert resolved is not None
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
        except OSError as e:
            return {"success": False, "path": str(resolved), "error": str(e)}
        return {"success": True, "path": str(resolved)}

    return _audit_wrap("write_report", f"path={path!r} bytes={len(content)}", inner)


def scan_frontend_contracts(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "scan_frontend_contracts")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        contracts = [c.model_dump() for c in scan_frontend(str(base), files)]
        return {"contracts": contracts}

    return _audit_wrap("scan_frontend_contracts", f"root={root!r}", inner)


def scan_backend_routes(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "scan_backend_routes")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        routes = [c.model_dump() for c in scan_backend(str(base), files)]
        return {"routes": routes}

    return _audit_wrap("scan_backend_routes", f"root={root!r}", inner)


def scan_frontend_auth(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "scan_frontend_auth")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        rows = scan_frontend_auth_paths(str(base), files)
        return {"findings": [r.model_dump() for r in rows]}

    return _audit_wrap("scan_frontend_auth", f"root={root!r}", inner)


def scan_backend_auth(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "scan_backend_auth")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        rows = scan_backend_auth_paths(str(base), files)
        return {"findings": [r.model_dump() for r in rows]}

    return _audit_wrap("scan_backend_auth", f"root={root!r}", inner)


def compare_auth_contracts(
    frontend_contracts: list[dict[str, Any]],
    backend_contracts: list[dict[str, Any]],
    frontend_auth_findings: list[dict[str, Any]],
    backend_auth_findings: list[dict[str, Any]],
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "compare_auth_contracts")
        mm = compare_auth_contracts_from_dicts(
            frontend_contracts,
            backend_contracts,
            frontend_auth_findings,
            backend_auth_findings,
        )
        return {"mismatches": [m.model_dump() for m in mm], "count": len(mm)}

    nfe = len(frontend_contracts) if isinstance(frontend_contracts, list) else 0
    nbe = len(backend_contracts) if isinstance(backend_contracts, list) else 0
    nfa = len(frontend_auth_findings) if isinstance(frontend_auth_findings, list) else 0
    nba = len(backend_auth_findings) if isinstance(backend_auth_findings, list) else 0
    return _audit_wrap(
        "compare_auth_contracts",
        f"fe_contracts={nfe} be_contracts={nbe} fe_auth={nfa} be_auth={nba}",
        inner,
    )


def scan_documentation_contracts(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "scan_documentation_contracts")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        rows = scan_documentation_paths(str(base), files)
        return {"claims": [r.model_dump() for r in rows]}

    return _audit_wrap("scan_documentation_contracts", f"root={root!r}", inner)


def compare_documentation_drift(
    root: str,
    frontend_contracts: list[dict[str, Any]],
    backend_contracts: list[dict[str, Any]],
    openapi_contracts: list[dict[str, Any]],
    documentation_claims: list[dict[str, Any]],
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "compare_documentation_drift")
        mm = compare_documentation_drift_from_dicts(
            frontend_contracts,
            backend_contracts,
            openapi_contracts,
            documentation_claims,
            repo_root=root,
        )
        return {"mismatches": [m.model_dump() for m in mm], "count": len(mm)}

    nc = len(documentation_claims) if isinstance(documentation_claims, list) else 0
    nfe = len(frontend_contracts) if isinstance(frontend_contracts, list) else 0
    nbe = len(backend_contracts) if isinstance(backend_contracts, list) else 0
    noa = len(openapi_contracts) if isinstance(openapi_contracts, list) else 0
    return _audit_wrap(
        "compare_documentation_drift",
        f"root={root!r} claims={nc} fe={nfe} be={nbe} oa={noa}",
        inner,
    )


def compare_contracts(
    frontend_contracts: list[dict[str, Any]],
    backend_contracts: list[dict[str, Any]],
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "compare_contracts")
        fe = [ApiContract.model_validate(x) for x in frontend_contracts]
        be = [ApiContract.model_validate(x) for x in backend_contracts]
        mismatches, summary = compare_contracts_fn(fe, be)
        return {
            "mismatches": [m.model_dump() for m in mismatches],
            "risk_summary": summary.model_dump(),
        }

    summary_in = f"fe={len(frontend_contracts)} be={len(backend_contracts)}"
    return _audit_wrap("compare_contracts", summary_in, inner)


def generate_contract_report(
    feature_name: str,
    root: str,
    *,
    verbose_log: bool = False,
    allow_write: bool = True,
    report_dir: str | None = None,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "generate_contract_report")
        werr = assert_write_allowed(allow_write)
        if werr:
            return werr
        base_root = Path(root).resolve()
        if not base_root.is_dir():
            return {"status": "error", "error": f"root not a directory: {base_root}"}

        from contractlens.workflow.graph import run_workflow
        from contractlens.workflow.state import new_state

        rd = Path(report_dir).resolve() if report_dir else DEFAULT_REPORT_DIR.resolve()
        rd.mkdir(parents=True, exist_ok=True)

        initial = new_state(feature_name, str(base_root), verbose=False, mode="default")
        initial["report_output_dir"] = str(rd)
        initial["report_path"] = str(default_report_path(feature_name, rd))
        initial["use_llm_agents"] = False
        initial["mcp_allow_write"] = allow_write

        out = run_workflow(initial)
        rp = out.get("report_path") or initial["report_path"]
        mismatches = out.get("mismatches") or []
        return {
            "report_path": rp,
            "mismatch_count": len(mismatches),
            "errors": out.get("errors") or [],
        }

    return _audit_wrap(
        "generate_contract_report",
        f"feature={feature_name!r} root={root!r}",
        inner,
    )


def generate_html_report(
    feature_name: str,
    root: str,
    *,
    verbose_log: bool = False,
    allow_write: bool = True,
    report_dir: str | None = None,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "generate_html_report")
        werr = assert_write_allowed(allow_write)
        if werr:
            return werr
        base_root = Path(root).resolve()
        if not base_root.is_dir():
            return {"status": "error", "error": f"root not a directory: {base_root}"}

        from contractlens.workflow.graph import run_workflow
        from contractlens.workflow.state import new_state

        rd = Path(report_dir).resolve() if report_dir else DEFAULT_REPORT_DIR.resolve()
        rd.mkdir(parents=True, exist_ok=True)

        initial = new_state(feature_name, str(base_root), verbose=False, mode="default")
        initial["report_output_dir"] = str(rd)
        initial["report_path"] = str(default_report_path(feature_name, rd))
        initial["generate_html"] = True
        initial["use_llm_agents"] = False
        initial["mcp_allow_write"] = allow_write

        out = run_workflow(initial)
        rp = out.get("report_path") or initial["report_path"]
        hp = (out.get("html_report_path") or "").strip()
        mismatches = out.get("mismatches") or []
        return {
            "report_path": rp,
            "html_report_path": hp,
            "mismatch_count": len(mismatches),
            "errors": out.get("errors") or [],
        }

    return _audit_wrap(
        "generate_html_report",
        f"feature={feature_name!r} root={root!r}",
        inner,
    )


def get_latest_report(
    reports_dir: str | None = None,
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "get_latest_report")
        rd = Path(reports_dir).resolve() if reports_dir else DEFAULT_REPORT_DIR.resolve()
        if not rd.is_dir():
            return {"status": "error", "error": f"reports dir not found: {rd}"}
        mds = sorted(rd.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not mds:
            return {"path": "", "content": "", "message": "No Markdown reports found."}
        latest = mds[0]
        try:
            body = latest.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return {"status": "error", "error": str(e)}
        return {"path": str(latest.resolve()), "content": body}

    return _audit_wrap("get_latest_report", f"reports_dir={reports_dir!r}", inner)


def get_run_trace(run_id: str = "latest", *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "get_run_trace")
        from contractlens.mcp_server import run_store

        rd = run_store.resolve_run_directory(run_id)
        if rd is None:
            return {"status": "error", "error": f"unknown or missing run directory for run_id={run_id!r}"}
        p = rd / "execution_trace.json"
        if not p.is_file():
            return {"trace": [], "run_id": run_id, "message": "No execution trace saved yet."}
        try:
            trace = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(trace, list):
                trace = []
        except (json.JSONDecodeError, OSError):
            trace = []
        return {"trace": trace, "run_id": run_id}

    return _audit_wrap("get_run_trace", f"run_id={run_id!r}", inner)


def list_runs(limit: int | str = 50, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "list_runs")
        from contractlens.mcp_server import run_store

        try:
            lim_raw = int(str(limit).strip())
        except (TypeError, ValueError):
            lim_raw = 50
        lim = max(1, min(lim_raw, 500))
        stamped = run_store.list_stamp_directories(limit=lim)
        rows: list[dict[str, Any]] = []
        for p in stamped:
            meta: dict[str, Any] = {}
            sp = p / "run_summary.json"
            if sp.is_file():
                try:
                    raw = json.loads(sp.read_text(encoding="utf-8"))
                    if isinstance(raw, dict):
                        meta = raw
                except (json.JSONDecodeError, OSError):
                    meta = {}
            rows.append(
                {
                    "run_id": p.name,
                    "feature_name": meta.get("feature_name"),
                    "completed_at": meta.get("completed_at"),
                    "duration_ms": meta.get("duration_ms"),
                    "mismatch_count": meta.get("mismatch_count"),
                }
            )
        latest_meta: dict[str, Any] = {}
        lp = run_store.latest_dir() / "run_summary.json"
        if lp.is_file():
            try:
                raw = json.loads(lp.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    latest_meta = raw
            except (json.JSONDecodeError, OSError):
                latest_meta = {}
        return {
            "runs": rows,
            "latest_run_id": latest_meta.get("run_id"),
            "latest_summary": latest_meta,
            "standard_artifacts": sorted(STANDARD_ARTIFACTS),
        }

    return _audit_wrap("list_runs", f"limit={limit}", inner)


def get_run_summary(run_id: str = "latest", *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "get_run_summary")
        from contractlens.mcp_server import run_store

        rd = run_store.resolve_run_directory(run_id)
        if rd is None:
            return {"status": "error", "error": f"unknown or missing run directory for run_id={run_id!r}"}
        data, err = run_store.read_artifact_json(rd, "run_summary.json")
        if err or data is None:
            return {"status": "error", "error": err or "could not read run_summary.json"}
        rid_out = data.get("run_id") if isinstance(data, dict) else run_id
        return {"run_id": rid_out, "summary": data}

    tail = str(run_id or "latest")[:40]
    return _audit_wrap("get_run_summary", f"run_id={tail!r}", inner)


def get_run_artifact(
    run_id: str,
    artifact: str,
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "get_run_artifact")
        from contractlens.mcp_server import run_store

        art = str(artifact or "").strip()
        if art not in STANDARD_ARTIFACTS:
            return {
                "status": "error",
                "error": f"artifact must be one of {sorted(STANDARD_ARTIFACTS)}",
            }
        rd = run_store.resolve_run_directory(run_id)
        if rd is None:
            return {"status": "error", "error": f"unknown or missing run directory for run_id={run_id!r}"}
        if art == "report.md":
            body, err = run_store.read_artifact_text(rd, art)
            if err:
                return {"status": "error", "error": err}
            return {
                "run_id": run_id,
                "artifact": art,
                "format": "markdown",
                "content": body or "",
            }
        data, err = run_store.read_artifact_json(rd, art)
        if err:
            return {"status": "error", "error": err}
        return {"run_id": run_id, "artifact": art, "format": "json", "data": data}

    return _audit_wrap(
        "get_run_artifact",
        f"run_id={str(run_id)[:40]!r} artifact={str(artifact)[:40]!r}",
        inner,
    )


def explain_mismatch(mismatch: dict[str, Any], *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "explain_mismatch")
        try:
            m = ContractMismatch.model_validate(mismatch)
        except Exception as exc:
            return {"status": "error", "error": f"invalid mismatch payload: {exc}"}

        explanation = (
            f"Area '{m.area}' ({m.risk} risk): frontend side expects `{m.frontend_expects}` "
            f"but backend provides `{m.backend_provides}`."
        )
        suggested = m.suggestion
        return {"explanation": explanation, "suggested_fix": suggested}

    area = str(mismatch.get("area", ""))
    return _audit_wrap("explain_mismatch", f"area={area!r}", inner)


def _normalize_prompt_tool_arguments(arguments: dict[str, Any] | None) -> dict[str, Any]:
    if not arguments:
        return {}
    if all(isinstance(v, str) for v in arguments.values()):
        str_args = {str(k): str(v) for k, v in arguments.items()}
        return mcp_prompts.coerce_prompt_arguments_from_strings(str_args)
    return dict(arguments)


def list_mcp_resources(*, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "list_mcp_resources")
        rows = [
            {"uri": u, "description": mcp_resources.RESOURCE_DESCRIPTIONS.get(u, "")}
            for u in mcp_resources.RESOURCE_REGISTRY
        ]
        return {"resources": rows, "count": len(rows)}

    return _audit_wrap("list_mcp_resources", "", inner)


def read_mcp_resource(uri: str, *, root: str | None = None, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "read_mcp_resource")
        payload = mcp_resources.read_resource_by_uri(uri, root=root)
        return {"requested_uri": uri, **payload}

    return _audit_wrap("read_mcp_resource", f"uri={uri[:120]!r}", inner)


def list_mcp_prompts(*, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "list_mcp_prompts")
        prompts = [{"name": n, "description": f"Template: {n} (deterministic string; no LLM)."} for n in mcp_prompts.PROMPT_NAMES]
        return {"prompts": prompts, "count": len(prompts)}

    return _audit_wrap("list_mcp_prompts", "", inner)


def find_openapi_specs(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "find_openapi_specs")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        paths = find_openapi_specs_under_root(base)
        yaml_paths = [p for p in paths if Path(p).suffix.lower() in {".yaml", ".yml"}]
        ys = yaml_supported()
        return {
            "spec_paths": paths,
            "yaml_specs": yaml_paths,
            "yaml_supported": ys,
            "skipped_yaml": yaml_paths if not ys else [],
        }

    return _audit_wrap("find_openapi_specs", f"root={root!r}", inner)


def parse_openapi_contracts(root: str, *, verbose_log: bool = False) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "parse_openapi_contracts")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        contracts, rels, notes = collect_openapi_contracts(str(base))
        return {
            "contracts": [c.model_dump() for c in contracts],
            "spec_paths": rels,
            "notes": notes,
            "yaml_supported": yaml_supported(),
        }

    return _audit_wrap("parse_openapi_contracts", f"root={root!r}", inner)


def get_changed_files(
    root: str,
    *,
    include_cached: bool = True,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "get_changed_files")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        paths, notes, is_git = get_changed_files_relative_to_root(str(base), include_cached=include_cached)
        return {"files": paths, "git_repository": is_git, "notes": notes}

    return _audit_wrap(
        "get_changed_files",
        f"root={root!r} include_cached={include_cached}",
        inner,
    )


def compare_backend_to_openapi(
    root: str,
    *,
    backend_contracts: list[dict[str, Any]] | None = None,
    openapi_contracts: list[dict[str, Any]] | None = None,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "compare_backend_to_openapi")
        base, err = resolve_repo_root(root)
        if err:
            return err
        assert base is not None
        files = _filtered_relative_paths(base)
        be_rows = backend_contracts
        if not be_rows:
            be_rows = [c.model_dump() for c in scan_backend(str(base), files)]
        oa_rows = openapi_contracts
        notes: list[str] = []
        if not oa_rows:
            oac, _, parse_notes = collect_openapi_contracts(str(base))
            oa_rows = [c.model_dump() for c in oac]
            notes.extend(parse_notes)
        be_models = [ApiContract.model_validate(x) for x in be_rows]
        oa_models = [ApiContract.model_validate(x) for x in oa_rows]
        drift = openapi_drift_compare(be_models, oa_models)
        summary = summarize_risk_from_mismatches(drift)
        return {
            "mismatches": [m.model_dump() for m in drift],
            "risk_summary": summary.model_dump(),
            "backend_operations_used": len(be_rows),
            "openapi_operations_used": len(oa_rows),
            "notes": notes,
        }

    bc = len(backend_contracts) if backend_contracts else 0
    oc = len(openapi_contracts) if openapi_contracts else 0
    return _audit_wrap(
        "compare_backend_to_openapi",
        f"root={root!r} backend_rows={bc} openapi_rows={oc}",
        inner,
    )


def evaluate_ci_gate(
    mismatches: list[dict[str, Any]],
    fail_on: str = "High",
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "evaluate_ci_gate")
        rows = mismatches if isinstance(mismatches, list) else []
        clean = [x for x in rows if isinstance(x, dict)]
        return ci_evaluate_gate(clean, fail_on=fail_on)

    fo = str(fail_on or "High")[:12]
    return _audit_wrap("evaluate_ci_gate", f"fail_on={fo!r} n={len(mismatches) if isinstance(mismatches, list) else 0}", inner)


def get_mcp_prompt(
    name: str,
    arguments: dict[str, Any] | None = None,
    *,
    verbose_log: bool = False,
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        _verbose(verbose_log, "get_mcp_prompt")
        norm = _normalize_prompt_tool_arguments(arguments)
        try:
            text = mcp_prompts.render_named_prompt(name, norm)
            return {"name": name, "prompt": text}
        except ValueError as exc:
            return {"status": "error", "error": str(exc)}

    return _audit_wrap("get_mcp_prompt", f"name={name!r}", inner)


MCP_TOOL_NAMES: list[str] = [
    "list_project_files",
    "read_project_file",
    "search_in_files",
    "write_report",
    "find_openapi_specs",
    "get_changed_files",
    "parse_openapi_contracts",
    "compare_backend_to_openapi",
    "scan_frontend_contracts",
    "scan_backend_routes",
    "scan_frontend_auth",
    "scan_backend_auth",
    "compare_contracts",
    "compare_auth_contracts",
    "scan_documentation_contracts",
    "compare_documentation_drift",
    "generate_contract_report",
    "generate_html_report",
    "get_latest_report",
    "get_run_trace",
    "list_runs",
    "get_run_summary",
    "get_run_artifact",
    "explain_mismatch",
    "evaluate_ci_gate",
    "list_mcp_resources",
    "read_mcp_resource",
    "list_mcp_prompts",
    "get_mcp_prompt",
]


def tools_manifest() -> str:
    return json.dumps({"tools": [{"name": n} for n in MCP_TOOL_NAMES]}, indent=2)
