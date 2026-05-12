"""Local Git utilities for ContractLens (no GitHub API)."""

from contractlens.git.diff import (
    ChangedOnlyScanDecision,
    changed_paths_relative_to_git_root,
    get_changed_files_relative_to_root,
    git_toplevel,
    resolve_changed_only_scan_files,
)

__all__ = [
    "ChangedOnlyScanDecision",
    "changed_paths_relative_to_git_root",
    "get_changed_files_relative_to_root",
    "git_toplevel",
    "resolve_changed_only_scan_files",
]
