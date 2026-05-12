"""GitHub issue draft text from mismatch rows (no GitHub API calls)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_github_issue_api_body(feature_name: str, mismatches: list[dict[str, Any]]) -> str:
    """Plain Markdown body suitable for ``POST /repos/.../issues`` or issue comments."""
    rows = [m for m in mismatches if isinstance(m, dict)]
    bullets = []
    for d in rows[:40]:
        risk = d.get("risk", "")
        area = d.get("area", "")
        sug = d.get("suggestion", "")
        bullets.append(f"- **[{risk}] `{area}`**: {sug}")
    body_list = "\n".join(bullets) if bullets else "_No mismatches recorded._"
    return (
        "### ContractLens audit\n\n"
        f"**Feature:** `{feature_name}`\n\n"
        "### Findings\n\n"
        f"{body_list}\n\n"
        "### Next steps\n\n"
        "- Align paths/DTOs or document intentional differences.\n"
        "- Re-run `python -m contractlens.main --feature \"...\" --root <repo> --verbose`\n"
    )


def github_issue_title_and_body(feature_name: str, mismatches: list[dict[str, Any]]) -> tuple[str, str]:
    title = f"Contract drift audit: {feature_name}"
    return title, build_github_issue_api_body(feature_name, mismatches)


def build_github_issue_draft_markdown(feature_name: str, mismatches: list[dict[str, Any]]) -> str:
    title = f"Contract drift audit: {feature_name}"
    rows = [m for m in mismatches if isinstance(m, dict)]
    bullets = []
    for d in rows[:30]:
        risk = d.get("risk", "")
        area = d.get("area", "")
        sug = d.get("suggestion", "")
        bullets.append(f"- **[{risk}] `{area}`**: {sug}")
    body_list = "\n".join(bullets) if bullets else "_No mismatches recorded._"
    return (
        f"## GitHub issue draft\n\n"
        f"**Suggested title:** `{title}`\n\n"
        "### Summary\n\n"
        f"This draft was generated locally by ContractLens AI for feature `{feature_name}`.\n\n"
        "### Findings\n\n"
        f"{body_list}\n\n"
        "### Next steps\n\n"
        "- Align paths/DTOs or document intentional differences.\n"
        "- Re-run `python -m contractlens.main --feature \"...\" --root <repo> --verbose`\n"
    )


def write_github_issue_draft(path: Path, feature_name: str, mismatches: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_github_issue_draft_markdown(feature_name, mismatches), encoding="utf-8")
