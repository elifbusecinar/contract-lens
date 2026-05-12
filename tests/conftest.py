"""Pytest fixtures."""

from __future__ import annotations

import pytest

from contractlens.mcp_server.permissions import reset_extra_ignore_dir_names
from contractlens.openapi.parser import set_max_schema_ref_chain


@pytest.fixture(autouse=True)
def reset_global_scan_settings() -> None:
    reset_extra_ignore_dir_names()
    set_max_schema_ref_chain(None)
    yield
    reset_extra_ignore_dir_names()
    set_max_schema_ref_chain(None)
