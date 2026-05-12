"""Extract frontend HTTP calls from TS/JS/Vue sources."""

from __future__ import annotations

import re
from pathlib import Path

from contractlens.contracts.models import ApiContract
from contractlens.scanner import scan_cache as scan_cache_mod


_FETCH_RE = re.compile(
    r"\bfetch\s*\(\s*[`\"']([^`\"']+)[`\"']",
    re.MULTILINE,
)
_FETCH_BT = re.compile(
    r"\bfetch\s*\(\s*`([^`]+)`",
    re.MULTILINE,
)
_AXIOS_RE = re.compile(
    r"\baxios\.(get|post|put|delete|patch)\s*\(\s*[`\"']([^`\"']+)[`\"']",
    re.IGNORECASE | re.MULTILINE,
)
_AXIOS_BT = re.compile(
    r"\baxios\.(get|post|put|delete|patch)\s*\(\s*`([^`]+)`",
    re.IGNORECASE | re.MULTILINE,
)
_APICLIENT_RE = re.compile(
    r"\bapiClient\.(get|post|put|delete|patch)\s*\(\s*[`\"']([^`\"']+)[`\"']",
    re.IGNORECASE | re.MULTILINE,
)
_APICLIENT_BT = re.compile(
    r"\bapiClient\.(get|post|put|delete|patch)\s*\(\s*`([^`]+)`",
    re.IGNORECASE | re.MULTILINE,
)
_TEMPLATE_VAR_RE = re.compile(r"\$\{([^}]+)\}")


def _normalize_path(raw: str) -> str:
    """Turn `/api/foo/${id}` into `/api/foo/{id}` for readable drift reporting."""

    def _repl(m: re.Match[str]) -> str:
        inner = m.group(1).strip()
        return "{" + inner + "}" if inner else "{param}"

    return _TEMPLATE_VAR_RE.sub(_repl, raw.strip())


def _guess_fields_from_object_literal(block: str, prefix: str) -> list[str]:
    """Very small heuristic: keys in `{ key:` or `key:` at line starts."""
    keys: list[str] = []
    for m in re.finditer(r"(?:^\s*|\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", block):
        k = m.group(1)
        if k not in ("return", "if", "else", "await", "async", "new", "type"):
            keys.append(k)
    return list(dict.fromkeys(keys))


def extract_response_fields_near_line(lines: list[str], line_idx: int) -> list[str]:
    """Look a few lines ahead for `response.data.foo` or destructuring."""
    window = "\n".join(lines[max(0, line_idx - 2) : min(len(lines), line_idx + 25)])
    fields: list[str] = []

    for m in re.finditer(r"response\.data\.([a-zA-Z_][a-zA-Z0-9_]*)", window):
        fields.append(m.group(1))
    for m in re.finditer(r"\.data\.([a-zA-Z_][a-zA-Z0-9_]*)", window):
        fields.append(m.group(1))
    # Common pattern: `const data = await res.json(); ... data.title`
    for m in re.finditer(r"\bdata\.([a-zA-Z_][a-zA-Z0-9_]*)", window):
        fields.append(m.group(1))

    dm = re.search(r"const\s*\{\s*([^}]+)\}\s*=\s*response\.data", window)
    if dm:
        inner = dm.group(1)
        for part in inner.split(","):
            name = part.strip().split(":")[0].strip()
            if name and re.match(r"^[a-zA-Z_]", name):
                fields.append(name)

    robj = re.search(r"return\s*\{([^}]{1,400})\}", window, re.DOTALL)
    if robj:
        fields.extend(_guess_fields_from_object_literal(robj.group(1), "ret"))

    return list(dict.fromkeys(fields))


def extract_request_fields_near_line(lines: list[str], line_idx: int) -> list[str]:
    window = "\n".join(lines[max(0, line_idx - 3) : min(len(lines), line_idx + 20)])
    fields: list[str] = []
    if "FormData" in window or "formData" in window:
        fields.append("file")
    if "JSON.stringify" in window:
        mobj = re.search(r"JSON\.stringify\s*\(\s*\{([^}]*)\}", window)
        if mobj:
            fields.extend(_guess_fields_from_object_literal("{" + mobj.group(1) + "}", ""))
    return list(dict.fromkeys(fields))


def scan_file(path: str | Path, source_root: str | Path | None = None) -> list[ApiContract]:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings: list[ApiContract] = []
    display = str(p)
    if source_root:
        try:
            display = str(p.resolve().relative_to(Path(source_root).resolve())).replace("\\", "/")
        except ValueError:
            display = str(p.resolve())

    def add(method: str, url: str, line_no: int) -> None:
        findings.append(
            ApiContract(
                method=method.upper(),
                path=_normalize_path(url),
                source=display,
                line=line_no,
                request_fields=extract_request_fields_near_line(lines, line_no - 1),
                response_fields=extract_response_fields_near_line(lines, line_no - 1),
            )
        )

    for i, line in enumerate(lines, start=1):
        for m in _FETCH_BT.finditer(line):
            add("GET", m.group(1), i)
        for m in _FETCH_RE.finditer(line):
            add("GET", m.group(1), i)
        for m in _AXIOS_BT.finditer(line):
            add(m.group(1).upper(), m.group(2), i)
        for m in _AXIOS_RE.finditer(line):
            add(m.group(1).upper(), m.group(2), i)
        for m in _APICLIENT_BT.finditer(line):
            add(m.group(1).upper(), m.group(2), i)
        for m in _APICLIENT_RE.finditer(line):
            add(m.group(1).upper(), m.group(2), i)

    seen: set[tuple[str, str, int, str]] = set()
    uniq: list[ApiContract] = []
    for c in findings:
        k = (c.method.upper(), c.path, c.line or 0, c.source)
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    return uniq


def scan_frontend(root: str | Path, relative_paths: list[str], *, use_scan_cache: bool = False) -> list[ApiContract]:
    base = Path(root).resolve()
    out: list[ApiContract] = []
    for rel in relative_paths:
        suf = Path(rel).suffix.lower()
        if suf not in {".ts", ".tsx", ".js", ".jsx", ".vue"}:
            continue
        fp = base / rel
        if not fp.is_file():
            continue
        if use_scan_cache:
            hit = scan_cache_mod.load_cached_contracts(base, rel, "frontend")
            if hit is not None:
                out.extend(hit)
                continue
        contracts = scan_file(fp, base)
        if use_scan_cache:
            scan_cache_mod.save_cached_contracts(base, rel, "frontend", contracts)
        out.extend(contracts)
    return out
