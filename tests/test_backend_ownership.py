"""Tests for backend ownership boundaries and owner-only raw logs."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil
from threading import Lock
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from backend.app.api.deps import resolve_request_auth_context
from backend.app.main import create_app
from backend.app.services.app_state import AppState
from backend.app.services.auth_service import AuthContext, AuthSession, AuthUser
from backend.app.services.remote_file_service import RemoteFileService
from src.services.site_store import SiteStore
from src.shared.models import SiteConfig, Task


class FakeScheduler:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_lock = Lock()
        self.task_queue: list[str] = []
        self.queued_task_ids: set[str] = set()
        self.active_task_ids: set[str] = set()
        self.futures: dict[str, object] = {}
        self.parallel_threshold = 50 * 1024 * 1024
        self.running = True

    def add_task(self, task: Task) -> str:
        with self.task_lock:
            self.tasks[task.task_id] = task
            self.task_queue.append(task.task_id)
            self.queued_task_ids.add(task.task_id)
        return task.task_id

    def get_task(self, task_id: str) -> Task | None:
        with self.task_lock:
            return self.tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        with self.task_lock:
            return [replace(task) for task in self.tasks.values()]

    def pause_task(self, task_id: str) -> bool:
        with self.task_lock:
            task = self.tasks.get(task_id)
            if task is None or task.status != 'running':
                return False
            task.paused = True
            return True

    def resume_task(self, task_id: str) -> bool:
        with self.task_lock:
            task = self.tasks.get(task_id)
            if task is None or task.status != 'paused':
                return False
            task.status = 'pending'
            task.paused = False
            return True

    def cancel_task(self, task_id: str) -> bool:
        with self.task_lock:
            task = self.tasks.get(task_id)
            if task is None or task.status not in ('pending', 'running', 'paused'):
                return False
            task.status = 'canceled'
            return True

    def restart_task(self, task_id: str) -> bool:
        with self.task_lock:
            task = self.tasks.get(task_id)
            if task is None or task.status not in ('failed', 'canceled', 'done', 'skipped'):
                return False
            task.status = 'pending'
            task.bytes_done = 0
            task.error_message = None
            task.error_code = None
            task.subtask_done = 0
            task.current_file = ''
            return True


class FakeAppState:
    def __init__(self, scheduler: FakeScheduler | None = None):
        self.scheduler = scheduler or FakeScheduler()
        self.remote_sessions: dict[str, SiteConfig] = {}
        self.session_lock = Lock()
        self.auth_token = 'fake-token'
        self.startup_error = None
        self.site_store = None
        self.runtime_settings = SimpleNamespace(workspace_root=Path('.workspace'), legacy_local_token_enabled=True)
        self.log_service = SimpleNamespace(snapshot=lambda limit=None: SimpleNamespace(items=[], total=0, sequence=0), clear=lambda: None)

    def start(self):
        return None

    def stop(self):
        return None

    @property
    def is_ready(self) -> bool:
        return self.scheduler is not None and getattr(self.scheduler, 'running', False)

    @property
    def session_count(self) -> int:
        return len(self.remote_sessions)

    def require_scheduler(self):
        if self.scheduler is None:
            raise RuntimeError('Task scheduler unavailable')
        return self.scheduler


def _build_context(user_id: str, role: str = 'owner') -> AuthContext:
    return AuthContext(
        user=AuthUser(
            user_id=user_id,
            username=user_id,
            display_name=user_id,
            role=role,
        ),
        session=AuthSession(
            session_id=f'session-{user_id}',
            user_id=user_id,
            username=user_id,
            role=role,
            refresh_token_hash='',
            created_at=1,
            expires_at=9999999999,
            last_refreshed_at=1,
        ),
        auth_scheme='test',
    )


def _build_client(state, context: AuthContext) -> TestClient:
    app = create_app(app_state_factory=lambda: state)
    app.dependency_overrides[resolve_request_auth_context] = lambda: context
    return TestClient(app)


def _run_in_temp_dir(test_name: str, runner) -> None:
    base_dir = Path('.tmp_test_backend_ownership') / test_name
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    try:
        runner(base_dir)
    finally:
        if base_dir.exists():
            shutil.rmtree(base_dir)


def test_sites_are_scoped_to_current_user():
    def runner(base_dir: Path):
        store = SiteStore(path=base_dir / 'sites.json')
        store.save([
            SiteConfig(
                name='alpha',
                host='alpha.example.com',
                port=22,
                username='alice',
                auth_method='password',
                remote_root='/work',
                owner_user_id='user-a',
            ),
            SiteConfig(
                name='beta',
                host='beta.example.com',
                port=22,
                username='bob',
                auth_method='password',
                remote_root='/work',
                owner_user_id='user-b',
            ),
        ])
        state = AppState(site_store=store)

        with _build_client(state, _build_context('user-a')) as client:
            listed = client.get('/api/sites')
            create = client.post(
                '/api/sites',
                json={
                    'name': 'gamma',
                    'host': 'gamma.example.com',
                    'port': 22,
                    'username': 'carol',
                    'auth_method': 'password',
                    'remote_root': '/srv',
                    'default_transfer_protocol': 'sftp',
                },
            )
            update_other = client.put(
                '/api/sites/beta',
                json={
                    'name': 'beta',
                    'host': 'beta2.example.com',
                    'port': 22,
                    'username': 'bob',
                    'auth_method': 'password',
                    'remote_root': '/work',
                    'default_transfer_protocol': 'sftp',
                },
            )

        loaded = store.load_or_raise()
        assert listed.status_code == 200
        assert listed.json()['total'] == 1
        assert listed.json()['items'][0]['name'] == 'alpha'
        assert create.status_code == 201
        assert update_other.status_code == 404
        created = next(site for site in loaded if site.name == 'gamma')
        assert created.owner_user_id == 'user-a'

    _run_in_temp_dir('sites_scope', runner)


def test_sessions_and_remote_files_are_scoped_to_current_user(monkeypatch):
    class FakeEngine:
        def connect(self):
            return None

        def disconnect(self):
            return None

        def list_dir(self, path):
            return [SimpleNamespace(name='data.txt', path=f'{path}/data.txt', is_dir=False, size=4, mtime=1.0, mode=None)]

    monkeypatch.setattr(RemoteFileService, '_build_engine', staticmethod(lambda _site: FakeEngine()))

    def runner(base_dir: Path):
        state = AppState(site_store=SiteStore(path=base_dir / 'sites.json'))
        with state.session_lock:
            state.remote_sessions['session-a'] = SiteConfig(
                name='alpha',
                host='alpha.example.com',
                port=22,
                username='alice',
                auth_method='password',
                remote_root='/alpha',
                password='secret',
                owner_user_id='user-a',
            )
            state.remote_sessions['session-b'] = SiteConfig(
                name='beta',
                host='beta.example.com',
                port=22,
                username='bob',
                auth_method='password',
                remote_root='/beta',
                password='secret',
                owner_user_id='user-b',
            )

        with _build_client(state, _build_context('user-a')) as client:
            listed = client.get('/api/sessions')
            own_remote = client.get('/api/remote-files/list', params={'session_id': 'session-a'})
            foreign_remote = client.get('/api/remote-files/list', params={'session_id': 'session-b'})
            close_foreign = client.post('/api/sessions/close', json={'session_id': 'session-b'})

        assert listed.status_code == 200
        assert listed.json()['total'] == 1
        assert listed.json()['items'][0]['session_id'] == 'session-a'
        assert own_remote.status_code == 200
        assert foreign_remote.status_code == 404
        assert close_foreign.status_code == 404

    _run_in_temp_dir('sessions_scope', runner)


def test_tasks_are_scoped_to_current_user():
    scheduler = FakeScheduler()
    scheduler.tasks = {
        'task-a': Task(
            task_id='task-a',
            kind='file_transfer',
            engine='sftp',
            src='a',
            dst='b',
            bytes_total=1,
            owner_user_id='user-a',
            status='done',
        ),
        'task-b': Task(
            task_id='task-b',
            kind='file_transfer',
            engine='sftp',
            src='c',
            dst='d',
            bytes_total=1,
            owner_user_id='user-b',
            status='done',
        ),
    }
    state = FakeAppState(scheduler=scheduler)

    with _build_client(state, _build_context('user-a')) as client:
        listed = client.get('/api/tasks')
        restart_foreign = client.post('/api/tasks/task-b/restart')
        cleared = client.delete('/api/tasks/finished')
        listed_after = client.get('/api/tasks')

    assert listed.status_code == 200
    assert listed.json()['total'] == 1
    assert listed.json()['items'][0]['task_id'] == 'task-a'
    assert restart_foreign.status_code == 404
    assert cleared.status_code == 204
    assert listed_after.status_code == 200
    assert listed_after.json()['items'] == []
    assert 'task-b' in scheduler.tasks
    assert 'task-a' not in scheduler.tasks


def test_logs_are_owner_only():
    def runner(base_dir: Path):
        state = AppState(site_store=SiteStore(path=base_dir / 'sites.json'))

        with _build_client(state, _build_context('viewer-1', role='viewer')) as client:
            listed = client.get('/api/logs')
            cleared = client.delete('/api/logs')

        with _build_client(state, _build_context('owner-1', role='owner')) as client:
            owner_listed = client.get('/api/logs')

        assert listed.status_code == 403
        assert cleared.status_code == 403
        assert owner_listed.status_code == 200

    _run_in_temp_dir('logs_owner_only', runner)


def test_task_websocket_filters_tasks_by_current_user(monkeypatch):
    scheduler = FakeScheduler()
    scheduler.tasks = {
        'task-a': Task(
            task_id='task-a',
            kind='file_transfer',
            engine='sftp',
            src='a',
            dst='b',
            bytes_total=1,
            owner_user_id='user-a',
            status='pending',
        ),
        'task-b': Task(
            task_id='task-b',
            kind='file_transfer',
            engine='sftp',
            src='c',
            dst='d',
            bytes_total=1,
            owner_user_id='user-b',
            status='pending',
        ),
    }
    state = FakeAppState(scheduler=scheduler)
    monkeypatch.setattr('backend.app.api.routes.ws.require_websocket_authenticated', lambda _websocket: _build_context('user-a'))

    with _build_client(state, _build_context('user-a')) as client:
        with client.websocket_connect('/api/ws/tasks') as websocket:
            message = websocket.receive_json()

    assert message['type'] == 'task_snapshot'
    assert message['total'] == 1
    assert message['items'][0]['task_id'] == 'task-a'