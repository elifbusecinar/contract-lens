"""Paths and demo-oriented defaults."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_DIR = PACKAGE_ROOT / "contractlens-reports"
RUNS_DIR = PACKAGE_ROOT / "contractlens-runs"
SAMPLE_FEATURE = "Create Project + Upload File"


def feature_slug(feature_name: str) -> str:
    """Slug for report filenames, e.g. 'Create Project + Upload File' -> create-project-upload-file."""
    import re

    s = feature_name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def default_report_path(feature_name: str, report_dir: Path | None = None) -> Path:
    base = report_dir or DEFAULT_REPORT_DIR
    return base / f"contractlens-report-{feature_slug(feature_name)}.md"


def default_html_report_path(feature_name: str, report_dir: Path | None = None) -> Path:
    base = report_dir or DEFAULT_REPORT_DIR
    return base / f"contractlens-report-{feature_slug(feature_name)}.html"


def display_path_under_repo(absolute: str | Path) -> str:
    """Stable relative path for demo logs (POSIX slashes when under PACKAGE_ROOT)."""
    try:
        return Path(absolute).resolve().relative_to(PACKAGE_ROOT.resolve()).as_posix()
    except ValueError:
        return str(Path(absolute).resolve())
