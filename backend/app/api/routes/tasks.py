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


def _publish_task_activity(
    app_state: AppState,
    *,
    user_id: str,
    level: str,
    action: str,
    title: str,
    message: str,
) -> None:
    app_state.activity_service.publish(
        user_id=user_id,
        level=level,
        category='task',
        action=action,
        title=title,
        message=message,
    )


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
    response = service.create_upload(payload, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='queued',
        title='Upload queued',
        message=f'{response.src_label} -> {response.dst_label}',
    )
    return response


@router.post('/upload-from-workspace', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_upload_from_workspace_task(
    payload: TaskCreateWorkspaceUploadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    response = service.create_upload_from_workspace(payload, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='queued',
        title='Workspace upload queued',
        message=f'{response.src_label} -> {response.dst_label}',
    )
    return response


@router.post('/download', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_download_task(
    payload: TaskCreateDownloadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    response = service.create_download(payload, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='queued',
        title='Download queued',
        message=f'{response.src_label} -> {response.dst_label}',
    )
    return response


@router.post('/download-to-workspace', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_download_to_workspace_task(
    payload: TaskCreateWorkspaceDownloadRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    response = service.create_download_to_workspace(payload, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='queued',
        title='Workspace download queued',
        message=f'{response.src_label} -> {response.dst_label}',
    )
    return response


@router.post('/remote-copy', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_remote_copy_task(
    payload: TaskCreateRemoteCopyRequest,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskResponse:
    service = TaskService(app_state)
    response = service.create_remote_copy(payload, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='queued',
        title='Remote copy queued',
        message=f'{response.src_label} -> {response.dst_label}',
    )
    return response


@router.post('/{task_id}/pause', response_model=TaskActionResponse)
def pause_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    response = service.pause_task(task_id, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='pause',
        title='Pause requested',
        message=f'Task {task_id} received a pause request.',
    )
    return response


@router.post('/{task_id}/resume', response_model=TaskActionResponse)
def resume_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    response = service.resume_task(task_id, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='resume',
        title='Resume requested',
        message=f'Task {task_id} resumed from the queue.',
    )
    return response


@router.post('/{task_id}/cancel', response_model=TaskActionResponse)
def cancel_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    response = service.cancel_task(task_id, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='warning',
        action='cancel',
        title='Cancel requested',
        message=f'Task {task_id} received a cancellation request.',
    )
    return response


@router.post('/{task_id}/restart', response_model=TaskActionResponse)
def restart_task(
    task_id: str,
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> TaskActionResponse:
    service = TaskService(app_state)
    response = service.restart_task(task_id, context.user.user_id)
    _publish_task_activity(
        app_state,
        user_id=context.user.user_id,
        level='info',
        action='restart',
        title='Restart requested',
        message=f'Task {task_id} was queued again.',
    )
    return response


@router.delete('/finished', status_code=status.HTTP_204_NO_CONTENT)
def clear_finished_tasks(
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> Response:
    service = TaskService(app_state)
    removed = service.clear_finished_tasks(context.user.user_id)
    if removed:
        _publish_task_activity(
            app_state,
            user_id=context.user.user_id,
            level='info',
            action='clear_finished',
            title='Finished tasks cleared',
            message=f'{removed} finished task(s) were removed from the task list.',
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
