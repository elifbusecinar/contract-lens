"""Optional repo-local ContractLens settings (contractlens.toml / contractlens.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from contractlens.config import PACKAGE_ROOT


@dataclass(frozen=True)
class UserContractLensConfig:
    extra_ignore_dirs: tuple[str, ...] = ()
    emit_html_by_default: bool = False
    openapi_max_ref_chain: int | None = None  # None = use parser default
    probe_base_url: str = ""
    scan_cache: bool = False


def _parse_section(section: dict[str, Any]) -> UserContractLensConfig:
    raw_ignore = section.get("extra_ignore_dirs") or section.get("extra_ignore_dir_names") or []
    if not isinstance(raw_ignore, list):
        raw_ignore = []
    dirs = tuple(str(x).strip() for x in raw_ignore if str(x).strip())

    emit_html = bool(section.get("emit_html_by_default") or section.get("html_by_default"))

    depth_raw = section.get("openapi_max_ref_chain") or section.get("openapi_ref_depth")
    depth: int | None = None
    if depth_raw is not None:
        try:
            depth = max(4, min(int(depth_raw), 96))
        except (TypeError, ValueError):
            depth = None

    probe = ""
    pb = section.get("probe_base_url") or section.get("probe_url")
    if isinstance(pb, str) and pb.strip():
        probe = pb.strip()
    probe_section = section.get("probe")
    if isinstance(probe_section, dict):
        bu = probe_section.get("base_url") or probe_section.get("url")
        if isinstance(bu, str) and bu.strip():
            probe = bu.strip()

    scan_cache = bool(section.get("scan_cache") or section.get("scan_cache_enabled"))

    return UserContractLensConfig(
        extra_ignore_dirs=dirs,
        emit_html_by_default=emit_html,
        openapi_max_ref_chain=depth,
        probe_base_url=probe,
        scan_cache=scan_cache,
    )


def _load_toml(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]

        loaded = tomllib.loads(text)
    except Exception:
        return None
    if not isinstance(loaded, dict):
        return None
    sec = loaded.get("contractlens")
    if isinstance(sec, dict):
        return sec
    return loaded


def _load_yaml(path: Path) -> dict[str, Any] | None:
    try:
        import yaml
    except ImportError:
        return None
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    sec = raw.get("contractlens")
    if isinstance(sec, dict):
        return sec
    return raw


def load_user_contractlens_config(search_roots: list[Path]) -> UserContractLensConfig:
    """First matching ``contractlens.toml`` / ``contractlens.yaml`` under search_roots wins."""
    names = ("contractlens.toml", "contractlens.yaml")
    for root in search_roots:
        base = root.resolve()
        if not base.is_dir():
            continue
        for name in names:
            path = base / name
            if not path.is_file():
                continue
            section = _load_toml(path) if name.endswith(".toml") else _load_yaml(path)
            if section is not None:
                return _parse_section(section)
    return UserContractLensConfig()


def contractlens_config_search_roots(repo_root: Path) -> list[Path]:
    """Prefer analyzed repo, then ContractLens package root (for dogfooding)."""
    return [repo_root.resolve(), PACKAGE_ROOT.resolve()]
