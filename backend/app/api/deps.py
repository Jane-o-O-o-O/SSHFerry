"""Shared API dependencies."""
from __future__ import annotations

import secrets
import time

from fastapi import Depends, Header, HTTPException, Request, WebSocket, WebSocketException, status

from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext, AuthSession, AuthUser, ROLE_OWNER


X_SSHFERRY_TOKEN = 'X-SSHFerry-Token'


def get_app_state(request: Request) -> AppState:
    """Return the singleton app state stored on the FastAPI app."""
    return request.app.state.app_state


def get_websocket_app_state(websocket: WebSocket) -> AppState:
    """Return the singleton app state stored on the FastAPI app for websocket routes."""
    return websocket.app.state.app_state


def _legacy_local_auth_enabled(app_state: AppState) -> bool:
    runtime_settings = getattr(app_state, 'runtime_settings', None)
    if runtime_settings is None:
        return True
    return bool(getattr(runtime_settings, 'legacy_local_token_enabled', False))


def _build_legacy_local_context(app_state: AppState) -> AuthContext:
    auth_service = getattr(app_state, 'auth_service', None)
    if auth_service is not None:
        return auth_service.get_local_dev_context()

    now = int(time.time())
    return AuthContext(
        user=AuthUser(
            user_id='local-dev-owner',
            username='localdev',
            display_name='Local Development',
            role=ROLE_OWNER,
            is_local_dev=True,
        ),
        session=AuthSession(
            session_id='local-dev-legacy',
            user_id='local-dev-owner',
            username='localdev',
            role=ROLE_OWNER,
            refresh_token_hash='',
            created_at=now,
            expires_at=now + 3600,
            last_refreshed_at=now,
        ),
        auth_scheme='local-token',
    )


def _resolve_legacy_local_token(app_state: AppState, provided_token: str | None) -> AuthContext | None:
    if not _legacy_local_auth_enabled(app_state):
        return None
    if not provided_token:
        return None
    if not secrets.compare_digest(provided_token, app_state.auth_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid local session token.')
    return _build_legacy_local_context(app_state)


def _require_owner_context(context: AuthContext) -> AuthContext:
    if context.user.role != ROLE_OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Owner access required.')
    return context


def resolve_request_auth_context(
    request: Request,
    x_sshferry_token: str | None = Header(default=None, alias=X_SSHFERRY_TOKEN),
) -> AuthContext:
    """Resolve the authenticated request context from auth cookies or local-dev fallback."""
    app_state = get_app_state(request)
    auth_service = getattr(app_state, 'auth_service', None)
    if auth_service is not None:
        access_cookie = auth_service.get_access_cookie(request.cookies)
        if access_cookie:
            return auth_service.authenticate_access_token(access_cookie)

    legacy_context = _resolve_legacy_local_token(app_state, x_sshferry_token)
    if legacy_context is not None:
        return legacy_context

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated.')


def require_authenticated_request(_: AuthContext = Depends(resolve_request_auth_context)) -> None:
    """Route dependency used to guard authenticated HTTP endpoints."""
    return None


def require_current_user(context: AuthContext = Depends(resolve_request_auth_context)) -> AuthContext:
    """Return the current authenticated user context."""
    return context


def require_owner_user(context: AuthContext = Depends(resolve_request_auth_context)) -> AuthContext:
    """Return the current authenticated user context and require owner role."""
    return _require_owner_context(context)


def require_websocket_authenticated(websocket: WebSocket) -> AuthContext:
    """Validate websocket auth via cookies or local-dev token fallback."""
    app_state = get_websocket_app_state(websocket)
    auth_service = getattr(app_state, 'auth_service', None)
    if auth_service is not None:
        access_cookie = auth_service.get_access_cookie(websocket.cookies)
        if access_cookie:
            try:
                return auth_service.authenticate_access_token(access_cookie)
            except HTTPException as exc:
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=exc.detail) from exc

    provided = websocket.query_params.get('token') or websocket.headers.get(X_SSHFERRY_TOKEN)
    if _legacy_local_auth_enabled(app_state) and provided:
        if secrets.compare_digest(provided, app_state.auth_token):
            return _build_legacy_local_context(app_state)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='Invalid local session token.')

    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='Not authenticated.')


def require_websocket_owner(websocket: WebSocket) -> AuthContext:
    """Validate websocket auth and require owner role."""
    context = require_websocket_authenticated(websocket)
    if context.user.role != ROLE_OWNER:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='Owner access required.')
    return context