"""Demonstrate MCP-style repository tools (prints visible labels)."""

from __future__ import annotations

import json

from contractlens.config import DEFAULT_REPORT_DIR, PACKAGE_ROOT, SAMPLE_FEATURE
from contractlens.mcp_server import audit_log
from contractlens.mcp_server import tools


def main() -> None:
    root_s = str((PACKAGE_ROOT / "examples" / "sample_project").resolve())
    print("[tools_demo] ContractLens MCP-first tools demo")
    print()

    tools.list_project_files(root_s, verbose_log=True)
    listing = tools.list_project_files(root_s, verbose_log=False)
    print("[tools_demo] list_project_files:", len(listing.get("files") or []), "files")
    print()

    tools.find_openapi_specs(root_s, verbose_log=True)
    spec_hit = tools.find_openapi_specs(root_s, verbose_log=False)
    print("[tools_demo] find_openapi_specs:", len(spec_hit.get("spec_paths") or []), "spec(s)")
    repo_root = str(PACKAGE_ROOT.resolve())
    tools.get_changed_files(repo_root, verbose_log=True)
    gf = tools.get_changed_files(repo_root, verbose_log=False)
    print("[tools_demo] get_changed_files:", len(gf.get("files") or []), "path(s) git=", gf.get("git_repository"))
    tools.parse_openapi_contracts(root_s, verbose_log=True)
    parsed = tools.parse_openapi_contracts(root_s, verbose_log=False)
    print("[tools_demo] parse_openapi_contracts:", len(parsed.get("contracts") or []), "operation(s)")
    tools.compare_backend_to_openapi(root_s, verbose_log=True)
    drift_demo = tools.compare_backend_to_openapi(root_s, verbose_log=False)
    print("[tools_demo] compare_backend_to_openapi:", len(drift_demo.get("mismatches") or []), "drift mismatch(es)")
    print()

    fe = tools.scan_frontend_contracts(root_s, verbose_log=True)
    fe_rows = fe.get("contracts") or []
    print("[tools_demo] frontend contracts:", len(fe_rows))
    print()

    be = tools.scan_backend_routes(root_s, verbose_log=True)
    be_rows = be.get("routes") or []
    print("[tools_demo] backend routes:", len(be_rows))
    print()

    tools.scan_frontend_auth(root_s, verbose_log=True)
    fe_auth_demo = tools.scan_frontend_auth(root_s, verbose_log=False)
    print("[tools_demo] scan_frontend_auth:", len(fe_auth_demo.get("findings") or []), "finding(s)")
    tools.scan_backend_auth(root_s, verbose_log=True)
    be_auth_demo = tools.scan_backend_auth(root_s, verbose_log=False)
    print("[tools_demo] scan_backend_auth:", len(be_auth_demo.get("findings") or []), "finding(s)")
    tools.compare_auth_contracts(
        fe_rows,
        be_rows,
        fe_auth_demo.get("findings") or [],
        be_auth_demo.get("findings") or [],
        verbose_log=True,
    )
    auth_demo = tools.compare_auth_contracts(
        fe_rows,
        be_rows,
        fe_auth_demo.get("findings") or [],
        be_auth_demo.get("findings") or [],
        verbose_log=False,
    )
    print("[tools_demo] compare_auth_contracts:", len(auth_demo.get("mismatches") or []), "mismatch(es)")
    print()

    tools.scan_documentation_contracts(root_s, verbose_log=True)
    doc_claims_demo = tools.scan_documentation_contracts(root_s, verbose_log=False).get("claims") or []
    print("[tools_demo] scan_documentation_contracts:", len(doc_claims_demo), "claim(s)")
    tools.compare_documentation_drift(
        root_s,
        fe_rows,
        be_rows,
        parsed.get("contracts") or [],
        doc_claims_demo,
        verbose_log=True,
    )
    doc_drift_demo = tools.compare_documentation_drift(
        root_s,
        fe_rows,
        be_rows,
        parsed.get("contracts") or [],
        doc_claims_demo,
        verbose_log=False,
    )
    print("[tools_demo] compare_documentation_drift:", len(doc_drift_demo.get("mismatches") or []), "row(s)")
    print()

    cmp_res = tools.compare_contracts(fe_rows, be_rows, verbose_log=True)
    print("[tools_demo] compare_contracts:", len(cmp_res.get("mismatches") or []), "mismatch(es)")
    mm_ci = cmp_res.get("mismatches") or []
    tools.evaluate_ci_gate(mm_ci, fail_on="High", verbose_log=True)
    gate_r = tools.evaluate_ci_gate(mm_ci, fail_on="High", verbose_log=False)
    print("[tools_demo] evaluate_ci_gate (sample mismatches):", gate_r.get("passed"), "exit=", gate_r.get("exit_code"))
    gate_pass = tools.evaluate_ci_gate([], fail_on="High", verbose_log=False)
    print("[tools_demo] evaluate_ci_gate (empty):", gate_pass.get("passed"), "exit=", gate_pass.get("exit_code"))
    print()

    gen = tools.generate_contract_report(
        SAMPLE_FEATURE,
        root_s,
        verbose_log=True,
        allow_write=True,
        report_dir=str(DEFAULT_REPORT_DIR),
    )
    print("[tools_demo] generate_contract_report:", gen.get("report_path"), "mismatch_count=", gen.get("mismatch_count"))
    errs = gen.get("errors") or []
    if errs:
        print("[tools_demo] workflow errors:", errs)
    print()

    latest = tools.get_latest_report(str(DEFAULT_REPORT_DIR), verbose_log=True)
    print("[tools_demo] get_latest_report:", latest.get("path"), f"({len(latest.get('content') or '')} chars)")
    print()

    tools.list_mcp_resources(verbose_log=True)
    lr = tools.list_mcp_resources(verbose_log=False)
    print("[tools_demo] list_mcp_resources:", lr.get("count"), "URIs")
    print()

    tools.read_mcp_resource("contractlens://reports/latest", verbose_log=True)
    rep_res = tools.read_mcp_resource("contractlens://reports/latest", verbose_log=False)
    st = rep_res.get("status", "ok")
    clen = len(rep_res.get("content") or "") if isinstance(rep_res.get("content"), str) else 0
    print("[tools_demo] read_mcp_resource reports/latest:", st, f"content_chars={clen}")
    print()

    tools.list_mcp_prompts(verbose_log=True)
    print("[tools_demo] list_mcp_prompts:", tools.list_mcp_prompts(verbose_log=False).get("count"))
    print()

    mm_sample = json.dumps(
        {"area": "path", "frontend_expects": "/a", "backend_provides": "/b", "risk": "High", "suggestion": "Align paths."}
    )
    tools.get_mcp_prompt("explain_contract_mismatch", {"mismatch": mm_sample}, verbose_log=True)
    gp = tools.get_mcp_prompt("explain_contract_mismatch", {"mismatch": mm_sample}, verbose_log=False)
    snippet = (gp.get("prompt") or "").splitlines()[0][:120]
    print("[tools_demo] get_mcp_prompt explain_contract_mismatch (first line):", snippet)
    print()

    print(f"[MCP] Tool audit log written: {audit_log.tool_audit_log_path()}")
    print("[tools_demo] Done.")


if __name__ == "__main__":
    main()
