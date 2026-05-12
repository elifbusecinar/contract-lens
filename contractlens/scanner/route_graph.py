"""Lightweight route-prefix grouping for dashboards/reports (not a full AST/router graph)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def route_prefix_summary_markdown(
    backend_findings: list[dict[str, Any]],
    frontend_findings: list[dict[str, Any]],
    *,
    depth: int = 3,
) -> str:
    """
    Build a shallow prefix map (first N path segments) to show backend surface area vs frontend calls.
    This complements regex scanners — it is **not** framework-aware routing decompilation.
    """
    depth = max(1, min(int(depth), 8))

    def prefixes(paths: list[str]) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for raw in paths:
            p = str(raw or "").strip()
            if not p.startswith("/"):
                p = "/" + p
            parts = [x for x in p.strip("/").split("/") if x]
            if not parts:
                counts["/"] += 1
                continue
            pref = ""
            for i in range(min(depth, len(parts))):
                pref += "/" + parts[i]
                counts[pref] += 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    be_paths = [str(x.get("path", "")) for x in backend_findings if isinstance(x, dict)]
    fe_paths = [str(x.get("path", "")) for x in frontend_findings if isinstance(x, dict)]

    be_pf = prefixes(be_paths)
    fe_pf = prefixes(fe_paths)

    lines = [
        f"Heuristic **prefix histogram** (depth **{depth}** segments). Useful for spotting missing `/api` clusters; "
        "it does **not** execute framework routers or resolve lazy-loaded modules.",
        "",
        "### Backend prefixes",
        "",
    ]
    if be_pf:
        for k, v in list(be_pf.items())[:40]:
            lines.append(f"- `{k}` — **{v}** hit(s) across routes")
        if len(be_pf) > 40:
            lines.append(f"- _…and **{len(be_pf) - 40}** more prefix buckets._")
    else:
        lines.append("_No backend paths._")

    lines.extend(["", "### Frontend prefixes", ""])
    if fe_pf:
        for k, v in list(fe_pf.items())[:40]:
            lines.append(f"- `{k}` — **{v}** hit(s) across calls")
        if len(fe_pf) > 40:
            lines.append(f"- _…and **{len(fe_pf) - 40}** more prefix buckets._")
    else:
        lines.append("_No frontend paths._")

    lines.extend(
        [
            "",
            "### Interpretation",
            "",
            "- Large frontend buckets with **no** overlapping backend bucket often indicate path drift or missing scanners "
            "for alternate HTTP clients.\n"
            "- Template tokens such as `{id}` are normalized from `${id}` in TS template literals when matched.",
        ]
    )
    return "\n".join(lines)
