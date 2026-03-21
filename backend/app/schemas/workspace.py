"""Pydantic schemas for workspace APIs."""
from __future__ import annotations

from pydantic import BaseModel, Field


class WorkspaceEntryResponse(BaseModel):
    """One file or directory inside the user's workspace."""

    name: str
    path: str
    is_dir: bool
    size: int
    mtime: float
    exists: bool = True


class WorkspaceListResponse(BaseModel):
    """Directory listing response for the workspace."""

    current_path: str
    parent_path: str | None
    items: list[WorkspaceEntryResponse]
    total: int


class WorkspaceStatResponse(BaseModel):
    """Stat and aggregate summary for a workspace path."""

    entry: WorkspaceEntryResponse
    file_count: int
    dir_count: int
    total_size: int


class WorkspaceDeleteRequest(BaseModel):
    """Delete one or more workspace paths."""

    paths: list[str] = Field(min_length=1)


class WorkspaceDeleteResponse(BaseModel):
    """Delete summary."""

    deleted_paths: list[str]
    total: int


class WorkspaceResetResponse(BaseModel):
    """Summary for clearing one authenticated user's persisted data."""

    deleted_site_count: int
    closed_session_count: int
    canceled_task_count: int
    cleared_task_count: int
    cleared_activity_count: int
    workspace_file_count: int
    workspace_dir_count: int
    workspace_total_size: int


class WorkspaceUploadResponse(BaseModel):
    """Upload summary."""

    target_path: str
    uploaded_paths: list[str]
    total: int
