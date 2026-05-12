"""Compare frontend expectations with backend routes — heuristic MVP comparator."""

from __future__ import annotations

import re
from typing import Iterable

from contractlens.contracts.models import ApiContract, ContractMismatch, RiskSummary


def _inline_anchor(fe: ApiContract) -> tuple[str | None, int | None]:
    """Repo-relative path + 1-based line on the frontend contract row (for PR inline comments)."""
    raw = (fe.source or "").strip().replace("\\", "/")
    parts = [p for p in raw.split("/") if p]
    if any(p == ".." for p in parts):
        return None, None
    path_out = "/".join(parts) if parts else None
    ln = fe.line if isinstance(fe.line, int) and fe.line >= 1 else None
    return path_out, ln


def _tokens(path: str) -> list[str]:
    p = path.split("?", 1)[0].strip()
    parts = [x for x in p.strip("/").split("/") if x]
    out: list[str] = []
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            out.append("{param}")
        elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", part):
            out.append(part.lower())
        else:
            out.append(part.lower())
    return out


def _path_similarity(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    common = sum(1 for x in ta if x in tb)
    return common / max(len(ta), len(tb))


def _best_backend_match(fe: ApiContract, backends: list[ApiContract]) -> ApiContract | None:
    same_method = [be for be in backends if be.method.upper() == fe.method.upper()]
    pool = same_method or backends
    best: tuple[float, ApiContract] | None = None
    for be in pool:
        sim = _path_similarity(fe.path, be.path)
        if best is None or sim > best[0]:
            best = (sim, be)
    if best and best[0] >= 0.34:
        return best[1]
    return None


_CANON = [
    ("id", "projectid"),
    ("projectid", "id"),
    ("thumbnailurl", "thumbnail_path"),
    ("thumbnail_path", "thumbnailurl"),
    ("name", "title"),
    ("title", "name"),
    ("createdat", "created_at"),
    ("created_at", "createdat"),
]


def _field_mismatch_pair(a: str, b: str) -> bool:
    aa, bb = a.lower(), b.lower()
    if aa == bb:
        return False
    for x, y in _CANON:
        if (aa == x and bb == y) or (aa == y and bb == x):
            return True
    return aa.replace("_", "") != bb.replace("_", "")


def _backend_response_tokens(be: ApiContract) -> set[str]:
    toks: set[str] = set()
    if be.response_dto:
        for m in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", be.response_dto):
            if m.group(1).lower() == "anonymous":
                continue
            toks.add(m.group(1))
    return toks


def _compare_fields(fe: ApiContract, be: ApiContract | None) -> list[ContractMismatch]:
    out: list[ContractMismatch] = []
    cp, cl = _inline_anchor(fe)
    if not be:
        return out

    backend_tokens = _backend_response_tokens(be)

    for rf in fe.response_fields:
        if not any(not _field_mismatch_pair(rf, bf) for bf in backend_tokens):
            guess = ", ".join(sorted(backend_tokens)) or "(none inferred)"
            risk = "High" if rf.lower() in {"id", "thumbnailurl"} else "Medium"
            out.append(
                ContractMismatch(
                    area="response_field",
                    frontend_expects=rf,
                    backend_provides=guess,
                    risk=risk,
                    suggestion=(
                        f"Align JSON property `{rf}` with backend naming or map in the client "
                        f"(backend hints: {guess})."
                    ),
                    comment_path=cp,
                    comment_line=cl,
                )
            )

    if fe.request_fields and be.request_dto:
        fe_blob = " ".join(fe.request_fields).lower()
        be_blob = be.request_dto.lower()
        if "file" in fe_blob and "iformfile" not in be_blob and "multipart" not in be_blob:
            out.append(
                ContractMismatch(
                    area="request_shape",
                    frontend_expects="multipart file upload",
                    backend_provides=be.request_dto,
                    risk="Medium",
                    suggestion=(
                        "Confirm backend expects IFormFile/multipart and the frontend sends "
                        "FormData with the field name the action binds."
                    ),
                    comment_path=cp,
                    comment_line=cl,
                )
            )

    return out


def path_similarity(a: str, b: str) -> float:
    """Public wrapper for workflow/OpenAPI drift pairing."""
    return _path_similarity(a, b)


def normalized_path_tokens(path: str) -> tuple[str, ...]:
    """Stable route shape token tuple for equality checks."""
    return tuple(_tokens(path))


def summarize_risk_from_mismatches(mismatches: Iterable[ContractMismatch]) -> RiskSummary:
    summary = RiskSummary()
    for m in mismatches:
        k = m.risk.lower()
        if k == "high":
            summary.high += 1
        elif k == "medium":
            summary.medium += 1
        elif k == "low":
            summary.low += 1
        else:
            summary.unknown += 1
    return summary


def compare_contracts(
    frontend: Iterable[ApiContract],
    backend: Iterable[ApiContract],
) -> tuple[list[ContractMismatch], RiskSummary]:
    fe_list = list(frontend)
    be_list = list(backend)
    mismatches: list[ContractMismatch] = []

    for fe in fe_list:
        cp, cl = _inline_anchor(fe)
        be = _best_backend_match(fe, be_list)
        if not be:
            mismatches.append(
                ContractMismatch(
                    area="missing_endpoint",
                    frontend_expects=f"{fe.method} {fe.path}",
                    backend_provides="no confident backend match",
                    risk="High",
                    suggestion=(
                        "Add a backend route matching this method/path or update the frontend to call "
                        "the existing backend endpoint."
                    ),
                    comment_path=cp,
                    comment_line=cl,
                )
            )
            continue

        if fe.method.upper() != be.method.upper():
            mismatches.append(
                ContractMismatch(
                    area="http_method",
                    frontend_expects=fe.method,
                    backend_provides=be.method,
                    risk="High",
                    suggestion="Align HTTP verbs between client and server for this operation.",
                    comment_path=cp,
                    comment_line=cl,
                )
            )

        sim = _path_similarity(fe.path, be.path)
        if sim < 0.85 or _tokens(fe.path) != _tokens(be.path):
            mismatches.append(
                ContractMismatch(
                    area="path",
                    frontend_expects=fe.path,
                    backend_provides=be.path,
                    risk="High",
                    suggestion=(
                        "Align the frontend upload path with the backend route (e.g. `/files` vs `/models`) "
                        "or add a compatibility alias endpoint."
                    ),
                    comment_path=cp,
                    comment_line=cl,
                )
            )

        if be.auth == "Authorize":
            mismatches.append(
                ContractMismatch(
                    area="auth",
                    frontend_expects="not inferred (MVP static scan)",
                    backend_provides="[Authorize]",
                    risk="Medium",
                    suggestion=(
                        "Ensure the frontend obtains and sends credentials (cookies/Bearer token) required "
                        "by authorized endpoints."
                    ),
                    comment_path=cp,
                    comment_line=cl,
                )
            )

        mismatches.extend(_compare_fields(fe, be))

    summary = summarize_risk_from_mismatches(mismatches)

    return mismatches, summary
