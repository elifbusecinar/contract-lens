"""Extract backend routes from ASP.NET controllers and light Express/FastAPI."""

from __future__ import annotations

import re
from pathlib import Path

from contractlens.contracts.models import ApiContract
from contractlens.scanner import scan_cache as scan_cache_mod


class _RouteCtx:
    def __init__(self) -> None:
        self.base = ""
        self.auth: str | None = None


def _strip_attr(s: str) -> str:
    return s.strip().strip('"').strip("'")


def _scan_csharp(text: str, source_display: str) -> list[ApiContract]:
    lines = text.splitlines()
    ctx = _RouteCtx()
    findings: list[ApiContract] = []

    route_class_re = re.compile(r'\[Route\s*\(\s*"([^"]*)"')
    http_re = re.compile(r"\[Http(Get|Post|Put|Delete|Patch)\s*(?:\(\s*\"([^\"]*)\"\s*\))?\]")
    auth_re = re.compile(r"\[(Authorize|AllowAnonymous)")

    current_method: str | None = None
    current_template: str = ""
    pending_http_line = 0

    for i, line in enumerate(lines, start=1):
        rm = route_class_re.search(line)
        if rm:
            ctx.base = _strip_attr(rm.group(1)).strip("/")

        if auth_re.search(line):
            m = auth_re.search(line)
            if m:
                ctx.auth = m.group(1)

        hm = http_re.search(line)
        if hm:
            verb = hm.group(1).upper()
            tpl = (hm.group(2) or "").strip("/")
            current_method = verb
            current_template = tpl
            pending_http_line = i

        stripped = line.strip()
        sig_m = re.search(
            r"public\s+(?:async\s+)?(?:Task<[^>]+>|IActionResult|ActionResult[^)]*)\s+\w+\s*\([^)]*\)",
            stripped,
        )
        if sig_m and current_method and pending_http_line:
            params = ""
            sig_full_m = re.match(
                r"public\s+(?:async\s+)?(?:Task<[^>]+>|IActionResult|ActionResult<\w+>|ActionResult)\s+(\w+)\s*\(([^)]*)\)",
                stripped,
            )
            if sig_full_m:
                params = sig_full_m.group(2)
            req_dto = _csharp_request_dto(params)
            resp_dto = _csharp_response_hint(lines, i)

            path = "/" + "/".join(p for p in [ctx.base, current_template] if p)
            if not path.startswith("/"):
                path = "/" + path

            findings.append(
                ApiContract(
                    method=current_method,
                    path=path,
                    source=source_display,
                    line=pending_http_line,
                    request_fields=[],
                    response_fields=[],
                    request_dto=req_dto,
                    response_dto=resp_dto,
                    auth=ctx.auth,
                )
            )
            current_method = None
            current_template = ""

    return findings


def _csharp_request_dto(params: str) -> str | None:
    if not params.strip():
        return None
    parts = [p.strip() for p in params.split(",") if p.strip()]
    types: list[str] = []
    for p in parts:
        tokens = p.split()
        if len(tokens) >= 2:
            types.append(tokens[-2])
    return ", ".join(types) if types else None


def _csharp_response_hint(lines: list[str], sig_line_idx: int) -> str | None:
    window = "\n".join(lines[sig_line_idx - 1 : min(len(lines), sig_line_idx + 40)])
    m = re.search(r"Ok\s*\(\s*new\s*\{([^}]*)\}", window, re.DOTALL)
    if not m:
        m = re.search(r"return\s+Ok\s*\(\s*new\s*\{([^}]*)\}", window, re.DOTALL)
    if m:
        keys = re.findall(r"(\w+)\s*=", m.group(1))
        return "anonymous {" + ", ".join(keys) + "}" if keys else "anonymous {}"
    return None


_EXPRESS_RE = re.compile(
    r"(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*[`\"']([^`\"']+)[`\"']",
    re.IGNORECASE,
)
_EXPRESS_BT = re.compile(
    r"(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*`([^`]+)`",
    re.IGNORECASE,
)


def _scan_express(text: str, source_display: str) -> list[ApiContract]:
    findings: list[ApiContract] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in _EXPRESS_BT.finditer(line):
            findings.append(
                ApiContract(
                    method=m.group(1).upper(),
                    path=m.group(2),
                    source=source_display,
                    line=i,
                    auth=None,
                )
            )
        for m in _EXPRESS_RE.finditer(line):
            findings.append(
                ApiContract(
                    method=m.group(1).upper(),
                    path=m.group(2),
                    source=source_display,
                    line=i,
                    auth=None,
                )
            )
    return findings


_FASTAPI_DECORATOR = re.compile(
    r"@(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)


def _scan_fastapi(text: str, source_display: str) -> list[ApiContract]:
    findings: list[ApiContract] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in _FASTAPI_DECORATOR.finditer(line):
            findings.append(
                ApiContract(
                    method=m.group(1).upper(),
                    path=m.group(2),
                    source=source_display,
                    line=i,
                    auth=None,
                )
            )
    return findings


def scan_file(path: str | Path, source_root: str | Path | None = None) -> list[ApiContract]:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    display = str(p)
    if source_root:
        try:
            display = str(p.resolve().relative_to(Path(source_root).resolve())).replace("\\", "/")
        except ValueError:
            display = str(p.resolve())

    suf = p.suffix.lower()
    out: list[ApiContract] = []
    if suf == ".cs":
        out.extend(_scan_csharp(text, display))
    out.extend(_scan_express(text, display))
    out.extend(_scan_fastapi(text, display))
    return out


def scan_backend(root: str | Path, relative_paths: list[str], *, use_scan_cache: bool = False) -> list[ApiContract]:
    base = Path(root).resolve()
    out: list[ApiContract] = []
    for rel in relative_paths:
        fp = base / rel
        if not fp.is_file():
            continue
        if use_scan_cache:
            hit = scan_cache_mod.load_cached_contracts(base, rel, "backend")
            if hit is not None:
                out.extend(hit)
                continue
        contracts = scan_file(fp, base)
        if use_scan_cache:
            scan_cache_mod.save_cached_contracts(base, rel, "backend", contracts)
        out.extend(contracts)
    return out
