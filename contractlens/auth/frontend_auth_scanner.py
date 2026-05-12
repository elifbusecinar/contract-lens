"""Heuristic frontend auth / role signal extraction (.ts, .tsx, .js, .jsx, .vue)."""

from __future__ import annotations

import re
from pathlib import Path

from contractlens.auth.models import FrontendAuthFinding

_FE_EXT = {".ts", ".tsx", ".js", ".jsx", ".vue"}

_HAS_ROLE = re.compile(r"hasRole\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
_CAN = re.compile(r"\bcan\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
_PERMISSION = re.compile(r"permission(?:s)?\.(?:has|includes)\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
_IS_ROLE = re.compile(r"\bis(Admin|Owner|Client|Architect)\b", re.IGNORECASE)
_ROLE_COMPARE = re.compile(
    r"(?:role|roles)\s*(?:===|==|\.includes)\s*['\"]([^'\"]+)['\"]|['\"]([^'\"]+)['\"]\s*(?:===|==)\s*(?:role|user\.role)",
    re.IGNORECASE,
)
_WITH_CRED = re.compile(r"withCredentials\s*:\s*true", re.IGNORECASE)
_AUTH_HEADER = re.compile(r"Authorization\s*:|['\"]Authorization['\"]\s*:", re.IGNORECASE)
_BEARER = re.compile(r"Bearer\s+|accessToken|idToken|authToken|getToken\s*\(", re.IGNORECASE)
_PROTECTED_ROUTE = re.compile(
    r"<(?:ProtectedRoute|PrivateRoute|RequireAuth)|requiredRoles\s*=|permissions\s*=\s*\[",
    re.IGNORECASE,
)


def scan_frontend_auth(root: str | Path, relative_paths: list[str]) -> list[FrontendAuthFinding]:
    base = Path(root).resolve()
    out: list[FrontendAuthFinding] = []
    for rel in relative_paths:
        suf = Path(rel).suffix.lower()
        if suf not in _FE_EXT:
            continue
        fp = base / rel
        if not fp.is_file():
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        display = rel.replace("\\", "/")
        out.extend(_scan_text(text, display))
    return out


def _scan_text(text: str, source_display: str) -> list[FrontendAuthFinding]:
    findings: list[FrontendAuthFinding] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        roles: list[str] = []
        has_auth_h = bool(_AUTH_HEADER.search(line))
        has_bearer = bool(_BEARER.search(line))
        has_wc = bool(_WITH_CRED.search(line))
        has_guard = bool(_HAS_ROLE.search(line) or _CAN.search(line) or _PROTECTED_ROUTE.search(line))

        for m in _HAS_ROLE.finditer(line):
            roles.append(m.group(1).strip())
        for m in _CAN.finditer(line):
            roles.append(m.group(1).strip())
        for m in _PERMISSION.finditer(line):
            roles.append(m.group(1).strip())
        for m in _IS_ROLE.finditer(line):
            roles.append(m.group(1).strip())
        for m in _ROLE_COMPARE.finditer(line):
            g1, g2 = m.group(1), m.group(2)
            if g1:
                roles.append(g1.strip())
            if g2:
                roles.append(g2.strip())

        roles = sorted({r for r in roles if r})

        if has_guard:
            findings.append(
                FrontendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="role_or_permission_check",
                    detail=line.strip()[:200],
                    roles_mentioned=roles,
                    has_authorization_header=has_auth_h,
                    has_bearer_token=has_bearer,
                    has_with_credentials=has_wc,
                    has_role_or_permission_check=True,
                )
            )
        elif has_auth_h or has_bearer:
            findings.append(
                FrontendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="authorization_header_or_token",
                    detail=line.strip()[:200],
                    roles_mentioned=roles,
                    has_authorization_header=has_auth_h,
                    has_bearer_token=has_bearer,
                    has_with_credentials=has_wc,
                    has_role_or_permission_check=False,
                )
            )
        elif has_wc:
            findings.append(
                FrontendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="axios_with_credentials",
                    detail=line.strip()[:200],
                    roles_mentioned=roles,
                    has_authorization_header=False,
                    has_bearer_token=False,
                    has_with_credentials=True,
                    has_role_or_permission_check=False,
                )
            )

    return findings
