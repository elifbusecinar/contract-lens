"""Optional HTTP GET probe for runtime reachability (config / env); JSON-serializable result."""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from typing import Any


def run_runtime_http_probe(url: str, *, timeout: float = 4.0) -> dict[str, Any]:
    """Perform a single GET; records status when HTTP responds (including error codes)."""
    cleaned = (url or "").strip()
    if not cleaned:
        return {"configured": False}

    t0 = time.perf_counter()
    req = urllib.request.Request(
        cleaned,
        method="GET",
        headers={"User-Agent": "ContractLens-runtime-probe/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            code = resp.getcode()
            return {
                "configured": True,
                "url": cleaned,
                "ok": True,
                "status_code": code,
                "error": None,
                "elapsed_ms": elapsed_ms,
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "configured": True,
            "url": cleaned,
            "ok": False,
            "status_code": e.code,
            "error": str(e.reason),
            "elapsed_ms": elapsed_ms,
        }
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "configured": True,
            "url": cleaned,
            "ok": False,
            "status_code": None,
            "error": str(e),
            "elapsed_ms": elapsed_ms,
        }
