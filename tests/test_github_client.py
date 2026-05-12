"""Unit tests for GitHub REST helpers (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from contractlens.integrations.github_client import (
    GitHubApiError,
    create_issue,
    create_issue_comment,
    create_pull_request_inline_comment,
    create_pull_request_review,
    normalize_repo_relative_path,
    parse_repository,
    resolve_token,
)


def test_parse_repository_explicit() -> None:
    o, r = parse_repository("octocat/hello", env={})
    assert o == "octocat" and r == "hello"


def test_parse_repository_from_env() -> None:
    o, r = parse_repository(None, env={"GITHUB_REPOSITORY": "myorg/tool"})
    assert o == "myorg" and r == "tool"


def test_resolve_token_priority() -> None:
    assert resolve_token("CUSTOM", env={"CUSTOM": "tok", "GITHUB_TOKEN": "x"}) == "tok"
    assert resolve_token("MISSING", env={"GITHUB_TOKEN": "ab", "GH_TOKEN": ""}) == "ab"


def test_resolve_token_missing_raises() -> None:
    with pytest.raises(GitHubApiError):
        resolve_token("NONE", env={})


class _FakeResp:
    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._raw


def test_create_issue_success() -> None:
    payload = {"number": 42, "html_url": "https://github.com/o/r/issues/42"}
    with patch("contractlens.integrations.github_client.urllib.request.urlopen") as op:
        op.return_value = _FakeResp(payload)
        out = create_issue("o", "r", "t", "b", "tok")
        assert out.number == 42
        assert "issues/42" in out.html_url


def test_create_issue_http_wraps_git_hub_api_error() -> None:
    with patch(
        "contractlens.integrations.github_client._request",
        side_effect=GitHubApiError("fail", status=403),
    ):
        with pytest.raises(GitHubApiError) as ei:
            create_issue("o", "r", "t", "b", "tok")
        assert ei.value.status == 403


def test_create_issue_comment_returns_url() -> None:
    payload = {"html_url": "https://github.com/o/r/issues/1#issuecomment-2"}
    with patch("contractlens.integrations.github_client.urllib.request.urlopen") as op:
        op.return_value = _FakeResp(payload)
        url = create_issue_comment("o", "r", 1, "hello", "tok")
        assert "issuecomment" in url


def test_create_pull_request_review_uses_head_sha() -> None:
    with patch("contractlens.integrations.github_client._request") as rq:
        rq.side_effect = [
            {"head": {"sha": "deadbeef"}},
            {"html_url": "https://github.com/o/r/pull/7/reviews/99"},
        ]
        url = create_pull_request_review("o", "r", 7, "audit body", "tok")
        assert url.endswith("/reviews/99")
        assert rq.call_count == 2
        assert rq.call_args_list[0][0][0] == "GET"
        assert rq.call_args_list[1][0][0] == "POST"
        assert "/pulls/7/reviews" in rq.call_args_list[1][0][1]


def test_normalize_repo_relative_path() -> None:
    assert normalize_repo_relative_path("a/b/c.ts") == "a/b/c.ts"
    assert normalize_repo_relative_path("\\x\\y\\z.ts") == "x/y/z.ts"
    assert normalize_repo_relative_path("/leading/slash") == "leading/slash"
    with pytest.raises(GitHubApiError):
        normalize_repo_relative_path("a/../b")


def test_create_pull_request_inline_comment_single_request_when_commit_given() -> None:
    with patch("contractlens.integrations.github_client._request") as rq:
        rq.return_value = {"html_url": "https://github.com/o/r/pull/3#discussion_r42"}
        url = create_pull_request_inline_comment(
            "o", "r", 3, body="note", path="./src/A.tsx", line=4, token="tok", commit_id="abc123def"
        )
        assert "pull/3" in url
        assert rq.call_count == 1
        call = rq.call_args_list[0]
        assert call[0][0] == "POST"
        assert "/pulls/3/comments" in call[0][1]
        payload = call[0][3]
        assert payload["commit_id"] == "abc123def"
        assert payload["path"] == "src/A.tsx"
        assert payload["line"] == 4
        assert payload["side"] == "RIGHT"
