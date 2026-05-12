"""Deterministic extraction of documentation claims from Markdown."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class DocClaim(BaseModel):
    """Single heuristic extraction from a documentation file."""

    kind: str
    """endpoint | endpoint_path_only | json_field | env_var | setup_command | feature_heading"""

    claim: str
    source: str
    line: int
    detail: str = ""
    method: str | None = None
    path: str | None = None


_ENDPOINT_PAIR = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\s+[`\"']?(/[^\s`'\")\]]+)",
    re.IGNORECASE,
)
_BTICK_PATH = re.compile(r"`(/[^\s`]+)`")
_JSON_STRING_KEYS = re.compile(r'"([a-zA-Z][a-zA-Z0-9_]*)"')
_NPM_RUN = re.compile(r"\bnpm\s+run\s+([a-zA-Z0-9_.:-]+)\b", re.IGNORECASE)
_PNPM_YARN_RUN = re.compile(r"\b(pnpm|yarn)\s+(?:run\s+)?([a-zA-Z0-9_.:-]+)\b", re.IGNORECASE)
_SETUP_BTICK = re.compile(r"`(npm\s+[^`]+|pnpm\s+[^`]+|yarn\s+[^`]+|pip3?\s+[^`]+|python\s+-m\s+[^`]+)`")
_HEADING = re.compile(r"^#{1,3}\s+(.+)\s*$")
_ENV_ASSIGN = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\s*=")

_STOPWORDS = frozenset(
    x.lower()
    for x in """
    this that with from demo sample project upload file when what your will must required
    path route endpoint json schema returns detail overview docs readme guide about using type object array string description uuid datetime multipart application localhost summary parameters responses examples optional configure installation prerequisites introduction contents metadata swagger openapi contract property properties items required enum format title version servers components request response example model view controller action http https boolean integer number null content encoding token bearer auth scope operation id ref get post put patch delete info servers paths webhook callbacks nullable deprecated discriminator xml nullable exclusivemaximum exclusiveminimum multipleof maxitems minitems uniqueitems maxproperties minproperties extravalues additionalproperties patternproperties allof anyof oneof not
    """.split()
)


def _field_candidate(tok: str) -> bool:
    t = tok.strip()
    if len(t) < 4:
        return False
    if t.lower() in _STOPWORDS:
        return False
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", t))


def scan_documentation(root: str | Path, relative_paths: list[str]) -> list[DocClaim]:
    base = Path(root).resolve()
    out: list[DocClaim] = []
    md_paths = sorted(
        rel.replace("\\", "/") for rel in relative_paths if rel.lower().endswith(".md")
    )
    for rel in md_paths:
        fp = base / rel
        if not fp.is_file():
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        disp = rel.replace("\\", "/")
        out.extend(_scan_file_lines(disp, text))
        out.extend(_scan_fenced_json(disp, text))
    return out


def _scan_file_lines(display_rel: str, text: str) -> list[DocClaim]:
    claims: list[DocClaim] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        hm = _HEADING.match(stripped)
        if hm:
            title = hm.group(1).strip()
            if len(title) >= 3:
                claims.append(
                    DocClaim(
                        kind="feature_heading",
                        claim=f"Heading: {title}",
                        source=display_rel,
                        line=i,
                        detail=stripped[:200],
                    )
                )

        for m in _ENDPOINT_PAIR.finditer(line):
            method = m.group(1).upper()
            path = m.group(2).strip()
            claims.append(
                DocClaim(
                    kind="endpoint",
                    claim=f"{method} {path}",
                    source=display_rel,
                    line=i,
                    detail=stripped[:200],
                    method=method,
                    path=path,
                )
            )

        for m in _BTICK_PATH.finditer(line):
            path = m.group(1).strip()
            if "/" not in path:
                continue
            claims.append(
                DocClaim(
                    kind="endpoint_path_only",
                    claim=f"`{path}`",
                    source=display_rel,
                    line=i,
                    detail=stripped[:200],
                    path=path,
                )
            )

        for m in _ENV_ASSIGN.finditer(line):
            claims.append(
                DocClaim(
                    kind="env_var",
                    claim=m.group(1),
                    source=display_rel,
                    line=i,
                    detail=stripped[:200],
                )
            )

        rm = _NPM_RUN.search(line)
        if rm:
            claims.append(
                DocClaim(
                    kind="setup_command",
                    claim=f"npm run {rm.group(1)}",
                    source=display_rel,
                    line=i,
                    detail=stripped[:200],
                )
            )
        pm = _PNPM_YARN_RUN.search(line)
        if pm:
            claims.append(
                DocClaim(
                    kind="setup_command",
                    claim=f"{pm.group(1)} {pm.group(2)}",
                    source=display_rel,
                    line=i,
                    detail=stripped[:200],
                )
            )
        for sm in _SETUP_BTICK.finditer(line):
            claims.append(
                DocClaim(
                    kind="setup_command",
                    claim=sm.group(1).strip(),
                    source=display_rel,
                    line=i,
                    detail=stripped[:200],
                )
            )

        for m in _JSON_STRING_KEYS.finditer(line):
            tok = m.group(1)
            if not _field_candidate(tok):
                continue
            claims.append(
                DocClaim(
                    kind="json_field",
                    claim=tok,
                    source=display_rel,
                    line=i,
                    detail=stripped[:180],
                )
            )

    return claims


def _scan_fenced_json(display_rel: str, text: str) -> list[DocClaim]:
    claims: list[DocClaim] = []
    pattern = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)

    for m in pattern.finditer(text):
        body = m.group(1)
        approx_line = text[: m.start()].count("\n") + 1
        claims.extend(_json_body_claims(display_rel, body, approx_line))

    return claims


def _json_body_claims(display_rel: str, body: str, approx_line: int) -> list[DocClaim]:
    claims: list[DocClaim] = []
    blob = body.strip()
    if not blob.startswith("{"):
        return claims
    try:
        data = json.loads(blob)
    except (json.JSONDecodeError, TypeError):
        for mk in _JSON_STRING_KEYS.finditer(blob):
            tok = mk.group(1)
            if _field_candidate(tok):
                claims.append(
                    DocClaim(
                        kind="json_field",
                        claim=tok,
                        source=display_rel,
                        line=approx_line,
                        detail=f"fenced JSON snippet key `{tok}`",
                    )
                )
        return claims

    def walk(obj: Any, depth: int = 0) -> None:
        if depth > 12:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str) and _field_candidate(k):
                    claims.append(
                        DocClaim(
                            kind="json_field",
                            claim=k,
                            source=display_rel,
                            line=approx_line,
                            detail=f"fenced JSON property `{k}`",
                        )
                    )
                walk(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj[:50]:
                walk(item, depth + 1)

    walk(data)
    return claims
