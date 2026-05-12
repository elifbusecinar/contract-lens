"""Structured auth / role hints from heuristic scans."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FrontendAuthFinding(BaseModel):
    source: str
    line: int
    kind: str
    detail: str
    roles_mentioned: list[str] = Field(default_factory=list)
    has_authorization_header: bool = False
    has_bearer_token: bool = False
    has_with_credentials: bool = False
    has_role_or_permission_check: bool = False


class BackendAuthFinding(BaseModel):
    source: str
    line: int
    kind: str
    detail: str
    roles_required: list[str] = Field(default_factory=list)
    policy: str | None = None
    auth_required: bool = True
    allow_anonymous: bool = False


class AuthMismatch(BaseModel):
    area: str
    frontend_assumption: str
    backend_rule: str
    risk: str
    suggestion: str
