"""Pydantic models for API contracts and mismatches."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ApiContract(BaseModel):
    method: str
    path: str
    source: str
    line: int | None = None
    request_fields: list[str] = Field(default_factory=list)
    response_fields: list[str] = Field(default_factory=list)
    request_dto: str | None = None
    response_dto: str | None = None
    auth: str | None = None


class ContractMismatch(BaseModel):
    area: str
    frontend_expects: str
    backend_provides: str
    risk: str
    suggestion: str
    comment_path: str | None = None
    comment_line: int | None = None


class RiskSummary(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    unknown: int = 0
