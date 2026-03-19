"""Pydantic schemas for auth APIs."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    """Username/password login request."""

    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthUserResponse(BaseModel):
    """Authenticated user profile returned to the frontend."""

    id: str
    username: str
    display_name: str
    role: str
    auth_scheme: str
    session_id: str
    session_expires_at: int


class AuthLegacySessionResponse(BaseModel):
    """Legacy local token payload kept for local-dev compatibility."""

    token: str
    header_name: str
    token_type: str
