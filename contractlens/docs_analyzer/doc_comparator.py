"""Compare documentation claims to frontend, backend, and OpenAPI contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

from contractlens.contracts.comparator import path_similarity
from contractlens.contracts.models import ApiContract
from contractlens.docs_analyzer.doc_scanner import DocClaim


class DocumentationDriftMismatch(BaseModel):
    documentation_claim: str
    actual_implementation: str
    risk: str
    suggestion: str


def _dedupe_json_field_claims(claims: list[DocClaim]) -> list[DocClaim]:
    seen: set[tuple[str, str]] = set()
    out: list[DocClaim] = []
    for c in claims:
        if c.kind == "json_field":
            key = (c.source, c.claim.strip().lower())
            if key in seen:
                continue
            seen.add(key)
        out.append(c)
    return out


_SIM_THRESHOLD_WEAK = 0.34
_SIM_THRESHOLD_STRONG = 0.72


def _contract_priority(c: ApiContract) -> int:
    src = (c.source or "").lower()
    if src.endswith(".cs"):
        return 0
    if "openapi" in src or src.endswith(".yaml") or src.endswith(".yml"):
        return 2
    return 1


def _best_contract_for_path(
    doc_path: str,
    method: str | None,
    contracts: list[ApiContract],
) -> tuple[float, ApiContract | None]:
    pool = contracts
    if method:
        mf = [c for c in contracts if c.method.upper() == method.upper()]
        if mf:
            pool = mf
    best: tuple[float, ApiContract] | None = None
    for c in pool:
        sim = path_similarity(doc_path, c.path)
        cand = (sim, c)
        if best is None:
            best = cand
            continue
        bsim, bc = best
        if sim > bsim:
            best = cand
        elif sim == bsim:
            if _contract_priority(c) < _contract_priority(bc):
                best = cand
            elif _contract_priority(c) == _contract_priority(bc) and (c.path or "") < (bc.path or ""):
                best = cand
    if best is None:
        return 0.0, None
    return best[0], best[1]


def _fields_from_contract(c: ApiContract) -> Iterable[str]:
    for x in c.request_fields or []:
        yield x
    for x in c.response_fields or []:
        yield x
    rd = c.response_dto or ""
    if rd.startswith("anonymous"):
        inner = rd[len("anonymous") :].strip()
        inner = inner.strip("{}").strip()
        if inner:
            for part in inner.split(","):
                p = part.strip()
                if p:
                    yield p.split()[0] if p.split() else p


def _implemented_fields(contracts: list[ApiContract]) -> set[str]:
    return {str(x).strip() for c in contracts for x in _fields_from_contract(c) if str(x).strip()}


def _norm_fold(name: str) -> str:
    return name.lower().replace("_", "")


_CANON_PAIRS = (
    ("thumbnailUrl", "thumbnail_path"),
    ("thumbnail_url", "thumbnail_path"),
    ("name", "title"),
    ("createdAt", "created_at"),
    ("created_at", "createdAt"),
    ("projectId", "id"),
)


def _field_drifts(doc_field: str, implemented: set[str]) -> DocumentationDriftMismatch | None:
    df_strip = doc_field.strip()
    if not df_strip:
        return None
    impl_lower = {x.lower() for x in implemented}
    if df_strip.lower() in impl_lower:
        return None
    folds_implemented = {_norm_fold(x) for x in implemented}

    for a, b in _CANON_PAIRS:
        if df_strip == a or df_strip.lower() == a.lower():
            if b.lower() in impl_lower or _norm_fold(b) in folds_implemented:
                return DocumentationDriftMismatch(
                    documentation_claim=f'Docs/json mention field `{df_strip}` (known mismatch vs `{b}`)',
                    actual_implementation=f"Scanned contracts carry `{b}` but not `{df_strip}` in payload hints.",
                    risk="Medium",
                    suggestion=f"Align docs with `{b}` or change responses to emit `{df_strip}`.",
                )
        if df_strip == b or df_strip.lower() == b.lower():
            if a.lower() in impl_lower or _norm_fold(a) in folds_implemented:
                return DocumentationDriftMismatch(
                    documentation_claim=f'Docs/json mention field `{df_strip}`',
                    actual_implementation=f"Alternate name `{a}` appears in contracts—confirm canonical spelling.",
                    risk="Low",
                    suggestion="Pick one JSON property casing across docs and OpenAPI.",
                )

    if _norm_fold(df_strip) in folds_implemented:
        return None

    return DocumentationDriftMismatch(
        documentation_claim=f'Docs mention JSON/property `{df_strip}`',
        actual_implementation="No matching property found in scanned frontend/backend/OpenAPI field lists.",
        risk="Medium",
        suggestion="Remove stale docs or add the property to schemas if it is required.",
    )


def _collect_package_scripts(root: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    candidates = [root / "package.json", *sorted(root.glob("*/package.json"))]
    for pj in candidates:
        if not pj.is_file():
            continue
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        scripts = data.get("scripts")
        if not isinstance(scripts, dict):
            continue
        label = str(pj.parent.relative_to(root)).replace("\\", "/")
        if label == ".":
            label = "."
        clean = {str(k): str(v) for k, v in scripts.items() if isinstance(k, str) and isinstance(v, str)}
        if clean:
            out[label] = clean
    return out


def _any_package_json(root: Path) -> bool:
    return root.joinpath("package.json").is_file() or bool(list(root.glob("*/package.json")))


def _setup_command_drift(
    claim: DocClaim,
    scripts_by_pkg: dict[str, dict[str, str]],
    root: Path | None,
) -> DocumentationDriftMismatch | None:
    if claim.kind != "setup_command":
        return None
    raw = claim.claim.strip().lower()
    m = re.search(r"npm\s+run\s+([a-z0-9_.:-]+)", raw)
    if not m:
        return None
    script_name = m.group(1)
    all_scripts: set[str] = set()
    for mscripts in scripts_by_pkg.values():
        all_scripts.update(mscripts.keys())
    if script_name in all_scripts:
        return None
    if root and _any_package_json(root) and not scripts_by_pkg:
        return DocumentationDriftMismatch(
            documentation_claim=f"Docs/setup: `{claim.claim}` (`{claim.source}`:{claim.line})",
            actual_implementation="package.json exists under analyzed root but defines no `scripts` block.",
            risk="Low",
            suggestion="Add a `scripts` section (e.g. `\"dev\": \"...\"`) or adjust docs to match the repo.",
        )
    loc = ", ".join(sorted(scripts_by_pkg.keys())) if scripts_by_pkg else "(no package.json scripts discovered)"
    return DocumentationDriftMismatch(
        documentation_claim=f"Docs/setup: `{claim.claim}` (`{claim.source}`:{claim.line})",
        actual_implementation=f"No `scripts.{script_name}` in scanned package.json files ({loc}).",
        risk="Low",
        suggestion="Fix docs to reference an existing npm script or define `scripts.{script_name}` in package.json.",
    )


def compare_documentation_drift(
    frontend: Iterable[ApiContract],
    backend: Iterable[ApiContract],
    openapi_rows: Iterable[ApiContract],
    claims: Iterable[DocClaim],
    *,
    repo_root: str | Path | None = None,
) -> list[DocumentationDriftMismatch]:
    fe_list = list(frontend)
    be_list = list(backend)
    oa_list = list(openapi_rows)
    contracts = fe_list + be_list + oa_list
    # Fields: backend-only ground truth when controllers exist (avoid masking FE/OA optimism).
    if be_list:
        impl_fields = _implemented_fields(be_list)
    else:
        impl_fields = _implemented_fields(contracts)
    scripts_map: dict[str, dict[str, str]] = {}
    root_path: Path | None = None
    if repo_root is not None:
        root_path = Path(repo_root).resolve()
        scripts_map = _collect_package_scripts(root_path)

    out: list[DocumentationDriftMismatch] = []
    emitted: set[tuple[str, str]] = set()

    def _sig(mm: DocumentationDriftMismatch) -> tuple[str, str]:
        dc = mm.documentation_claim
        if " (`" in dc:
            dc = dc.split(" (`", 1)[0].strip()
        return (dc[:180], mm.actual_implementation[:180])

    def emit(mm: DocumentationDriftMismatch) -> None:
        key = _sig(mm)
        if key in emitted:
            return
        emitted.add(key)
        out.append(mm)

    claim_list = _dedupe_json_field_claims(list(claims))

    for cl in claim_list:
        if cl.kind == "endpoint" and cl.method and cl.path:
            sim, best = _best_contract_for_path(cl.path, cl.method, contracts)
            if best is None:
                emit(
                    DocumentationDriftMismatch(
                        documentation_claim=f"{cl.claim} (`{cl.source}`:{cl.line})",
                        actual_implementation="No scanned frontend/backend/OpenAPI route matched this path/method.",
                        risk="High",
                        suggestion="Correct the docs path/method or implement the missing endpoint.",
                    )
                )
                continue
            if sim < _SIM_THRESHOLD_WEAK:
                emit(
                    DocumentationDriftMismatch(
                        documentation_claim=f"{cl.claim} (`{cl.source}`:{cl.line})",
                        actual_implementation=f'Closest scanned route: `{best.method} {best.path}` (`{best.source}`) similarity={sim:.2f}',
                        risk="High",
                        suggestion="Align documented routes with controller/client/OpenAPI paths.",
                    )
                )
            elif sim < _SIM_THRESHOLD_STRONG or cl.path.strip().rstrip("/") != best.path.strip().rstrip("/"):
                emit(
                    DocumentationDriftMismatch(
                        documentation_claim=f"{cl.claim} (`{cl.source}`:{cl.line})",
                        actual_implementation=(
                            f'Implementation reference: `{best.method} {best.path}` (`{best.source}` line {best.line or "?"}) '
                            f"match_score≈{sim:.2f}"
                        ),
                        risk="Medium",
                        suggestion="Update docs to the real template path or add a backward-compatible alias route.",
                    )
                )

        elif cl.kind == "endpoint_path_only" and cl.path:
            sim_get, best_get = _best_contract_for_path(cl.path, "GET", contracts)
            sim_any, best_any = _best_contract_for_path(cl.path, None, contracts)
            sim, best = (sim_get, best_get) if sim_get >= sim_any else (sim_any, best_any)
            if best is None or sim < _SIM_THRESHOLD_WEAK:
                emit(
                    DocumentationDriftMismatch(
                        documentation_claim=f"{cl.claim} (`{cl.source}`:{cl.line})",
                        actual_implementation="No scanned route strongly matches this documented path.",
                        risk="Medium",
                        suggestion="Document the HTTP method and exact route template used by the backend.",
                    )
                )
            elif sim < _SIM_THRESHOLD_STRONG:
                emit(
                    DocumentationDriftMismatch(
                        documentation_claim=f"{cl.claim} (`{cl.source}`:{cl.line})",
                        actual_implementation=f'Closest: `{best.method} {best.path}` (`{best.source}`) score≈{sim:.2f}',
                        risk="Low",
                        suggestion="Clarify path templates (`{{id}}` vs literal segments) in documentation.",
                    )
                )

        elif cl.kind == "json_field":
            mm = _field_drifts(cl.claim, impl_fields)
            if mm:
                mm.documentation_claim = f"{mm.documentation_claim} (`{cl.source}`:{cl.line})"
                emit(mm)

        elif cl.kind == "setup_command" and root_path is not None:
            mm = _setup_command_drift(cl, scripts_map, root_path)
            if mm:
                emit(mm)

    return out


def compare_documentation_drift_from_dicts(
    fe_contracts: list[dict],
    be_contracts: list[dict],
    openapi_contracts: list[dict],
    documentation_claims: list[dict],
    *,
    repo_root: str | None = None,
) -> list[DocumentationDriftMismatch]:
    fe = [ApiContract.model_validate(x) for x in fe_contracts]
    be = [ApiContract.model_validate(x) for x in be_contracts]
    oa = [ApiContract.model_validate(x) for x in openapi_contracts]
    claims = [DocClaim.model_validate(x) for x in documentation_claims]
    return compare_documentation_drift(fe, be, oa, claims, repo_root=repo_root)
