"""Activity feed routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import get_app_state, require_current_user
from backend.app.schemas.activity import ActivityEntryResponse, ActivityListResponse
from backend.app.services.activity_service import ActivitySnapshot
from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext


DEFAULT_ACTIVITY_LIMIT = 200
MAX_ACTIVITY_LIMIT = 1000
router = APIRouter(prefix='/activity', tags=['activity'])


def _to_response(snapshot: ActivitySnapshot) -> ActivityListResponse:
    return ActivityListResponse(
        items=[
            ActivityEntryResponse(
                sequence=item.sequence,
                timestamp=item.timestamp,
                level=item.level,
                category=item.category,
                action=item.action,
                title=item.title,
                message=item.message,
            )
            for item in snapshot.items
        ],
        total=snapshot.total,
        sequence=snapshot.sequence,
    )


@router.get('', response_model=ActivityListResponse)
def list_activity(
    limit: int = Query(default=DEFAULT_ACTIVITY_LIMIT, ge=1, le=MAX_ACTIVITY_LIMIT),
    context: AuthContext = Depends(require_current_user),
    app_state: AppState = Depends(get_app_state),
) -> ActivityListResponse:
    snapshot = app_state.activity_service.snapshot(user_id=context.user.user_id, limit=limit)
    return _to_response(snapshot)
