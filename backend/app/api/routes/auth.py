"""Authentication routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from backend.app.api.deps import X_SSHFERRY_TOKEN, get_app_state, require_current_user
from backend.app.schemas.auth import AuthLegacySessionResponse, AuthLoginRequest, AuthUserResponse
from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext


router = APIRouter(prefix='/auth', tags=['auth'])


@router.get('/session', response_model=AuthLegacySessionResponse)
def get_local_session(app_state: AppState = Depends(get_app_state)) -> AuthLegacySessionResponse:
    """Return the legacy local token for local-dev compatibility."""
    if not app_state.runtime_settings.legacy_local_token_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Legacy local auth session is disabled.')
    return AuthLegacySessionResponse(
        token=app_state.auth_token,
        header_name=X_SSHFERRY_TOKEN,
        token_type='local',
    )


@router.post('/login', response_model=AuthUserResponse)
def login(payload: AuthLoginRequest, request: Request, app_state: AppState = Depends(get_app_state)) -> Response:
    """Authenticate with username/password and issue auth cookies."""
    context, tokens = app_state.auth_service.login(
        username=payload.username,
        password=payload.password,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get('user-agent'),
    )
    response = JSONResponse(content=context.to_response(), status_code=status.HTTP_200_OK)
    return app_state.auth_service.attach_auth_cookies(response, tokens)


@router.get('/me', response_model=AuthUserResponse)
def get_current_user(request: Request, app_state: AppState = Depends(get_app_state)) -> Response | dict[str, object]:
    """Return the current authenticated user profile."""
    access_cookie = app_state.auth_service.get_access_cookie(request.cookies)
    if access_cookie:
        try:
            return app_state.auth_service.authenticate_access_token(access_cookie).to_response()
        except HTTPException:
            if app_state.runtime_settings.is_deployed_web:
                raise

    if app_state.runtime_settings.runtime_mode == 'local-dev':
        context, tokens = app_state.auth_service.auto_login_local_dev(
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
        )
        response = JSONResponse(content=context.to_response(), status_code=status.HTTP_200_OK)
        return app_state.auth_service.attach_auth_cookies(response, tokens)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated.')


@router.post('/refresh', response_model=AuthUserResponse)
def refresh_session(request: Request, app_state: AppState = Depends(get_app_state)) -> Response:
    """Rotate refresh token and re-issue auth cookies."""
    refresh_token = app_state.auth_service.get_refresh_cookie(request.cookies)
    context, tokens = app_state.auth_service.authenticate_refresh_token(
        refresh_token=refresh_token or '',
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get('user-agent'),
    )
    response = JSONResponse(content=context.to_response(), status_code=status.HTTP_200_OK)
    return app_state.auth_service.attach_auth_cookies(response, tokens)


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, app_state: AppState = Depends(get_app_state)) -> Response:
    """Revoke the current session and clear auth cookies."""
    refresh_token = app_state.auth_service.get_refresh_cookie(request.cookies)
    access_token = app_state.auth_service.get_access_cookie(request.cookies)
    app_state.auth_service.logout(refresh_token=refresh_token, access_token=access_token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return app_state.auth_service.clear_auth_cookies(response)


@router.get('/me/current', response_model=AuthUserResponse, include_in_schema=False)
def get_current_user_legacy_alias(context: AuthContext = Depends(require_current_user)) -> AuthUserResponse:
    """Hidden alias kept for direct dependency probing in tests."""
    return AuthUserResponse.model_validate(context.to_response())
