"""Deterministic auth / role drift helpers."""

from contractlens.auth.auth_comparator import compare_auth_contracts, compare_auth_contracts_from_dicts
from contractlens.auth.backend_auth_scanner import scan_backend_auth
from contractlens.auth.frontend_auth_scanner import scan_frontend_auth
from contractlens.auth.models import AuthMismatch, BackendAuthFinding, FrontendAuthFinding

__all__ = [
    "AuthMismatch",
    "BackendAuthFinding",
    "FrontendAuthFinding",
    "compare_auth_contracts",
    "compare_auth_contracts_from_dicts",
    "scan_backend_auth",
    "scan_frontend_auth",
]
