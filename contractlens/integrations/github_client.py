"""Minimal GitHub REST client (stdlib only): issues, timeline comments, and PR reviews."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

GITHUB_API = "https://api.github.com"


class GitHubApiError(Exception):
    """Raised when the GitHub API returns an error or an unexpected payload."""

    def __init__(self, message: str, *, status: int | None = None, body: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def parse_repository(repo: str | None, *, env: dict[str, str] | None = None) -> tuple[str, str]:
    """
    Resolve owner/repo from explicit ``owner/name``, ``GITHUB_REPOSITORY``,
    or ``GITHUB_REPOSITORY_OWNER`` + repository name heuristics are **not** used — caller must pass repo string or env.
    """
    env = env if env is not None else dict(os.environ)
    candidate = (repo or "").strip()
    if not candidate:
        candidate = env.get("GITHUB_REPOSITORY", "").strip()
    if not candidate:
        raise GitHubApiError("Missing GitHub repository (use --github-repo owner/name or set GITHUB_REPOSITORY).")
    if not _REPO_RE.match(candidate):
        raise GitHubApiError(f"Invalid GitHub repository slug: {candidate!r} (expected owner/name).")
    owner, _, name = candidate.partition("/")
    return owner, name


def resolve_token(token_env: str | None = None, *, env: dict[str, str] | None = None) -> str:
    env = env if env is not None else dict(os.environ)
    var = (token_env or "GITHUB_TOKEN").strip() or "GITHUB_TOKEN"
    tok = env.get(var, "").strip()
    if tok:
        return tok
    if var != "GITHUB_TOKEN":
        tok = env.get("GITHUB_TOKEN", "").strip()
        if tok:
            return tok
    tok = env.get("GH_TOKEN", "").strip()
    if tok:
        return tok
    raise GitHubApiError(
        f"No GitHub token found (set {var}, GITHUB_TOKEN, or GH_TOKEN). "
        "Fine-grained PAT needs appropriate scopes: Issues (create_issue / timeline comments), "
        "Pull requests (PR reviews & comments)."
    )


def _request(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    *,
    preview_schema: str | None = None,
) -> Any:
    url = f"{GITHUB_API}{path}"
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "ContractLens-GitHub-Client/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    if preview_schema:
        headers["Accept"] = str(preview_schema)
    m = method.upper()
    req = urllib.request.Request(url, data=payload, method=m, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 — intentional GitHub HTTPS
            raw = resp.read().decode("utf-8", errors="replace")
            if not raw.strip():
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise GitHubApiError(
            f"GitHub HTTP {e.code}: {e.reason}",
            status=e.code,
            body=err_body[:4000],
        ) from e


@dataclass(frozen=True)
class CreatedIssue:
    number: int
    html_url: str


def create_issue(owner: str, repo: str, title: str, body: str, token: str, *, labels: list[str] | None = None) -> CreatedIssue:
    path = f"/repos/{owner}/{repo}/issues"
    payload: dict[str, Any] = {"title": title[:256], "body": body}
    if labels:
        payload["labels"] = labels[:20]
    data = _request("POST", path, token, payload)
    if not isinstance(data, dict):
        raise GitHubApiError("Unexpected GitHub response when creating issue.")
    num = data.get("number")
    url = data.get("html_url")
    if not isinstance(num, int) or not isinstance(url, str):
        raise GitHubApiError(f"Malformed issue payload: {data!r}")
    return CreatedIssue(number=num, html_url=url)


def create_issue_comment(owner: str, repo: str, issue_number: int, body: str, token: str) -> str:
    """Post a timeline comment on an issue or pull request (PR numbers share the issues namespace)."""
    if issue_number < 1:
        raise GitHubApiError("issue_number must be positive.")
    path = f"/repos/{owner}/{repo}/issues/{issue_number}/comments"
    data = _request("POST", path, token, {"body": body})
    if not isinstance(data, dict):
        raise GitHubApiError("Unexpected GitHub response when creating comment.")
    url = data.get("html_url")
    if not isinstance(url, str):
        raise GitHubApiError(f"Malformed comment payload: {data!r}")
    return url


def get_pull_request_head_sha(owner: str, repo: str, pull_number: int, token: str) -> str:
    if pull_number < 1:
        raise GitHubApiError("pull_number must be positive.")
    data = _request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}", token, None)
    if not isinstance(data, dict):
        raise GitHubApiError("Unexpected GitHub response when loading pull request.")
    head = data.get("head")
    if not isinstance(head, dict):
        raise GitHubApiError("Pull response missing head.")
    sha = head.get("sha")
    if not isinstance(sha, str) or len(sha) < 7:
        raise GitHubApiError("Pull response missing head.sha.")
    return sha


def normalize_repo_relative_path(path: str) -> str:
    """Strip slashes and reject ``..`` for GitHub ``path`` fields."""
    p = path.strip().replace("\\", "/")
    parts = [s for s in p.split("/") if s and s != "."]
    if any(s == ".." for s in parts):
        raise GitHubApiError("Path must be repo-relative without '..' segments.")
    return "/".join(parts)


def create_pull_request_inline_comment(
    owner: str,
    repo: str,
    pull_number: int,
    *,
    body: str,
    path: str,
    line: int,
    token: str,
    commit_id: str | None = None,
    side: str = "RIGHT",
) -> str:
    """
    POST ``/repos/.../pulls/{pull_number}/comments`` — a **line-specific** review comment on the PR diff.

    Requires ``path`` (repo-relative file), ``line`` (1-based position on the merge diff), and ``commit_id``
    (defaults to the PR head SHA).
    """
    if pull_number < 1:
        raise GitHubApiError("pull_number must be positive.")
    if line < 1:
        raise GitHubApiError("line must be >= 1 for inline PR comments.")
    rel = normalize_repo_relative_path(path)
    cid = commit_id or get_pull_request_head_sha(owner, repo, pull_number, token)
    side_up = side.upper()
    if side_up not in {"LEFT", "RIGHT"}:
        raise GitHubApiError("side must be LEFT or RIGHT.")
    payload: dict[str, Any] = {
        "body": body[:65536],
        "commit_id": cid,
        "path": rel,
        "line": line,
        "side": side_up,
    }
    data = _request("POST", f"/repos/{owner}/{repo}/pulls/{pull_number}/comments", token, payload)
    if not isinstance(data, dict):
        raise GitHubApiError("Unexpected GitHub response when creating pull request review comment.")
    url = data.get("html_url")
    if not isinstance(url, str):
        raise GitHubApiError(f"Malformed pull request comment payload: {data!r}")
    return url


def create_pull_request_review(owner: str, repo: str, pull_number: int, body: str, token: str) -> str:
    """
    Submit a **pull request review** with ``event: COMMENT`` (summary comment on the PR diff/review UI).

    This is **not** a line-specific review comment; those require ``pulls/comments`` with path + line metadata.
    """
    commit_id = get_pull_request_head_sha(owner, repo, pull_number, token)
    payload: dict[str, Any] = {"commit_id": commit_id, "body": body, "event": "COMMENT"}
    data = _request("POST", f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews", token, payload)
    if not isinstance(data, dict):
        raise GitHubApiError("Unexpected GitHub response when creating pull request review.")
    url = data.get("html_url")
    if not isinstance(url, str):
        raise GitHubApiError(f"Malformed pull request review payload: {data!r}")
    return url
