"""Route prefix summary regression."""

from __future__ import annotations

from contractlens.scanner.route_graph import route_prefix_summary_markdown


def test_route_prefix_contains_clusters() -> None:
    fe = [{"path": "/api/projects/{id}/files"}]
    be = [{"path": "/api/projects/{projectId}/models"}]
    md = route_prefix_summary_markdown(be, fe)
    assert "/api" in md
    assert "Frontend prefixes" in md
