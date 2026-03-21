"""Health and runtime status routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.api.deps import X_SSHFERRY_TOKEN, get_app_state
from backend.app.services.app_state import AppState
from src import __version__


router = APIRouter(tags=['health'])


@router.get('/health')
def get_health(app_state: AppState = Depends(get_app_state)) -> dict[str, object]:
    """Return basic liveness and backend runtime status."""
    settings = app_state.runtime_settings
    return {
        'status': 'ok' if app_state.is_ready else 'degraded',
        'service': 'sshferry-backend',
        'version': __version__,
        'ready': app_state.is_ready,
        'scheduler_running': app_state.scheduler.running if app_state.scheduler else False,
        'session_count': app_state.session_count,
        'startup_error': app_state.startup_error,
        'auth_required': True,
        'auth_header_name': X_SSHFERRY_TOKEN if settings.legacy_local_token_enabled else None,
        'auth_mode': settings.auth_mode,
        'runtime_mode': settings.runtime_mode,
        'access_cookie_name': settings.access_cookie_name,
        'refresh_cookie_name': settings.refresh_cookie_name,
        'workspace_root': str(settings.workspace_root),
        'features': [
            'activity-feed',
            'debug-logs',
            'workspace-reset',
        ],
    }
