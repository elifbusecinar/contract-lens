"""Heuristic backend auth annotations (ASP.NET Core, light Express/FastAPI)."""

from __future__ import annotations

import re
from pathlib import Path

from contractlens.auth.models import BackendAuthFinding

_CS_EXT = {".cs"}
_JS_EXT = {".js", ".jsx", ".mjs", ".cjs"}
_PY_EXT = {".py"}

_AUTH_CLASS = re.compile(r"\[\s*Authorize\s*(?:\(([^)]*)\))?\s*\]")
_ALLOW_ANON = re.compile(r"\[\s*AllowAnonymous\s*\]")
_ROLES = re.compile(r"Roles\s*=\s*\"([^\"]+)\"", re.IGNORECASE)
_POLICY = re.compile(r"Policy\s*=\s*\"([^\"]+)\"", re.IGNORECASE)

_EXPRESS_AUTH = re.compile(
    r"\b(requireAuth|requireRole|authenticateToken|isAuthenticated|ensureAuthenticated)\s*\(",
    re.IGNORECASE,
)
_FASTAPI_DEP = re.compile(r"\bDepends\s*\(", re.IGNORECASE)
_FASTAPI_SEC = re.compile(r"\b(?:HTTPBearer|OAuth2PasswordBearer|HTTPAuthorizationCredentials)\b", re.IGNORECASE)


def scan_backend_auth(root: str | Path, relative_paths: list[str]) -> list[BackendAuthFinding]:
    base = Path(root).resolve()
    out: list[BackendAuthFinding] = []
    for rel in relative_paths:
        fp = base / rel
        if not fp.is_file():
            continue
        suf = fp.suffix.lower()
        text = fp.read_text(encoding="utf-8", errors="replace")
        display = rel.replace("\\", "/")
        if suf in _CS_EXT:
            out.extend(_scan_csharp(text, display))
        elif suf in _JS_EXT:
            out.extend(_scan_express(text, display))
        elif suf in _PY_EXT:
            out.extend(_scan_fastapi(text, display))
    return out


def _parse_authorize_args(inner: str | None) -> tuple[list[str], str | None]:
    if not inner or not inner.strip():
        return [], None
    rm = _ROLES.search(inner)
    roles = [x.strip() for x in rm.group(1).split(",")] if rm else []
    pm = _POLICY.search(inner)
    policy = pm.group(1).strip() if pm else None
    return roles, policy


def _scan_csharp(text: str, source_display: str) -> list[BackendAuthFinding]:
    findings: list[BackendAuthFinding] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if _ALLOW_ANON.search(stripped):
            findings.append(
                BackendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="allow_anonymous",
                    detail=stripped[:200],
                    roles_required=[],
                    policy=None,
                    auth_required=False,
                    allow_anonymous=True,
                )
            )
            continue
        am = _AUTH_CLASS.search(stripped)
        if am:
            roles, policy = _parse_authorize_args(am.group(1))
            findings.append(
                BackendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="authorize",
                    detail=stripped[:200],
                    roles_required=roles,
                    policy=policy,
                    auth_required=True,
                    allow_anonymous=False,
                )
            )
    return findings


def _scan_express(text: str, source_display: str) -> list[BackendAuthFinding]:
    findings: list[BackendAuthFinding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if _EXPRESS_AUTH.search(line):
            findings.append(
                BackendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="express_auth_middleware",
                    detail=line.strip()[:200],
                    roles_required=[],
                    policy=None,
                    auth_required=True,
                    allow_anonymous=False,
                )
            )
    return findings


def _scan_fastapi(text: str, source_display: str) -> list[BackendAuthFinding]:
    findings: list[BackendAuthFinding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if _FASTAPI_DEP.search(line) and _FASTAPI_SEC.search(line):
            findings.append(
                BackendAuthFinding(
                    source=source_display,
                    line=i,
                    kind="fastapi_security_dependency",
                    detail=line.strip()[:200],
                    roles_required=[],
                    policy=None,
                    auth_required=True,
                    allow_anonymous=False,
                )
            )
    return findings
