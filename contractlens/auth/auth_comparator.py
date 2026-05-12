"""Pair API contracts with auth heuristics and emit AuthMismatch rows."""

from __future__ import annotations

from typing import Iterable

from contractlens.auth.models import AuthMismatch, BackendAuthFinding, FrontendAuthFinding
from contractlens.contracts.comparator import path_similarity
from contractlens.contracts.models import ApiContract

_ROLE_RANK: dict[str, int] = {
    "admin": 100,
    "superadmin": 100,
    "architect": 90,
    "owner": 80,
    "user": 40,
    "client": 20,
    "guest": 10,
}


def _norm_role(r: str) -> str:
    return str(r).strip().lower()


def _role_rank(name: str) -> int:
    return _ROLE_RANK.get(_norm_role(name), 55)


def _best_backend_match(fe: ApiContract, backends: list[ApiContract]) -> ApiContract | None:
    same_method = [be for be in backends if be.method.upper() == fe.method.upper()]
    pool = same_method or backends
    best: tuple[float, ApiContract] | None = None
    for be in pool:
        sim = path_similarity(fe.path, be.path)
        if best is None or sim > best[0]:
            best = (sim, be)
    if best and best[0] >= 0.34:
        return best[1]
    return None


def _aggregate_frontend_file(findings: list[FrontendAuthFinding], source: str, up_to_line: int) -> dict[str, object]:
    rows = [f for f in findings if f.source == source and f.line <= up_to_line + 50]
    roles: set[str] = set()
    token = False
    wc = False
    guard = False
    for f in rows:
        roles.update(f.roles_mentioned)
        if f.has_authorization_header or f.has_bearer_token:
            token = True
        if f.has_with_credentials:
            wc = True
        if f.has_role_or_permission_check:
            guard = True
    max_rank = max((_role_rank(r) for r in roles), default=0)
    return {
        "roles": roles,
        "token_signal": token,
        "with_credentials": wc,
        "role_guard": guard,
        "max_fe_rank": max_rank,
    }


def _backend_rule_for_method(
    findings: list[BackendAuthFinding],
    source: str,
    method_line: int,
) -> dict[str, object]:
    """Infer backend auth for one route using attributes immediately above its HTTP verb line."""
    file_f = [f for f in findings if f.source == source]
    prelude_lo = max(1, method_line - 8)
    window = [f for f in file_f if method_line - 85 <= f.line <= method_line + 5]
    allow = any(f.allow_anonymous for f in window)
    roles: set[str] = set()
    policies: list[str] = []
    # Roles/policies: only attribute lines directly above this action (not earlier endpoints).
    for f in file_f:
        if f.kind != "authorize":
            continue
        if not (prelude_lo <= f.line <= method_line):
            continue
        roles.update(f.roles_required)
        if f.policy:
            policies.append(f.policy)
    roles_l = sorted(roles)
    has_authorize_before = any(f.kind == "authorize" and f.line <= method_line for f in file_f)
    if allow:
        auth_required = False
    else:
        auth_required = has_authorize_before or len(roles_l) > 0

    if roles_l:
        min_rank = min(_role_rank(r) for r in roles_l)
    elif auth_required:
        min_rank = 70
    else:
        min_rank = 0

    return {
        "auth_required": auth_required,
        "roles": roles_l,
        "allow_anonymous": allow,
        "min_required_rank": min_rank,
        "policies": policies,
    }


def compare_auth_contracts(
    frontend: Iterable[ApiContract],
    backend: Iterable[ApiContract],
    fe_auth: Iterable[FrontendAuthFinding],
    be_auth: Iterable[BackendAuthFinding],
) -> list[AuthMismatch]:
    fe_list = list(frontend)
    be_list = list(backend)
    fe_a = list(fe_auth)
    be_a = list(be_auth)
    out: list[AuthMismatch] = []
    emitted: set[tuple[str, str, str]] = set()

    def emit(area: str, fe_assumption: str, be_rule: str, risk: str, suggestion: str) -> None:
        key = (area, fe_assumption[:120], be_rule[:120])
        if key in emitted:
            return
        emitted.add(key)
        out.append(
            AuthMismatch(
                area=area,
                frontend_assumption=fe_assumption,
                backend_rule=be_rule,
                risk=risk,
                suggestion=suggestion,
            )
        )

    for fe in fe_list:
        be = _best_backend_match(fe, be_list)
        if not be or not be.line:
            continue

        fe_sig = _aggregate_frontend_file(fe_a, fe.source, fe.line or 0)
        be_rule = _backend_rule_for_method(be_a, be.source, be.line)

        auth_req = bool(be_rule["auth_required"])
        allow = bool(be_rule["allow_anonymous"])
        fe_roles: set[str] = set(str(x) for x in fe_sig["roles"])  # type: ignore[arg-type]
        be_roles = list(be_rule["roles"])  # type: ignore[assignment]
        fe_token = bool(fe_sig["token_signal"])
        fe_wc = bool(fe_sig["with_credentials"])
        fe_guard = bool(fe_sig["role_guard"])
        fe_max = int(fe_sig["max_fe_rank"])  # type: ignore[arg-type]
        be_min = int(be_rule["min_required_rank"])  # type: ignore[arg-type]

        pair_desc = f"{fe.method} `{fe.path}` ↔ `{be.source}`:{be.line}"
        policies_l = list(be_rule["policies"])  # type: ignore[arg-type]
        before_ct = len(out)

        if auth_req and not fe_token and not fe_wc:
            emit(
                "backend_requires_auth_frontend_missing_token",
                f"No Authorization/Bearer/withCredentials signal near `{fe.source}` around API line {fe.line} ({pair_desc})",
                f"Backend auth required (roles={be_roles or 'authenticated'} policies={policies_l})",
                "High",
                "Attach credentials (cookies via `withCredentials`, or `Authorization` bearer token) or expose an explicit `[AllowAnonymous]` route if public.",
            )

        if be_roles and fe_max > 0 and fe_max < be_min:
            emit(
                "frontend_allows_role_backend_blocks",
                f"Frontend hints imply weaker roles {sorted(fe_roles) or 'low-privilege UI'} (max heuristic rank {fe_max}) for {pair_desc}",
                f"Backend requires elevated roles: {', '.join(be_roles)}",
                "High",
                "Hide actions from insufficient roles in the UI or loosen `[Authorize(Roles=...)]` if self-service is intentional.",
            )

        if allow and fe_guard and not fe_roles.intersection({r for r in be_roles}):
            emit(
                "frontend_hides_route_backend_allows",
                f"Role/permission gates present in `{fe.source}` while calling {pair_desc}",
                f"`[AllowAnonymous]` or equivalent near `{be.source}`:{be.line}",
                "Medium",
                "Confirm anonymous access is intended—either simplify frontend guards or enforce authentication on the backend.",
            )

        if len(out) == before_ct:
            if policies_l:
                emit(
                    "unknown_auth_contract",
                    f"Backend declares authorization policies {policies_l} for {pair_desc}; frontend auth hints could not be reconciled automatically.",
                    "Review policy requirements vs UI/route guards manually.",
                    "Unknown",
                    "Map policies to concrete roles/claims in tests or docs, then align `[Authorize(Policy=...)]` with frontend permission checks.",
                )
            elif auth_req and fe_token:
                emit(
                    "unknown_auth_contract",
                    f"Credential/token signals exist near `{fe.source}` for {pair_desc}, but effective scopes vs backend rule are unclear.",
                    f"Backend auth_required=True roles={', '.join(be_roles) if be_roles else '(unspecified)'}",
                    "Unknown",
                    "Verify the token carries roles/scopes required by the backend for this route.",
                )

    return out


def compare_auth_contracts_from_dicts(
    fe_contracts: list[dict],
    be_contracts: list[dict],
    fe_auth: list[dict],
    be_auth: list[dict],
) -> list[AuthMismatch]:
    fe = [ApiContract.model_validate(x) for x in fe_contracts]
    be = [ApiContract.model_validate(x) for x in be_contracts]
    fa = [FrontendAuthFinding.model_validate(x) for x in fe_auth]
    ba = [BackendAuthFinding.model_validate(x) for x in be_auth]
    return compare_auth_contracts(fe, be, fa, ba)
