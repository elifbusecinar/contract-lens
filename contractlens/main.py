"""CLI entrypoint for ContractLens AI."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from contractlens.agents import crew as crew_mod
from contractlens.ci.gate import evaluate_ci_gate, format_ci_summary_lines
from contractlens.config import PACKAGE_ROOT, SAMPLE_FEATURE, default_report_path, display_path_under_repo
from contractlens.integrations.github_client import (
    GitHubApiError,
    create_issue,
    create_issue_comment,
    create_pull_request_inline_comment,
    create_pull_request_review,
    get_pull_request_head_sha,
    parse_repository,
    resolve_token,
)
from contractlens.mcp_server.permissions import reset_extra_ignore_dir_names, set_extra_ignore_dir_names
from contractlens.openapi.parser import set_max_schema_ref_chain
from contractlens.reporting.issue_draft import github_issue_title_and_body, write_github_issue_draft
from contractlens.user_config import contractlens_config_search_roots, load_user_contractlens_config
from contractlens.workflow.graph import run_workflow
from contractlens.workflow.state import new_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ContractLens AI — contract drift audit")
    parser.add_argument("--feature", default=SAMPLE_FEATURE, help="Feature label for the audit context")
    parser.add_argument(
        "--root",
        default=str(PACKAGE_ROOT / "examples" / "sample_project"),
        help="Repository root to analyze",
    )
    parser.add_argument(
        "--report-dir",
        default=str(PACKAGE_ROOT / "contractlens-reports"),
        help="Directory for Markdown reports",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose demo logs")
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also write a standalone HTML report next to the Markdown file",
    )
    parser.add_argument("--mode", default="default", choices=("default", "demo"), help="Demo mode flag")
    parser.add_argument(
        "--deterministic-agents",
        action="store_true",
        help="Disable LLM CrewAI even if OPENAI_API_KEY is set (deterministic specialist steps only)",
    )
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Restrict scanners (and optional OpenAPI load) to files reported changed by local Git under --root",
    )
    parser.add_argument(
        "--fallback-full-scan",
        action="store_true",
        help="When --changed-only finds no eligible changed files under root, fall back to the full discovered file list",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="After the audit, exit with code 1 if any mismatch meets or exceeds --fail-on severity (report still written)",
    )
    parser.add_argument(
        "--fail-on",
        dest="fail_on",
        default="High",
        choices=("High", "Medium", "Low"),
        help="With --ci: fail the process when a mismatch is at this severity or stricter (default: High)",
    )
    parser.add_argument(
        "--issue-draft",
        metavar="PATH",
        default=None,
        help="After a successful audit, write a GitHub issue draft Markdown file (no API calls)",
    )
    parser.add_argument(
        "--github-repo",
        metavar="OWNER/REPO",
        default=None,
        help="Target repository for GitHub REST actions (fallback: GITHUB_REPOSITORY env)",
    )
    parser.add_argument(
        "--github-token-env",
        default="GITHUB_TOKEN",
        metavar="VAR",
        help="Environment variable holding a PAT / GitHub Actions token (default: GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--github-create-issue",
        action="store_true",
        help="After a successful audit, open a GitHub Issue using the REST API (requires token + repo)",
    )
    parser.add_argument(
        "--github-issue-comment",
        metavar="N",
        type=int,
        default=None,
        help="After a successful audit, post a Markdown comment on issue or PR number N (REST API)",
    )
    parser.add_argument(
        "--github-pr-review",
        metavar="N",
        type=int,
        default=None,
        help="After a successful audit, post a PR review (event=COMMENT) on pull request N — summary on the review UI, not a line-specific comment",
    )
    parser.add_argument(
        "--github-pr-inline-comments",
        metavar="N",
        type=int,
        default=None,
        help="After a successful audit, post line-specific review comments on PR N for mismatches that include comment_path + comment_line (see --github-inline-max)",
    )
    parser.add_argument(
        "--github-inline-max",
        type=int,
        default=5,
        metavar="K",
        help="Cap inline PR comments when using --github-pr-inline-comments (default: 5; use 0 to skip posting)",
    )
    parser.add_argument(
        "--scan-cache",
        action="store_true",
        help="Write per-file scanner cache under <root>/.contractlens/scan-cache/",
    )
    parser.add_argument(
        "--no-scan-cache",
        action="store_true",
        help="Disable scan cache even if repo config enables it",
    )

    args = parser.parse_args(argv)

    crew_mod.reset_fallback_banner()

    root_path_obj = Path(args.root).resolve()
    if not root_path_obj.exists():
        print(f"[Error] Root path does not exist: {root_path_obj}", file=sys.stderr)
        return 1
    if not root_path_obj.is_dir():
        print(f"[Error] Root path is not a directory: {root_path_obj}", file=sys.stderr)
        return 1

    root_path = str(root_path_obj)

    reset_extra_ignore_dir_names()
    set_max_schema_ref_chain(None)
    user_cfg = load_user_contractlens_config(contractlens_config_search_roots(root_path_obj))
    set_extra_ignore_dir_names(user_cfg.extra_ignore_dirs)
    set_max_schema_ref_chain(user_cfg.openapi_max_ref_chain)
    probe_url = (user_cfg.probe_base_url or os.getenv("CONTRACTLENS_PROBE_BASE_URL", "")).strip()

    report_dir = Path(args.report_dir).resolve()
    try:
        report_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[Error] Cannot create report directory {report_dir}: {exc}", file=sys.stderr)
        return 1

    initial = new_state(
        args.feature,
        root_path,
        verbose=args.verbose,
        mode=args.mode,
    )
    initial["report_output_dir"] = str(report_dir)
    initial["report_path"] = str(default_report_path(args.feature, report_dir))
    initial["use_llm_agents"] = (not args.deterministic_agents) and bool(
        os.getenv("OPENAI_API_KEY", "").strip()
    )
    initial.setdefault("mcp_allow_write", True)
    initial["changed_only"] = bool(args.changed_only)
    initial["fallback_full_scan"] = bool(args.fallback_full_scan)
    initial["generate_html"] = bool(args.html or user_cfg.emit_html_by_default)
    initial["runtime_probe_base_url"] = probe_url

    scan_enabled = bool(user_cfg.scan_cache)
    if args.no_scan_cache:
        scan_enabled = False
    elif args.scan_cache:
        scan_enabled = True

    env_sc = os.getenv("CONTRACTLENS_SCAN_CACHE", "").strip().lower()
    if env_sc in ("1", "true", "yes", "on"):
        scan_enabled = True
    elif env_sc in ("0", "false", "no", "off"):
        scan_enabled = False

    initial["scan_cache_enabled"] = scan_enabled

    try:
        out = run_workflow(initial)
    except Exception as exc:
        print(f"[Error] Workflow failed: {exc}", file=sys.stderr)
        return 1

    final_path = Path(out.get("report_path") or initial["report_path"])
    rel_display = display_path_under_repo(final_path)
    print(f"[Report] Markdown report generated: {rel_display}")
    html_rp = (out.get("html_report_path") or "").strip()
    if html_rp:
        print(f"[Report] HTML report generated: {display_path_under_repo(html_rp)}")

    errs = out.get("errors") or []
    ci_exit = 0
    if args.ci:
        gate = evaluate_ci_gate(out.get("mismatches") or [], fail_on=args.fail_on)
        for line in format_ci_summary_lines(gate):
            print(line)
        ci_exit = int(gate.get("exit_code") or 0)

    if errs:
        print("[Warn] Errors encountered:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if args.issue_draft:
        draft_path = Path(args.issue_draft).resolve()
        write_github_issue_draft(draft_path, args.feature, out.get("mismatches") or [])
        print(f"[Report] GitHub issue draft written: {display_path_under_repo(draft_path)}")

    def _inline_pr_comment_body(mismatch_row: dict) -> str:
        area = str(mismatch_row.get("area") or "")
        risk = str(mismatch_row.get("risk") or "")
        fe = str(mismatch_row.get("frontend_expects") or "")
        be = str(mismatch_row.get("backend_provides") or "")
        sug = str(mismatch_row.get("suggestion") or "")
        return (
            f"**ContractLens** ({risk}) `{area}`\n\n"
            f"- Expects: `{fe}`\n"
            f"- Backend: `{be}`\n\n"
            f"{sug}"
        )[:65536]

    gh_fail = 0
    gh_any = (
        args.github_create_issue
        or args.github_issue_comment is not None
        or args.github_pr_review is not None
        or args.github_pr_inline_comments is not None
    )
    if gh_any:
        try:
            owner, repo_name = parse_repository(args.github_repo)
            token = resolve_token(args.github_token_env)
            title, body_md = github_issue_title_and_body(args.feature, out.get("mismatches") or [])
            if args.github_create_issue:
                created = create_issue(owner, repo_name, title, body_md, token)
                print(f"[GitHub] Issue #{created.number}: {created.html_url}")
            if args.github_issue_comment is not None:
                c_url = create_issue_comment(owner, repo_name, args.github_issue_comment, body_md, token)
                print(f"[GitHub] Comment posted: {c_url}")
            if args.github_pr_review is not None:
                r_url = create_pull_request_review(owner, repo_name, args.github_pr_review, body_md, token)
                print(f"[GitHub] PR review posted: {r_url}")
            if args.github_pr_inline_comments is not None:
                pr_n = args.github_pr_inline_comments
                max_inline = int(args.github_inline_max)
                if max_inline <= 0:
                    print("[GitHub] Inline PR comments skipped (--github-inline-max <= 0).")
                else:
                    head_sha = get_pull_request_head_sha(owner, repo_name, pr_n, token)
                    seen_keys: set[tuple[str, int]] = set()
                    posted = 0
                    for row in out.get("mismatches") or []:
                        if posted >= max_inline:
                            break
                        if not isinstance(row, dict):
                            continue
                        rel_path = row.get("comment_path")
                        line_no = row.get("comment_line")
                        if not rel_path or not isinstance(line_no, int) or line_no < 1:
                            continue
                        key = (str(rel_path), int(line_no))
                        if key in seen_keys:
                            continue
                        seen_keys.add(key)
                        body_one = _inline_pr_comment_body(row)
                        try:
                            url = create_pull_request_inline_comment(
                                owner,
                                repo_name,
                                pr_n,
                                body=body_one,
                                path=str(rel_path),
                                line=int(line_no),
                                token=token,
                                commit_id=head_sha,
                            )
                            print(f"[GitHub] Inline PR comment ({rel_path}:{line_no}): {url}")
                            posted += 1
                        except GitHubApiError as exc:
                            print(
                                f"[GitHub] Inline comment failed for {rel_path}:{line_no}: {exc}",
                                file=sys.stderr,
                            )
                            if getattr(exc, "body", None):
                                print(str(exc.body)[:800], file=sys.stderr)
        except GitHubApiError as exc:
            print(f"[GitHub] Error: {exc}", file=sys.stderr)
            if getattr(exc, "body", None):
                print(str(exc.body)[:1200], file=sys.stderr)
            gh_fail = 1

    exit_code = ci_exit if args.ci else 0
    exit_code = max(exit_code, gh_fail)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
