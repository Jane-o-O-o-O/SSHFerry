"""Tests for persistent site storage behavior."""
import json
from pathlib import Path
import shutil

import pytest

from src.services.site_store import SiteStore
from src.shared.models import SiteConfig


TEST_SECRET = 'unit-secret'


def _run_in_temp_store(test_name: str, runner) -> None:
    base_dir = Path('.tmp_test_site_store') / test_name
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    store_path = base_dir / 'sites.json'
    try:
        runner(store_path)
    finally:
        if base_dir.exists():
            shutil.rmtree(base_dir)


def test_save_does_not_persist_password_by_default():
    def runner(path: Path):
        store = SiteStore(path=path, secret_key=TEST_SECRET)
        site = SiteConfig(
            name='demo',
            host='example.com',
            port=22,
            username='alice',
            auth_method='password',
            password='top-secret',
            remote_root='/work',
        )

        store.save([site])

        raw = json.loads(path.read_text(encoding='utf-8'))
        assert 'password' not in raw[0]
        assert 'password_encrypted' not in raw[0]
        assert raw[0]['remember_password'] is False

    _run_in_temp_store('no_password_persist', runner)


def test_save_encrypts_password_when_explicitly_enabled():
    def runner(path: Path):
        store = SiteStore(path=path, secret_key=TEST_SECRET)
        site = SiteConfig(
            name='demo',
            host='example.com',
            port=22,
            username='alice',
            auth_method='password',
            password='top-secret',
            remote_root='/work',
            remember_password=True,
        )

        store.save([site])

        raw = json.loads(path.read_text(encoding='utf-8'))
        assert raw[0]['secret_format'] == 'fernet-v1'
        assert raw[0]['password_encrypted']
        assert raw[0]['password_encrypted'] != 'top-secret'
        assert 'password' not in raw[0]

        loaded = store.load_or_raise()
        assert loaded[0].password == 'top-secret'
        assert loaded[0].remember_password is True

    _run_in_temp_store('encrypt_password', runner)


def test_save_encrypts_key_passphrase_when_present():
    def runner(path: Path):
        store = SiteStore(path=path, secret_key=TEST_SECRET)
        site = SiteConfig(
            name='gpu',
            host='example.com',
            port=22,
            username='alice',
            auth_method='key',
            key_path='C:/keys/id_ed25519',
            key_passphrase='key-secret',
            remote_root='/work',
        )

        store.save([site])

        raw = json.loads(path.read_text(encoding='utf-8'))
        assert raw[0]['secret_format'] == 'fernet-v1'
        assert raw[0]['key_passphrase_encrypted']
        assert raw[0]['key_passphrase_encrypted'] != 'key-secret'
        assert 'key_passphrase' not in raw[0]

        loaded = store.load_or_raise()
        assert loaded[0].key_passphrase == 'key-secret'

    _run_in_temp_store('encrypt_key_passphrase', runner)


def test_load_or_raise_rejects_encrypted_secret_without_configured_key(monkeypatch):
    def runner(path: Path):
        store = SiteStore(path=path, secret_key=TEST_SECRET)
        site = SiteConfig(
            name='demo',
            host='example.com',
            port=22,
            username='alice',
            auth_method='password',
            password='top-secret',
            remote_root='/work',
            remember_password=True,
        )
        store.save([site])

        monkeypatch.setenv('SSHFERRY_RUNTIME_MODE', 'deployed-web')
        monkeypatch.delenv('SSHFERRY_SITE_SECRET', raising=False)

        strict_store = SiteStore(path=path)
        with pytest.raises(RuntimeError, match='SSHFERRY_SITE_SECRET'):
            strict_store.load_or_raise()

    _run_in_temp_store('missing_secret', runner)


def test_load_defaults_empty_remote_root_to_slash():
    def runner(path: Path):
        path.write_text(
            json.dumps(
                [
                    {
                        'name': 'demo',
                        'host': 'example.com',
                        'port': 22,
                        'username': 'alice',
                        'auth_method': 'password',
                        'remote_root': '',
                    }
                ]
            ),
            encoding='utf-8',
        )

        store = SiteStore(path=path)
        loaded = store.load_or_raise()

        assert len(loaded) == 1
        assert loaded[0].remote_root == '/'

    _run_in_temp_store('remote_root_default', runner)


def test_default_transfer_protocol_persisted_and_backward_compatible():
    def runner(path: Path):
        store = SiteStore(path=path, secret_key=TEST_SECRET)
        site = SiteConfig(
            name='demo',
            host='example.com',
            port=22,
            username='alice',
            auth_method='password',
            remote_root='/work',
            default_transfer_protocol='scp',
        )
        store.save([site])

        loaded = store.load_or_raise()
        assert len(loaded) == 1
        assert loaded[0].default_transfer_protocol == 'scp'

        path.write_text(
            json.dumps(
                [
                    {
                        'name': 'legacy',
                        'host': 'old.example.com',
                        'port': 22,
                        'username': 'bob',
                        'auth_method': 'password',
                        'remote_root': '/',
                    }
                ]
            ),
            encoding='utf-8',
        )
        loaded_legacy = store.load_or_raise()
        assert loaded_legacy[0].default_transfer_protocol == 'sftp'

    _run_in_temp_store('protocol_backward_compatible', runner)