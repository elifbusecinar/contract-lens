"""Comparator attaches scanner source/line to mismatches for PR inline comments."""

from __future__ import annotations

from contractlens.contracts.comparator import compare_contracts
from contractlens.contracts.models import ApiContract


def test_compare_contracts_inline_anchor_from_frontend_row() -> None:
    fe = ApiContract(
        method="POST",
        path="/api/projects/{id}/files",
        source="frontend/projectApi.ts",
        line=12,
        request_fields=["file"],
        response_fields=["id", "thumbnailUrl"],
    )
    be = ApiContract(
        method="POST",
        path="/api/projects/{projectId}/models",
        source="backend/X.cs",
        line=1,
        request_dto="IFormFile",
        response_dto="new { projectId thumbnail_path }",
        auth="Authorize",
    )
    mismatches, _ = compare_contracts([fe], [be])
    path_m = next(m for m in mismatches if m.area == "path")
    assert path_m.comment_path == "frontend/projectApi.ts"
    assert path_m.comment_line == 12
