"""Orchestrate one-click cleanup for the current authenticated user."""
from __future__ import annotations

from contextlib import nullcontext
import time

from fastapi import HTTPException, status

from backend.app.schemas.workspace import WorkspaceResetResponse
from backend.app.services.app_state import AppState
from backend.app.services.workspace_service import WorkspaceService


TASK_STOP_TIMEOUT_SECONDS = 5.0
TASK_STOP_POLL_INTERVAL_SECONDS = 0.1


class UserCleanupService:
    """Delete persisted user data without touching other users' records."""

    def __init__(self, app_state: AppState):
        self.app_state = app_state

    def reset_user_data(self, user_id: str) -> WorkspaceResetResponse:
        canceled_task_count, cleared_task_count = self._cancel_and_clear_tasks(user_id)
        closed_session_count = self._close_sessions(user_id)
        deleted_site_count = self._delete_sites(user_id)
        workspace_file_count, workspace_dir_count, workspace_total_size = self._clear_workspace(user_id)
        cleared_activity_count = self._clear_activity(user_id)
        return WorkspaceResetResponse(
            deleted_site_count=deleted_site_count,
            closed_session_count=closed_session_count,
            canceled_task_count=canceled_task_count,
            cleared_task_count=cleared_task_count,
            cleared_activity_count=cleared_activity_count,
            workspace_file_count=workspace_file_count,
            workspace_dir_count=workspace_dir_count,
            workspace_total_size=workspace_total_size,
        )

    def _cancel_and_clear_tasks(self, user_id: str) -> tuple[int, int]:
        scheduler = getattr(self.app_state, 'scheduler', None)
        if scheduler is None:
            return 0, 0

        with self._task_guard(scheduler):
            owned_unfinished_task_ids = [
                task_id
                for task_id, task in getattr(scheduler, 'tasks', {}).items()
                if getattr(task, 'owner_user_id', None) == user_id and not task.is_finished
            ]

        canceled = 0
        for task_id in owned_unfinished_task_ids:
            if scheduler.cancel_task(task_id):
                canceled += 1

        if owned_unfinished_task_ids:
            deadline = time.monotonic() + TASK_STOP_TIMEOUT_SECONDS
            while time.monotonic() < deadline:
                remaining = self._count_unfinished_tasks(scheduler, user_id)
                if remaining == 0:
                    break
                time.sleep(TASK_STOP_POLL_INTERVAL_SECONDS)

            remaining = self._count_unfinished_tasks(scheduler, user_id)
            if remaining:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'{remaining} task(s) are still stopping. Please retry in a moment.',
                )

        cleared = 0
        with self._task_guard(scheduler):
            tasks = getattr(scheduler, 'tasks', {})
            owned_task_ids = [
                task_id
                for task_id, task in tasks.items()
                if getattr(task, 'owner_user_id', None) == user_id
            ]
            for task_id in owned_task_ids:
                tasks.pop(task_id, None)
                queued_task_ids = getattr(scheduler, 'queued_task_ids', None)
                if queued_task_ids is not None:
                    queued_task_ids.discard(task_id)
                active_task_ids = getattr(scheduler, 'active_task_ids', None)
                if active_task_ids is not None:
                    active_task_ids.discard(task_id)
                futures = getattr(scheduler, 'futures', None)
                if futures is not None:
                    futures.pop(task_id, None)
                cleared += 1

            if hasattr(scheduler, 'task_queue'):
                scheduler.task_queue = [task_id for task_id in scheduler.task_queue if task_id in tasks]

        return canceled, cleared

    @staticmethod
    def _count_unfinished_tasks(scheduler, user_id: str) -> int:
        with UserCleanupService._task_guard(scheduler):
            return sum(
                1
                for task in getattr(scheduler, 'tasks', {}).values()
                if getattr(task, 'owner_user_id', None) == user_id and not task.is_finished
            )

    def _close_sessions(self, user_id: str) -> int:
        with self._session_guard():
            owned_session_ids = [
                session_id
                for session_id, site in self.app_state.remote_sessions.items()
                if getattr(site, 'owner_user_id', None) == user_id
            ]
            for session_id in owned_session_ids:
                self.app_state.remote_sessions.pop(session_id, None)
        return len(owned_session_ids)

    def _delete_sites(self, user_id: str) -> int:
        site_store = getattr(self.app_state, 'site_store', None)
        if site_store is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Site store is unavailable.')

        try:
            sites = site_store.load_or_raise()
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

        remaining_sites = []
        deleted = 0
        for site in sites:
            if getattr(site, 'owner_user_id', None) == user_id:
                deleted += 1
            else:
                remaining_sites.append(site)

        if deleted:
            try:
                site_store.save(remaining_sites)
            except RuntimeError as exc:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

        return deleted

    def _clear_workspace(self, user_id: str) -> tuple[int, int, int]:
        runtime_settings = getattr(self.app_state, 'runtime_settings', None)
        workspace_root = getattr(runtime_settings, 'workspace_root', None)
        if workspace_root is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Workspace root is unavailable.')

        service = WorkspaceService(workspace_root)
        return service.clear_user_root(user_id)

    def _clear_activity(self, user_id: str) -> int:
        activity_service = getattr(self.app_state, 'activity_service', None)
        if activity_service is None or not hasattr(activity_service, 'clear_user'):
            return 0
        return int(activity_service.clear_user(user_id))

    def _session_guard(self):
        lock = getattr(self.app_state, 'session_lock', None)
        return lock if lock is not None else nullcontext()

    @staticmethod
    def _task_guard(scheduler):
        lock = getattr(scheduler, 'task_lock', None)
        return lock if lock is not None else nullcontext()
