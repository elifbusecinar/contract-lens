"""Per-file scan cache under ``<repo>/.contractlens/scan-cache/v1``.

Uses ``mtime_ns`` + ``size`` for quick checks and **SHA-256 of raw file bytes** so identical
mtimes across copies still invalidate when content differs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from contractlens.contracts.models import ApiContract


def _norm_rel(rel: str) -> str:
    return rel.replace("\\", "/")


def _fp_for_file(fp: Path) -> dict[str, int] | None:
    try:
        st = fp.stat()
        mtime_ns = getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000))
        return {"mtime_ns": int(mtime_ns), "size": int(st.st_size)}
    except OSError:
        return None


def _sha256_file(fp: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with fp.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _entry_path(base: Path, rel: str, kind: str) -> Path:
    digest = hashlib.sha256(f"{kind}:{_norm_rel(rel)}".encode("utf-8")).hexdigest()[:32]
    return base / ".contractlens" / "scan-cache" / "v1" / f"{digest}.json"


def load_cached_contracts(base: Path, rel: str, kind: str) -> list[ApiContract] | None:
    source = base / rel
    if not source.is_file():
        return None
    fg = _fp_for_file(source)
    if fg is None:
        return None
    sha = _sha256_file(source)
    if sha is None:
        return None
    cp = _entry_path(base, rel, kind)
    if not cp.is_file():
        return None
    try:
        raw = json.loads(cp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(raw, dict):
        return None
    if raw.get("fingerprint") != fg:
        return None
    cached_sha = raw.get("content_sha256")
    if isinstance(cached_sha, str) and cached_sha:
        if cached_sha != sha:
            return None
    items = raw.get("contracts")
    if not isinstance(items, list):
        return None
    out: list[ApiContract] = []
    for item in items:
        if isinstance(item, dict):
            try:
                out.append(ApiContract.model_validate(item))
            except Exception:
                return None
    return out


def save_cached_contracts(base: Path, rel: str, kind: str, contracts: list[ApiContract]) -> None:
    source = base / rel
    fg = _fp_for_file(source)
    sha = _sha256_file(source)
    if fg is None or sha is None:
        return
    cp = _entry_path(base, rel, kind)
    cp.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "kind": kind,
        "rel": _norm_rel(rel),
        "fingerprint": fg,
        "content_sha256": sha,
        "contracts": [c.model_dump() for c in contracts],
    }
    tmp = cp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(cp)
