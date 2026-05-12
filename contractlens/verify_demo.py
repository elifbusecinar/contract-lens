"""Lightweight verification checks for the ContractLens demo (no test framework required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from contractlens.config import DEFAULT_REPORT_DIR, PACKAGE_ROOT, SAMPLE_FEATURE

from contractlens.mcp_server import audit_log
from contractlens.mcp_server import tools
from contractlens.mcp_server.capability_manifest import build_capability_manifest
from contractlens.mcp_server.export_docs import write_mcp_capabilities_md


def main(argv: list[str] | None = None) -> int:
    _ = argv
    errors: list[str] = []

    sample = PACKAGE_ROOT / "examples" / "sample_project"
    if not sample.is_dir():
        errors.append(f"sample project missing: {sample}")
        _print(errors)
        return 1

    root_s = str(sample.resolve())

    try:
        build_capability_manifest()
    except Exception as exc:
        errors.append(f"capability manifest failed: {exc}")

    try:
        doc_path = write_mcp_capabilities_md()
        if not doc_path.is_file():
            errors.append("MCP_CAPABILITIES.md not written")
    except Exception as exc:
        errors.append(f"export docs failed: {exc}")

    fe = tools.scan_frontend_contracts(root_s, verbose_log=False)
    fe_rows = fe.get("contracts") or []
    if len(fe_rows) < 1:
        errors.append(f"expected >= 1 frontend API call, got {len(fe_rows)}")

    be = tools.scan_backend_routes(root_s, verbose_log=False)
    be_rows = be.get("routes") or []
    if len(be_rows) < 1:
        errors.append(f"expected >= 1 backend route, got {len(be_rows)}")

    cmp_res = tools.compare_contracts(fe_rows, be_rows, verbose_log=False)
    mismatches = cmp_res.get("mismatches") or []
    if len(mismatches) < 3:
        errors.append(f"expected >= 3 mismatches on sample project, got {len(mismatches)}")

    fe_auth = tools.scan_frontend_auth(root_s, verbose_log=False)
    fe_auth_rows = fe_auth.get("findings") or []
    if isinstance(fe_auth, dict) and fe_auth.get("error"):
        errors.append(f"scan_frontend_auth error: {fe_auth.get('error')}")
    elif len(fe_auth_rows) < 1:
        errors.append(f"expected >= 1 frontend auth finding, got {len(fe_auth_rows)}")

    be_auth = tools.scan_backend_auth(root_s, verbose_log=False)
    be_auth_rows = be_auth.get("findings") or []
    if isinstance(be_auth, dict) and be_auth.get("error"):
        errors.append(f"scan_backend_auth error: {be_auth.get('error')}")
    elif len(be_auth_rows) < 1:
        errors.append(f"expected >= 1 backend auth finding, got {len(be_auth_rows)}")

    auth_cmp = tools.compare_auth_contracts(
        fe_rows,
        be_rows,
        fe_auth_rows,
        be_auth_rows,
        verbose_log=False,
    )
    auth_mm = auth_cmp.get("mismatches") or []
    if isinstance(auth_cmp, dict) and auth_cmp.get("error"):
        errors.append(f"compare_auth_contracts error: {auth_cmp.get('error')}")
    elif len(auth_mm) < 2:
        errors.append(f"expected >= 2 auth contract mismatches on sample project, got {len(auth_mm)}")

    fo = tools.find_openapi_specs(root_s, verbose_log=False)
    if len(fo.get("spec_paths") or []) < 1:
        errors.append(f"expected >= 1 OpenAPI/Swagger spec under sample project, got {fo!r}")

    parsed = tools.parse_openapi_contracts(root_s, verbose_log=False)
    oa_ops = parsed.get("contracts") or []
    if len(oa_ops) < 1:
        errors.append(f"expected >= 1 parsed OpenAPI operation, got {len(oa_ops)}")

    drift_tool = tools.compare_backend_to_openapi(root_s, verbose_log=False)
    drift_mm = drift_tool.get("mismatches") or []
    if len(drift_mm) < 1:
        errors.append(f"expected >= 1 OpenAPI vs backend drift mismatch, got {len(drift_mm)}")

    doc_scan = tools.scan_documentation_contracts(root_s, verbose_log=False)
    doc_claims = doc_scan.get("claims") or []
    if isinstance(doc_scan, dict) and doc_scan.get("error"):
        errors.append(f"scan_documentation_contracts error: {doc_scan.get('error')}")
    elif len(doc_claims) < 6:
        errors.append(f"expected >= 6 documentation claims on sample project, got {len(doc_claims)}")

    doc_cmp = tools.compare_documentation_drift(
        root_s,
        fe_rows,
        be_rows,
        oa_ops,
        doc_claims,
        verbose_log=False,
    )
    doc_mm = doc_cmp.get("mismatches") or []
    if isinstance(doc_cmp, dict) and doc_cmp.get("error"):
        errors.append(f"compare_documentation_drift error: {doc_cmp.get('error')}")
    elif len(doc_mm) < 2:
        errors.append(f"expected >= 2 documentation drift rows on sample project, got {len(doc_mm)}")

    gen = tools.generate_contract_report(
        SAMPLE_FEATURE,
        root_s,
        verbose_log=False,
        allow_write=True,
        report_dir=str(DEFAULT_REPORT_DIR.resolve()),
    )
    rp = gen.get("report_path") or ""
    gen_errs = gen.get("errors") or []
    if gen_errs:
        errors.append(f"generate_contract_report errors: {gen_errs}")
    if not rp:
        errors.append("generate_contract_report returned empty report_path")
    elif not Path(rp).is_file():
        errors.append(f"report file missing: {rp}")
    else:
        try:
            body = Path(rp).read_text(encoding="utf-8", errors="replace")
            if "## Auth / Role Contract Analysis" not in body:
                errors.append("report missing ## Auth / Role Contract Analysis section")
            if "## Documentation Drift Analysis" not in body:
                errors.append("report missing ## Documentation Drift Analysis section")
        except OSError as exc:
            errors.append(f"report unreadable: {exc}")

    log_path = audit_log.tool_audit_log_path()
    if not log_path.is_file():
        errors.append(f"tool audit log missing: {log_path}")
    else:
        try:
            entries = json.loads(log_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list) or len(entries) < 1:
                errors.append("audit log should contain at least one entry")
            elif not any(isinstance(e, dict) and e.get("tool") for e in entries):
                errors.append("audit log entries missing tool field")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"audit log unreadable: {exc}")

    rs = PACKAGE_ROOT / "contractlens-runs" / "latest" / "run_summary.json"
    if not rs.is_file():
        errors.append(f"run_summary.json missing after workflow: {rs}")

    _print(errors)
    return 1 if errors else 0


def _print(errors: list[str]) -> None:
    if errors:
        print("[verify_demo] FAILED")
        for e in errors:
            print(f"  - {e}")
    else:
        print("[verify_demo] OK: scanners, workflow artifacts, manifest, and MCP docs look healthy.")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
