"""Optional OpenAPI/Swagger ingestion for backend contract accuracy + doc drift checks."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from contractlens.contracts.comparator import normalized_path_tokens, path_similarity, summarize_risk_from_mismatches
from contractlens.contracts.models import ApiContract, ContractMismatch
from contractlens.openapi.loader import find_openapi_specs_under_root, load_spec_dict, yaml_supported
from contractlens.openapi.parser import (
    backend_implementation_field_names,
    backend_request_field_names,
    openapi_documented_field_names,
    openapi_documented_request_fields,
    parse_spec_document,
)


def collect_openapi_contracts(
    root: str | Path,
    *,
    allowed_spec_relative_paths: frozenset[str] | None = None,
) -> tuple[list[ApiContract], list[str], list[str]]:
    """
    Load every discovered spec under ``root``.

    When ``allowed_spec_relative_paths`` is set, only specs whose relative path is in that set are parsed.

    Returns ``(contracts, relative_spec_paths, notes)``.
    """
    base = Path(root).resolve()
    rels = find_openapi_specs_under_root(base)
    if allowed_spec_relative_paths is not None:
        rels = [r for r in rels if r in allowed_spec_relative_paths]
    notes: list[str] = []
    if not yaml_supported():
        yaml_missing = [r for r in rels if Path(r).suffix.lower() in {".yaml", ".yml"}]
        if yaml_missing:
            notes.append(
                "YAML specs skipped (install PyYAML or convert specs to JSON): "
                + ", ".join(yaml_missing)
            )
        rels = [r for r in rels if Path(r).suffix.lower() == ".json"]

    contracts: list[ApiContract] = []
    for rel in rels:
        full = base / rel
        doc, err = load_spec_dict(full)
        if err:
            notes.append(f"{rel}: load error — {err}")
            continue
        assert doc is not None
        contracts.extend(parse_spec_document(doc, rel))
    return contracts, rels, notes


def _norm_field_key(name: str) -> str:
    return name.lower().replace("_", "").replace("-", "")


def _normalized_field_set(names: set[str]) -> set[str]:
    return {_norm_field_key(n) for n in names if n}


def _describe_field_drift(openapi_names: set[str], impl_names: set[str]) -> tuple[str, str]:
    sn = _normalized_field_set(openapi_names)
    bn = _normalized_field_set(impl_names)
    spec_only_norm = sn - bn
    impl_only_norm = bn - sn

    def pick_rep(norm_key: str, pool: set[str]) -> str:
        for p in sorted(pool):
            if _norm_field_key(p) == norm_key:
                return p
        return norm_key

    spec_extra = ", ".join(sorted(pick_rep(k, openapi_names) for k in sorted(spec_only_norm))) or "—"
    impl_extra = ", ".join(sorted(pick_rep(k, impl_names) for k in sorted(impl_only_norm))) or "—"

    return (
        "OpenAPI fields: " + (", ".join(sorted(openapi_names)) or "(none)"),
        "Implementation fields: " + (", ".join(sorted(impl_names)) or "(none)")
        + (f"; only-in-spec (normalized): {spec_extra}" if spec_only_norm else "")
        + (f"; only-in-code (normalized): {impl_extra}" if impl_only_norm else ""),
    )


def compare_backend_to_openapi(
    backend_contracts: Iterable[ApiContract],
    openapi_contracts: Iterable[ApiContract],
) -> list[ContractMismatch]:
    """
    Pair scanner-derived backend routes with OpenAPI operations (same method, best path similarity).

    Emits deterministic documentation/schema drift mismatches when paths or JSON field hints diverge.
    """
    be_list = list(backend_contracts)
    oa_list = list(openapi_contracts)
    mismatches: list[ContractMismatch] = []

    if not oa_list:
        return mismatches

    consumed_oa: set[int] = set()
    pairs: list[tuple[ApiContract, ApiContract]] = []

    for b in sorted(be_list, key=lambda x: (x.path, x.method)):
        best_idx: int | None = None
        best_sim = -1.0
        for j, o in enumerate(oa_list):
            if j in consumed_oa:
                continue
            if o.method.upper() != b.method.upper():
                continue
            sim = path_similarity(o.path, b.path)
            if sim > best_sim:
                best_sim = sim
                best_idx = j
        if best_idx is not None and best_sim >= 0.45:
            consumed_oa.add(best_idx)
            pairs.append((b, oa_list[best_idx]))

    paired_backend_ids = {id(be) for be, _ in pairs}

    for be, oa in pairs:
        if normalized_path_tokens(oa.path) != normalized_path_tokens(be.path):
            mismatches.append(
                ContractMismatch(
                    area="openapi_vs_code_path",
                    frontend_expects=f"OpenAPI {oa.method} `{oa.path}` (`{oa.source}`)",
                    backend_provides=f"Code {be.method} `{be.path}` (`{be.source}`)",
                    risk="High",
                    suggestion=(
                        "Update the published OpenAPI path or change the controller route so spec and implementation "
                        "agree (add an alias route if both must remain temporarily)."
                    ),
                )
            )

        o_resp = openapi_documented_field_names(oa)
        b_resp = backend_implementation_field_names(be)
        if o_resp or b_resp:
            if _normalized_field_set(o_resp) != _normalized_field_set(b_resp):
                o_txt, b_txt = _describe_field_drift(o_resp, b_resp)
                mismatches.append(
                    ContractMismatch(
                        area="openapi_vs_code_response_schema",
                        frontend_expects=o_txt,
                        backend_provides=b_txt,
                        risk="Medium",
                        suggestion=(
                            "Refresh the OpenAPI response schema to match serialized DTOs or rename backend properties "
                            "/ configure serializers so documentation reflects runtime JSON."
                        ),
                    )
                )

        o_req = openapi_documented_request_fields(oa)
        b_req = backend_request_field_names(be)
        if o_req or b_req:
            if _normalized_field_set(o_req) != _normalized_field_set(b_req):
                o_txt, b_txt = _describe_field_drift(o_req, b_req)
                mismatches.append(
                    ContractMismatch(
                        area="openapi_vs_code_request_schema",
                        frontend_expects=o_txt,
                        backend_provides=b_txt,
                        risk="Medium",
                        suggestion=(
                            "Align requestBody/parameters in OpenAPI with binding models and multipart field names."
                        ),
                    )
                )

    for j, o in enumerate(oa_list):
        if j in consumed_oa:
            continue
        mismatches.append(
            ContractMismatch(
                area="openapi_vs_code_missing_implementation",
                frontend_expects=f"OpenAPI documents `{o.method} {o.path}` (`{o.source}`)",
                backend_provides="Static backend scan found no confident matching route",
                risk="Medium",
                suggestion=(
                    "Implement the documented endpoint or remove it from the spec if it is obsolete."
                ),
            )
        )

    for b in be_list:
        if id(b) in paired_backend_ids:
            continue
        mismatches.append(
            ContractMismatch(
                area="openapi_vs_code_missing_spec",
                frontend_expects=f"Backend exposes `{b.method} {b.path}` (`{b.source}`)",
                backend_provides="No matching OpenAPI operation in discovered specs",
                risk="Low",
                suggestion="Export or hand-write OpenAPI coverage for this route so API consumers see accurate docs.",
            )
        )

    return mismatches


# Re-export helpers used by MCP/workflow
def summarize_openapi_drift_risk(mismatches: Iterable[ContractMismatch]) -> dict[str, int]:
    return summarize_risk_from_mismatches(mismatches).model_dump()


__all__ = [
    "collect_openapi_contracts",
    "compare_backend_to_openapi",
    "find_openapi_specs_under_root",
    "summarize_openapi_drift_risk",
    "yaml_supported",
]
