"""Task routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from backend.app.api.deps import get_app_state, require_current_user
from backend.app.schemas.tasks import (
    TaskActionResponse,
    TaskCreateDownloadRequest,
    TaskCreateRemoteCopyRequest,
    TaskCreateUploadRequest,
    TaskCreateWorkspaceDownloadRequest,
    TaskCreateWorkspaceUploadRequest,
    TaskListResponse,
    TaskResponse,
)
from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext
from backend.app.services.task_service import TaskService


router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('', response_model=TaskListResponse)
def list_tasks(
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskListResponse:
    service = TaskService(app_state)
    items = service.list_tasks(context.user.user_id)
    return TaskListResponse(items=items, total=len(items))


@router.post('/upload', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_upload_task(
    payload: TaskCreateUploadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    return service.create_upload(payload, context.user.user_id)


@router.post('/upload-from-workspace', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_upload_from_workspace_task(
    payload: TaskCreateWorkspaceUploadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    return service.create_upload_from_workspace(payload, context.user.user_id)


@router.post('/download', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_download_task(
    payload: TaskCreateDownloadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    return service.create_download(payload, context.user.user_id)


@router.post('/download-to-workspace', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_download_to_workspace_task(
    payload: TaskCreateWorkspaceDownloadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    return service.create_download_to_workspace(payload, context.user.user_id)


@router.post('/remote-copy', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_remote_copy_task(
    payload: TaskCreateRemoteCopyRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    return service.create_remote_copy(payload, context.user.user_id)


@router.post('/{task_id}/pause', response_model=TaskActionResponse)
def pause_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    return service.pause_task(task_id, context.user.user_id)


@router.post('/{task_id}/resume', response_model=TaskActionResponse)
def resume_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    return service.resume_task(task_id, context.user.user_id)


@router.post('/{task_id}/cancel', response_model=TaskActionResponse)
def cancel_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    return service.cancel_task(task_id, context.user.user_id)


@router.post('/{task_id}/restart', response_model=TaskActionResponse)
def restart_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    return service.restart_task(task_id, context.user.user_id)


@router.delete('/finished', status_code=status.HTTP_204_NO_CONTENT)
def clear_finished_tasks(
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> Response:
    service = TaskService(app_state)
    service.clear_finished_tasks(context.user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)