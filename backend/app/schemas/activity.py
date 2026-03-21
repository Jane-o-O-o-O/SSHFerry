"""Pydantic schemas for activity feed APIs."""
from __future__ import annotations

from pydantic import BaseModel


class ActivityEntryResponse(BaseModel):
    """One user-facing activity event."""

    sequence: int
    timestamp: float
    level: str
    category: str
    action: str
    title: str
    message: str


class ActivityListResponse(BaseModel):
    """List wrapper for activity feed responses."""

    items: list[ActivityEntryResponse]
    total: int
    sequence: int
