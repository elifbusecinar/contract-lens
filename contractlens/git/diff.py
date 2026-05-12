"""Local Git diff helpers — discover changed paths without GitHub or network calls."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from contractlens.mcp_server.permissions import path_under_root_has_ignored_dir


def git_toplevel(start: Path) -> Path | None:
    """Return absolute Git worktree root for ``start``, or ``None`` if not inside a repo."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(start.resolve()), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    line = (proc.stdout or "").strip().splitlines()
    if not line:
        return None
    return Path(line[0]).resolve()


def _git_name_only(git_root: Path, *args: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(git_root), *args],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        return []
    except subprocess.TimeoutExpired:
        return []
    if proc.returncode != 0:
        return []
    out: list[str] = []
    for raw in (proc.stdout or "").splitlines():
        s = raw.strip().replace("\\", "/")
        if s:
            out.append(s)
    return out


def changed_paths_relative_to_git_root(git_root: Path, *, include_cached: bool) -> list[str]:
    """Union of unstaged and (optionally) staged changed paths, POSIX relative to ``git_root``."""
    names: set[str] = set()
    for p in _git_name_only(git_root, "diff", "--name-only"):
        names.add(p)
    if include_cached:
        for p in _git_name_only(git_root, "diff", "--cached", "--name-only"):
            names.add(p)
    return sorted(names)


def paths_under_analysis_root(
    git_root: Path,
    analysis_root: Path,
    paths_rel_git: list[str],
) -> list[str]:
    """Keep existing files under ``analysis_root`` as paths relative to ``analysis_root``."""
    analysis_root = analysis_root.resolve()
    git_root = git_root.resolve()
    try:
        analysis_root.relative_to(git_root)
    except ValueError:
        # analysis_root outside git root — nothing to map
        return []

    out: list[str] = []
    seen: set[str] = set()
    for rel_g in paths_rel_git:
        candidate = (git_root / rel_g).resolve()
        if not candidate.is_file():
            continue
        try:
            rel_a = candidate.relative_to(analysis_root)
        except ValueError:
            continue
        if path_under_root_has_ignored_dir(rel_a):
            continue
        key = rel_a.as_posix()
        if key not in seen:
            seen.add(key)
            out.append(key)
    out.sort()
    return out


def get_changed_files_relative_to_root(root: str | Path, *, include_cached: bool = True) -> tuple[list[str], list[str], bool]:
    """
    Return ``(files_relative_to_root, notes, is_git_repository)``.

    ``files_relative_to_root`` lists changed tracked/untracked file paths that exist on disk under ``root``,
    relative to ``root``, suitable for scanner inputs.
    """
    analysis = Path(root).resolve()
    notes: list[str] = []
    top = git_toplevel(analysis)
    if top is None:
        notes.append("Not a Git repository (or `git` is unavailable); cannot list changed files.")
        return [], notes, False

    raw = changed_paths_relative_to_git_root(top, include_cached=include_cached)
    under = paths_under_analysis_root(top, analysis, raw)
    notes.append(f"Git worktree: `{top}`; raw changed path(s) from Git: {len(raw)}.")
    return under, notes, True


@dataclass(frozen=True)
class ChangedOnlyScanDecision:
    """Outcome of applying ``--changed-only`` to the discovered project file list."""

    files_for_scanners: list[str]
    openapi_limit_to_scan_files: bool
    git_changed_only_requested: bool
    git_is_repository: bool
    git_graceful_full_scan_not_git: bool
    git_fallback_full_scan_used: bool
    git_changed_files_count: int
    notes: tuple[str, ...]


def resolve_changed_only_scan_files(
    analysis_root: Path,
    full_relative_paths: list[str],
    *,
    changed_only: bool,
    fallback_full_scan: bool,
    include_cached: bool,
    verbose: bool,
) -> ChangedOnlyScanDecision:
    """
    Optionally narrow ``full_relative_paths`` to Git-changed files under ``analysis_root``.
    """
    analysis_root = analysis_root.resolve()
    full_set = frozenset(full_relative_paths)

    if not changed_only:
        return ChangedOnlyScanDecision(
            files_for_scanners=list(full_relative_paths),
            openapi_limit_to_scan_files=False,
            git_changed_only_requested=False,
            git_is_repository=False,
            git_graceful_full_scan_not_git=False,
            git_fallback_full_scan_used=False,
            git_changed_files_count=0,
            notes=(),
        )

    changed_under_root, notes_list, is_git = get_changed_files_relative_to_root(
        analysis_root,
        include_cached=include_cached,
    )
    notes = list(notes_list)

    if not is_git:
        notes.append(
            "changed-only mode ignored: analyzing full discovered file list (not a Git repository or git failed)."
        )
        if verbose:
            print("[Git] changed-only requested but root is not in a Git worktree - using full scan.")
        return ChangedOnlyScanDecision(
            files_for_scanners=list(full_relative_paths),
            openapi_limit_to_scan_files=False,
            git_changed_only_requested=True,
            git_is_repository=False,
            git_graceful_full_scan_not_git=True,
            git_fallback_full_scan_used=False,
            git_changed_files_count=0,
            notes=tuple(notes),
        )

    intersect = sorted(full_set & frozenset(changed_under_root))

    if not intersect:
        msg = (
            "No changed files under this root match the project scan (or index is clean). "
            "Scanners will receive an empty file list."
        )
        notes.append(msg)
        if verbose:
            print(f"[Git] {msg}")
        if fallback_full_scan:
            notes.append("fallback-full-scan: using full discovered file list instead.")
            if verbose:
                print("[Git] --fallback-full-scan: reverting to full file list.")
            return ChangedOnlyScanDecision(
                files_for_scanners=list(full_relative_paths),
                openapi_limit_to_scan_files=False,
                git_changed_only_requested=True,
                git_is_repository=True,
                git_graceful_full_scan_not_git=False,
                git_fallback_full_scan_used=True,
                git_changed_files_count=0,
                notes=tuple(notes),
            )

        return ChangedOnlyScanDecision(
            files_for_scanners=[],
            openapi_limit_to_scan_files=True,
            git_changed_only_requested=True,
            git_is_repository=True,
            git_graceful_full_scan_not_git=False,
            git_fallback_full_scan_used=False,
            git_changed_files_count=0,
            notes=tuple(notes),
        )

    if verbose:
        print(f"[Git] changed-only: {len(intersect)} file(s) under root will be scanned.")

    return ChangedOnlyScanDecision(
        files_for_scanners=intersect,
        openapi_limit_to_scan_files=True,
        git_changed_only_requested=True,
        git_is_repository=True,
        git_graceful_full_scan_not_git=False,
        git_fallback_full_scan_used=False,
        git_changed_files_count=len(intersect),
        notes=tuple(notes),
    )
