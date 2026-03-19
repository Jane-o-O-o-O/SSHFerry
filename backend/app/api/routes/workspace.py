"""Workspace routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from backend.app.api.deps import get_app_state, require_current_user
from backend.app.schemas.workspace import (
    WorkspaceDeleteRequest,
    WorkspaceDeleteResponse,
    WorkspaceListResponse,
    WorkspaceStatResponse,
    WorkspaceUploadResponse,
)
from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext
from backend.app.services.workspace_service import WorkspaceService


router = APIRouter(prefix='/workspace', tags=['workspace'])


@router.get('/items', response_model=WorkspaceListResponse)
def list_workspace_items(
    path: str | None = Query(default=None),
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> WorkspaceListResponse:
    service = WorkspaceService(app_state.runtime_settings.workspace_root)
    return service.list_dir(context.user.user_id, path)


@router.get('/items/stat', response_model=WorkspaceStatResponse)
def stat_workspace_path(
    path: str | None = Query(default=None),
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> WorkspaceStatResponse:
    service = WorkspaceService(app_state.runtime_settings.workspace_root)
    return service.stat_path(context.user.user_id, path)


@router.post('/uploads', response_model=WorkspaceUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_workspace_items(
    files: list[UploadFile] = File(...),
    target_path: str | None = Form(default=None),
    relative_paths: list[str] | None = Form(default=None),
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> WorkspaceUploadResponse:
    service = WorkspaceService(app_state.runtime_settings.workspace_root)
    return service.save_uploads(
        user_id=context.user.user_id,
        files=files,
        target_path=target_path,
        relative_paths=relative_paths,
    )


@router.delete('/items', response_model=WorkspaceDeleteResponse)
def delete_workspace_items(
    payload: WorkspaceDeleteRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> WorkspaceDeleteResponse:
    service = WorkspaceService(app_state.runtime_settings.workspace_root)
    return service.delete_paths(context.user.user_id, payload.paths)