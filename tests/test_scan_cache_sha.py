"""Scan cache content hashing."""

from __future__ import annotations

from contractlens.contracts.models import ApiContract
from contractlens.scanner.scan_cache import load_cached_contracts, save_cached_contracts


def test_scan_cache_invalidates_when_content_changes(tmp_path) -> None:
    root = tmp_path
    rel = "src/x.ts"
    fp = root / rel
    fp.parent.mkdir(parents=True)
    fp.write_text("// v1\n", encoding="utf-8")

    contracts = [
        ApiContract(method="GET", path="/a", source=rel, line=1),
    ]
    save_cached_contracts(root, rel, "frontend", contracts)
    loaded = load_cached_contracts(root, rel, "frontend")
    assert loaded is not None and len(loaded) == 1

    fp.write_text("// v2\n", encoding="utf-8")
    assert load_cached_contracts(root, rel, "frontend") is None


def test_legacy_cache_without_sha256_still_loads_if_fingerprint_matches(tmp_path) -> None:
    import json

    root = tmp_path
    rel = "legacy.ts"
    fp = root / rel
    fp.write_text("stable\n", encoding="utf-8")

    from contractlens.scanner.scan_cache import _entry_path, _fp_for_file

    fg = _fp_for_file(fp)
    assert fg is not None
    cp = _entry_path(root, rel, "frontend")
    cp.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "kind": "frontend",
        "rel": rel,
        "fingerprint": fg,
        "contracts": [ApiContract(method="GET", path="/z", source=rel, line=1).model_dump()],
    }
    cp.write_text(json.dumps(payload), encoding="utf-8")

    hit = load_cached_contracts(root, rel, "frontend")
    assert hit is not None and hit[0].path == "/z"
