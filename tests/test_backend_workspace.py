"""Tests for workspace APIs."""
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


def _build_test_client(store_path: Path) -> TestClient:
    state = AppState(site_store=SiteStore(path=store_path))
    app = create_app(app_state_factory=lambda: state)
    client = TestClient(app)
    client.headers.update({X_SSHFERRY_TOKEN: state.auth_token})
    return client


def _run_in_temp_fs(test_name: str, runner):
    base_dir = Path('.tmp_test_workspace') / test_name
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    store_path = base_dir / 'sites.json'
    workspace_root = base_dir / 'workspace-root'
    env = {'SSHFERRY_WORKSPACE_ROOT': str(workspace_root)}
    try:
        with patch.dict(os.environ, env, clear=False):
            runner(base_dir, store_path, workspace_root)
    finally:
        if base_dir.exists():
            shutil.rmtree(base_dir)


def test_workspace_items_defaults_to_user_root_and_lists_entries():
    def runner(base_dir: Path, store_path: Path, workspace_root: Path):
        user_root = workspace_root / 'local-dev-owner'
        user_root.mkdir(parents=True, exist_ok=True)
        (user_root / 'docs').mkdir()
        (user_root / 'alpha.txt').write_text('alpha', encoding='utf-8')

        with _build_test_client(store_path) as client:
            response = client.get('/api/workspace/items')

        assert response.status_code == 200
        body = response.json()
        assert body['current_path'] == '/'
        assert body['parent_path'] is None
        assert body['total'] == 2
        assert body['items'][0]['name'] == 'docs'
        assert body['items'][0]['is_dir'] is True
        assert body['items'][1]['path'] == '/alpha.txt'

    _run_in_temp_fs('list_root', runner)


def test_workspace_upload_stat_and_delete_flow():
    def runner(_base_dir: Path, store_path: Path, workspace_root: Path):
        with _build_test_client(store_path) as client:
            uploaded = client.post(
                '/api/workspace/uploads',
                files=[
                    ('files', ('alpha.txt', b'alpha', 'text/plain')),
                    ('files', ('readme.txt', b'hello', 'text/plain')),
                    ('target_path', (None, '/')),
                    ('relative_paths', (None, 'alpha.txt')),
                    ('relative_paths', (None, 'docs/readme.txt')),
                ],
            )
            listing = client.get('/api/workspace/items')
            stat = client.get('/api/workspace/items/stat')
            deleted = client.request('DELETE', '/api/workspace/items', json={'paths': ['/docs']})
            listing_after = client.get('/api/workspace/items')

        assert uploaded.status_code == 201
        assert uploaded.json()['uploaded_paths'] == ['/alpha.txt', '/docs/readme.txt']

        assert listing.status_code == 200
        names = [item['name'] for item in listing.json()['items']]
        assert names == ['docs', 'alpha.txt']

        assert stat.status_code == 200
        stat_body = stat.json()
        assert stat_body['entry']['path'] == '/'
        assert stat_body['file_count'] == 2
        assert stat_body['dir_count'] == 1
        assert stat_body['total_size'] == 10

        assert deleted.status_code == 200
        assert deleted.json()['deleted_paths'] == ['/docs']

        assert listing_after.status_code == 200
        assert listing_after.json()['total'] == 1
        assert listing_after.json()['items'][0]['path'] == '/alpha.txt'

        actual_file = workspace_root / 'local-dev-owner' / 'alpha.txt'
        assert actual_file.exists()
        assert not (workspace_root / 'local-dev-owner' / 'docs').exists()

    _run_in_temp_fs('upload_delete', runner)


def test_workspace_rejects_path_escape_and_root_delete():
    def runner(_base_dir: Path, store_path: Path, _workspace_root: Path):
        with _build_test_client(store_path) as client:
            escaped = client.get('/api/workspace/items', params={'path': '/../secret'})
            delete_root = client.request('DELETE', '/api/workspace/items', json={'paths': ['/']})

        assert escaped.status_code == 400
        assert 'Illegal workspace path' in escaped.json()['detail']
        assert delete_root.status_code == 400
        assert delete_root.json()['detail'] == 'Workspace root cannot be deleted.'

    _run_in_temp_fs('guardrails', runner)