from __future__ import annotations
import os
from pathlib import Path
import shutil
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.api.deps import X_SSHFERRY_TOKEN
from backend.app.main import create_app
from backend.app.services.app_state import AppState
from src.services.site_store import SiteStore

ALLOWED_ORIGIN = 'http://localhost:5173'

def _build_state(store_path: Path) -> AppState:
    return AppState(site_store=SiteStore(path=store_path))

def _run_in_temp_store(test_name: str, runner):
    base_dir = Path('.tmp_test_backend_auth') / test_name
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    store_path = base_dir / 'sites.json'
    try:
        runner(store_path, base_dir)
    finally:
        if base_dir.exists():
            shutil.rmtree(base_dir)

def test_auth_session_returns_token_and_header_name():
    def runner(store_path: Path, _: Path):
        state = _build_state(store_path)
        app = create_app(app_state_factory=lambda: state)
        with TestClient(app) as client:
            response = client.get('/api/auth/session')
        assert response.status_code == 200
        body = response.json()
        assert body['token'] == state.auth_token
        assert body['header_name'] == X_SSHFERRY_TOKEN
        assert body['token_type'] == 'local'
    _run_in_temp_store('auth-session', runner)

def test_protected_route_requires_token_header():
    def runner(store_path: Path, _: Path):
        state = _build_state(store_path)
        app = create_app(app_state_factory=lambda: state)
        with TestClient(app) as client:
            missing = client.get('/api/sites')
            client.headers.update({X_SSHFERRY_TOKEN: state.auth_token})
            allowed = client.get('/api/sites')
        assert missing.status_code == 401
        assert allowed.status_code == 200
    _run_in_temp_store('token-required', runner)

def test_deployed_web_signup_login_me_refresh_logout_flow():
    def runner(store_path: Path, base_dir: Path):
        owner_file = base_dir / 'owner.json'
        users_file = base_dir / 'users.json'
        env = {
            'SSHFERRY_RUNTIME_MODE': 'deployed-web',
            'SSHFERRY_OWNER_USERNAME': 'owner',
            'SSHFERRY_OWNER_PASSWORD': 'secret-pass-123',
            'SSHFERRY_OWNER_FILE': str(owner_file),
            'SSHFERRY_USERS_FILE': str(users_file),
            'SSHFERRY_AUTH_COOKIE_SECURE': 'false',
        }
        with patch.dict(os.environ, env, clear=False):
            state = _build_state(store_path)
            app = create_app(app_state_factory=lambda: state)
            with TestClient(app) as client:
                health = client.get('/api/health')
                anonymous_me = client.get('/api/auth/me')
                signup = client.post('/api/auth/signup', json={'username': 'alice', 'password': 'secret-pass-456', 'display_name': 'Alice'})
                me = client.get('/api/auth/me')
                protected = client.get('/api/sites')
                logout = client.post('/api/auth/logout')
                login = client.post('/api/auth/login', json={'username': 'alice', 'password': 'secret-pass-456'})
                refreshed = client.post('/api/auth/refresh')
                owner_login = client.post('/api/auth/login', json={'username': 'owner', 'password': 'secret-pass-123'})
                me_after_owner_login = client.get('/api/auth/me')
        assert health.status_code == 200
        health_body = health.json()
        assert health_body['runtime_mode'] == 'deployed-web'
        assert health_body['auth_mode'] == 'cookie-session'
        assert health_body['ready'] is True
        assert anonymous_me.status_code == 401
        assert signup.status_code == 201
        assert signup.json()['username'] == 'alice'
        assert signup.json()['role'] == 'operator'
        assert state.runtime_settings.access_cookie_name in signup.cookies
        assert state.runtime_settings.refresh_cookie_name in signup.cookies
        assert me.status_code == 200
        assert me.json()['username'] == 'alice'
        assert protected.status_code == 200
        assert logout.status_code == 204
        assert login.status_code == 200
        assert login.json()['username'] == 'alice'
        assert refreshed.status_code == 200
        assert refreshed.json()['username'] == 'alice'
        assert owner_login.status_code == 200
        assert me_after_owner_login.status_code == 200
        assert me_after_owner_login.json()['role'] == 'owner'
    _run_in_temp_store('deployed-web-flow', runner)

def test_cors_preflight_allows_local_dev_origin():
    def runner(store_path: Path, _: Path):
        state = _build_state(store_path)
        app = create_app(app_state_factory=lambda: state)
        with TestClient(app) as client:
            response = client.options('/api/sites', headers={'Origin': ALLOWED_ORIGIN, 'Access-Control-Request-Method': 'GET', 'Access-Control-Request-Headers': X_SSHFERRY_TOKEN})
        assert response.status_code == 200
        assert response.headers['access-control-allow-origin'] == ALLOWED_ORIGIN
    _run_in_temp_store('cors-allowed', runner)

def test_cors_preflight_blocks_unknown_origin():
    def runner(store_path: Path, _: Path):
        state = _build_state(store_path)
        app = create_app(app_state_factory=lambda: state)
        with TestClient(app) as client:
            response = client.options('/api/sites', headers={'Origin': 'https://evil.example.com', 'Access-Control-Request-Method': 'GET', 'Access-Control-Request-Headers': X_SSHFERRY_TOKEN})
        assert response.status_code == 400
        assert 'access-control-allow-origin' not in response.headers
    _run_in_temp_store('cors-blocked', runner)
