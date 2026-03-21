"""Workspace routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from backend.app.api.deps import get_app_state, require_current_user
from backend.app.schemas.workspace import (
    WorkspaceDeleteRequest,
    WorkspaceDeleteResponse,
    WorkspaceListResponse,
    WorkspaceResetResponse,
    WorkspaceStatResponse,
    WorkspaceUploadResponse,
)
from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext
from backend.app.services.user_cleanup_service import UserCleanupService
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
    response = service.save_uploads(
        user_id=context.user.user_id,
        files=files,
        target_path=target_path,
        relative_paths=relative_paths,
    )
    app_state.activity_service.publish(
        user_id=context.user.user_id,
        level='success',
        category='workspace',
        action='upload',
        title='Workspace upload completed',
        message=f'{response.total} item(s) uploaded into {response.target_path}.',
    )
    return response


@router.delete('/items', response_model=WorkspaceDeleteResponse)
def delete_workspace_items(
    payload: WorkspaceDeleteRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> WorkspaceDeleteResponse:
    service = WorkspaceService(app_state.runtime_settings.workspace_root)
    response = service.delete_paths(context.user.user_id, payload.paths)
    app_state.activity_service.publish(
        user_id=context.user.user_id,
        level='warning',
        category='workspace',
        action='delete',
        title='Workspace items deleted',
        message=f'{response.total} item(s) removed from the workspace.',
    )
    return response


@router.post('/reset', response_model=WorkspaceResetResponse)
def reset_workspace_data(
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> WorkspaceResetResponse:
    service = UserCleanupService(app_state)
    response = service.reset_user_data(context.user.user_id)
    app_state.activity_service.publish(
        user_id=context.user.user_id,
        level='warning',
        category='workspace',
        action='reset',
        title='User data cleared',
        message='Saved sites, sessions, tasks, activity entries, and workspace files were removed.',
    )
    return response
