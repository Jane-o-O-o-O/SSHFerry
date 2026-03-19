"""Cookie-backed authentication service with deployed-web and local-dev support."""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import hmac
import json
import logging
import secrets
import time
from threading import RLock
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import Response

from backend.app.config import RuntimeSettings


PASSWORD_SCHEME = 'pbkdf2_sha256'
PASSWORD_ITERATIONS = 600_000
ROLE_OWNER = 'owner'
LOCAL_DEV_USER_ID = 'local-dev-owner'


@dataclass(slots=True)
class AuthUser:
    """Authenticated SSHFerry user."""

    user_id: str
    username: str
    display_name: str
    role: str
    is_local_dev: bool = False


@dataclass(slots=True)
class AuthSession:
    """Server-side refresh session record."""

    session_id: str
    user_id: str
    username: str
    role: str
    refresh_token_hash: str
    created_at: int
    expires_at: int
    last_refreshed_at: int
    client_ip: str | None = None
    user_agent: str | None = None
    revoked_at: int | None = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > int(time.time())


@dataclass(slots=True)
class AuthTokens:
    """Issued cookie token pair for one session."""

    access_token: str
    refresh_token: str
    access_expires_at: int
    refresh_expires_at: int


@dataclass(slots=True)
class AuthContext:
    """Current authenticated request context."""

    user: AuthUser
    session: AuthSession
    auth_scheme: str

    def to_response(self) -> dict[str, Any]:
        return {
            'id': self.user.user_id,
            'username': self.user.username,
            'display_name': self.user.display_name,
            'role': self.user.role,
            'auth_scheme': self.auth_scheme,
            'session_id': self.session.session_id,
            'session_expires_at': self.session.expires_at,
        }


@dataclass(slots=True)
class FailedLoginState:
    failed_attempts: int = 0
    locked_until: int | None = None


class AuthService:
    """Issue and validate auth cookies for SSHFerry."""

    def __init__(self, settings: RuntimeSettings, logger: logging.Logger | None = None) -> None:
        self.settings = settings
        self.logger = logger or logging.getLogger(__name__)
        self.lock = RLock()
        self.owner_user: AuthUser | None = None
        self.local_dev_user = AuthUser(
            user_id=LOCAL_DEV_USER_ID,
            username='localdev',
            display_name='Local Development',
            role=ROLE_OWNER,
            is_local_dev=True,
        )
        self._secret = (settings.auth_secret or secrets.token_urlsafe(48)).encode('utf-8')
        self._sessions_by_id: dict[str, AuthSession] = {}
        self._session_ids_by_refresh_hash: dict[str, str] = {}
        self._rate_limit_buckets: dict[str, list[int]] = {}
        self._login_failures: dict[str, FailedLoginState] = {}
        self._ready_error: str | None = None

    @property
    def is_ready(self) -> bool:
        return self._ready_error is None

    @property
    def ready_error(self) -> str | None:
        return self._ready_error

    def start(self) -> None:
        """Initialize auth runtime state and owner bootstrap."""
        self.settings.workspace_root.mkdir(parents=True, exist_ok=True)
        self.settings.owner_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if self.settings.is_deployed_web:
                self.owner_user = self._load_or_create_owner()
            elif self.settings.owner_file.exists() or self.settings.owner_username:
                self.owner_user = self._load_or_create_owner()
            else:
                self.owner_user = None
            self._ready_error = None
        except Exception as exc:
            self._ready_error = str(exc)
            self.logger.error('Auth service failed to initialize: %s', exc)
            raise

    def stop(self) -> None:
        """Clear in-memory auth sessions."""
        with self.lock:
            self._sessions_by_id.clear()
            self._session_ids_by_refresh_hash.clear()
            self._rate_limit_buckets.clear()
            self._login_failures.clear()

    def login(self, username: str, password: str, client_ip: str | None, user_agent: str | None) -> tuple[AuthContext, AuthTokens]:
        """Validate credentials and issue a new auth session."""
        normalized_username = username.strip().lower()
        if not normalized_username or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username and password are required.')
        self._ensure_ready()
        self._check_rate_limit(
            key=f'login:{client_ip or "unknown"}',
            window_seconds=self.settings.login_rate_limit_window_seconds,
            max_attempts=self.settings.login_rate_limit_max_attempts,
            detail='Too many login attempts. Try again later.',
        )
        self._ensure_login_not_locked(normalized_username)

        if self.owner_user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username/password login is unavailable in local-dev mode without an initialized owner account.',
            )
        if normalized_username != self.owner_user.username.lower() or not verify_password(password, self._read_owner_password_hash()):
            self._record_login_failure(normalized_username)
            self.logger.warning('Login failed for username=%s ip=%s', normalized_username, client_ip or 'unknown')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password.')

        self._reset_login_failures(normalized_username)
        context, tokens = self._issue_session(self.owner_user, client_ip=client_ip, user_agent=user_agent)
        self.logger.info('Login succeeded for username=%s ip=%s', normalized_username, client_ip or 'unknown')
        return context, tokens

    def auto_login_local_dev(self, client_ip: str | None, user_agent: str | None) -> tuple[AuthContext, AuthTokens]:
        """Issue a local-dev owner-like session without password bootstrap."""
        self._ensure_ready()
        context, tokens = self._issue_session(self.local_dev_user, client_ip=client_ip, user_agent=user_agent)
        self.logger.info('Issued local-dev auth session for ip=%s', client_ip or 'unknown')
        return context, tokens

    def authenticate_access_token(self, access_token: str) -> AuthContext:
        """Resolve an access token to the current authenticated user."""
        self._ensure_ready()
        payload = self._decode_access_token(access_token)
        if payload.get('typ') != 'access':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token.')
        session_id = str(payload.get('session_id') or '')
        if not session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token payload.')
        with self.lock:
            session = self._sessions_by_id.get(session_id)
            if session is None or not session.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired or revoked.')
        user = self._get_user_by_id(session.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exists.')
        return AuthContext(user=user, session=session, auth_scheme='cookie')

    def authenticate_refresh_token(
        self,
        refresh_token: str,
        client_ip: str | None,
        user_agent: str | None,
    ) -> tuple[AuthContext, AuthTokens]:
        """Rotate a refresh token and issue a fresh access/refresh pair."""
        self._ensure_ready()
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing refresh token.')
        self._check_rate_limit(
            key=f'refresh:{client_ip or "unknown"}',
            window_seconds=self.settings.refresh_rate_limit_window_seconds,
            max_attempts=self.settings.refresh_rate_limit_max_attempts,
            detail='Too many refresh attempts. Try again later.',
        )

        refresh_hash = self._hash_refresh_token(refresh_token)
        now = int(time.time())
        with self.lock:
            self._purge_expired_sessions(now)
            session_id = self._session_ids_by_refresh_hash.get(refresh_hash)
            session = self._sessions_by_id.get(session_id) if session_id else None
            if session is None or not session.is_active or not hmac.compare_digest(session.refresh_token_hash, refresh_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired refresh token.')
            user = self._get_user_by_id(session.user_id)
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exists.')
            new_refresh_token = self._generate_refresh_token()
            new_refresh_hash = self._hash_refresh_token(new_refresh_token)
            self._session_ids_by_refresh_hash.pop(session.refresh_token_hash, None)
            session.refresh_token_hash = new_refresh_hash
            session.expires_at = now + self.settings.refresh_token_ttl_seconds
            session.last_refreshed_at = now
            session.client_ip = client_ip or session.client_ip
            session.user_agent = user_agent or session.user_agent
            self._session_ids_by_refresh_hash[new_refresh_hash] = session.session_id
            access_token, access_expires_at = self._create_access_token(user, session)
            context = AuthContext(user=user, session=session, auth_scheme='cookie')
            tokens = AuthTokens(
                access_token=access_token,
                refresh_token=new_refresh_token,
                access_expires_at=access_expires_at,
                refresh_expires_at=session.expires_at,
            )
        self.logger.info('Refresh succeeded for session=%s ip=%s', context.session.session_id, client_ip or 'unknown')
        return context, tokens

    def logout(self, refresh_token: str | None = None, access_token: str | None = None) -> None:
        """Revoke the current refresh session."""
        with self.lock:
            if refresh_token:
                refresh_hash = self._hash_refresh_token(refresh_token)
                session_id = self._session_ids_by_refresh_hash.pop(refresh_hash, None)
                if session_id and session_id in self._sessions_by_id:
                    self._sessions_by_id[session_id].revoked_at = int(time.time())
            elif access_token:
                try:
                    payload = self._decode_access_token(access_token)
                except HTTPException:
                    return
                session_id = str(payload.get('session_id') or '')
                session = self._sessions_by_id.get(session_id)
                if session is not None:
                    self._session_ids_by_refresh_hash.pop(session.refresh_token_hash, None)
                    session.revoked_at = int(time.time())

    def attach_auth_cookies(self, response: Response, tokens: AuthTokens) -> Response:
        """Attach access and refresh cookies to a response."""
        response.set_cookie(
            key=self.settings.access_cookie_name,
            value=tokens.access_token,
            httponly=True,
            secure=self.settings.cookie_secure,
            samesite=self.settings.cookie_samesite,
            max_age=self.settings.access_token_ttl_seconds,
            path='/',
        )
        response.set_cookie(
            key=self.settings.refresh_cookie_name,
            value=tokens.refresh_token,
            httponly=True,
            secure=self.settings.cookie_secure,
            samesite=self.settings.cookie_samesite,
            max_age=self.settings.refresh_token_ttl_seconds,
            path='/',
        )
        return response

    def clear_auth_cookies(self, response: Response) -> Response:
        """Clear auth cookies from a response."""
        response.delete_cookie(
            key=self.settings.access_cookie_name,
            path='/',
            secure=self.settings.cookie_secure,
            httponly=True,
            samesite=self.settings.cookie_samesite,
        )
        response.delete_cookie(
            key=self.settings.refresh_cookie_name,
            path='/',
            secure=self.settings.cookie_secure,
            httponly=True,
            samesite=self.settings.cookie_samesite,
        )
        return response

    def get_access_cookie(self, cookies: dict[str, str]) -> str | None:
        return cookies.get(self.settings.access_cookie_name)

    def get_refresh_cookie(self, cookies: dict[str, str]) -> str | None:
        return cookies.get(self.settings.refresh_cookie_name)

    def get_local_dev_context(self) -> AuthContext:
        """Build a pseudo-auth context for legacy local token fallback."""
        now = int(time.time())
        session = AuthSession(
            session_id='local-dev-legacy',
            user_id=self.local_dev_user.user_id,
            username=self.local_dev_user.username,
            role=self.local_dev_user.role,
            refresh_token_hash='',
            created_at=now,
            expires_at=now + self.settings.refresh_token_ttl_seconds,
            last_refreshed_at=now,
        )
        return AuthContext(user=self.local_dev_user, session=session, auth_scheme='local-token')

    def _load_or_create_owner(self) -> AuthUser:
        owner_file = self.settings.owner_file
        if owner_file.exists():
            payload = json.loads(owner_file.read_text(encoding='utf-8'))
            password_hash = str(payload.get('password_hash') or '').strip()
            username = str(payload.get('username') or '').strip().lower()
            display_name = str(payload.get('display_name') or username).strip() or username
            if not username or not password_hash:
                raise RuntimeError(f'Owner file {owner_file} is missing username or password_hash.')
            return AuthUser(
                user_id=str(payload.get('id') or 'owner'),
                username=username,
                display_name=display_name,
                role=str(payload.get('role') or ROLE_OWNER),
            )

        username = (self.settings.owner_username or '').strip().lower()
        password_hash = (self.settings.owner_password_hash or '').strip()
        password = self.settings.owner_password or ''
        if not username:
            raise RuntimeError(
                'No owner account is initialized. Configure SSHFERRY_OWNER_USERNAME together with SSHFERRY_OWNER_PASSWORD '
                'or SSHFERRY_OWNER_PASSWORD_HASH before starting deployed-web mode.'
            )
        if not password_hash and not password:
            raise RuntimeError(
                'Owner bootstrap requires SSHFERRY_OWNER_PASSWORD or SSHFERRY_OWNER_PASSWORD_HASH when the owner file does not exist.'
            )
        if not password_hash:
            password_hash = hash_password(password)
        owner_payload = {
            'id': 'owner',
            'username': username,
            'display_name': self.settings.owner_display_name or username,
            'role': ROLE_OWNER,
            'password_hash': password_hash,
            'created_at': int(time.time()),
        }
        owner_file.write_text(json.dumps(owner_payload, ensure_ascii=True, indent=2), encoding='utf-8')
        self.logger.info('Bootstrapped owner account at %s', owner_file)
        return AuthUser(
            user_id='owner',
            username=username,
            display_name=self.settings.owner_display_name or username,
            role=ROLE_OWNER,
        )

    def _read_owner_password_hash(self) -> str:
        payload = json.loads(self.settings.owner_file.read_text(encoding='utf-8'))
        return str(payload.get('password_hash') or '')

    def _issue_session(self, user: AuthUser, client_ip: str | None, user_agent: str | None) -> tuple[AuthContext, AuthTokens]:
        session_id = str(uuid4())
        now = int(time.time())
        refresh_token = self._generate_refresh_token()
        session = AuthSession(
            session_id=session_id,
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            refresh_token_hash=self._hash_refresh_token(refresh_token),
            created_at=now,
            expires_at=now + self.settings.refresh_token_ttl_seconds,
            last_refreshed_at=now,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        with self.lock:
            self._purge_expired_sessions(now)
            self._sessions_by_id[session_id] = session
            self._session_ids_by_refresh_hash[session.refresh_token_hash] = session_id
        access_token, access_expires_at = self._create_access_token(user, session)
        context = AuthContext(user=user, session=session, auth_scheme='cookie')
        tokens = AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=session.expires_at,
        )
        return context, tokens

    def _create_access_token(self, user: AuthUser, session: AuthSession) -> tuple[str, int]:
        now = int(time.time())
        expires_at = now + self.settings.access_token_ttl_seconds
        payload = {
            'sub': user.user_id,
            'username': user.username,
            'role': user.role,
            'session_id': session.session_id,
            'iat': now,
            'exp': expires_at,
            'typ': 'access',
        }
        payload_bytes = json.dumps(payload, ensure_ascii=True, separators=(',', ':'), sort_keys=True).encode('utf-8')
        encoded_payload = _b64encode(payload_bytes)
        signature = hmac.new(self._secret, encoded_payload.encode('ascii'), hashlib.sha256).digest()
        return f'v1.{encoded_payload}.{_b64encode(signature)}', expires_at

    def _decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            version, encoded_payload, encoded_signature = token.split('.', 2)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token.') from exc
        if version != 'v1':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unsupported access token version.')
        expected_signature = hmac.new(self._secret, encoded_payload.encode('ascii'), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64encode(expected_signature), encoded_signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token signature.')
        try:
            payload = json.loads(_b64decode(encoded_payload).decode('utf-8'))
        except Exception as exc:  # pragma: no cover - defensive parsing path
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Malformed access token payload.') from exc
        if int(payload.get('exp') or 0) <= int(time.time()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token expired.')
        return payload

    def _get_user_by_id(self, user_id: str) -> AuthUser | None:
        if user_id == self.local_dev_user.user_id:
            return self.local_dev_user
        if self.owner_user and self.owner_user.user_id == user_id:
            return self.owner_user
        return None

    def _hash_refresh_token(self, refresh_token: str) -> str:
        digest = hmac.new(self._secret, refresh_token.encode('utf-8'), hashlib.sha256).hexdigest()
        return digest

    def _generate_refresh_token(self) -> str:
        return secrets.token_urlsafe(48)

    def _purge_expired_sessions(self, now: int) -> None:
        expired_ids = [session_id for session_id, session in self._sessions_by_id.items() if session.expires_at <= now]
        for session_id in expired_ids:
            session = self._sessions_by_id.pop(session_id, None)
            if session is not None:
                self._session_ids_by_refresh_hash.pop(session.refresh_token_hash, None)

    def _check_rate_limit(self, key: str, window_seconds: int, max_attempts: int, detail: str) -> None:
        now = int(time.time())
        with self.lock:
            attempts = [stamp for stamp in self._rate_limit_buckets.get(key, []) if stamp > now - window_seconds]
            if len(attempts) >= max_attempts:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)
            attempts.append(now)
            self._rate_limit_buckets[key] = attempts

    def _ensure_login_not_locked(self, username: str) -> None:
        now = int(time.time())
        with self.lock:
            state = self._login_failures.get(username)
            if state is None:
                return
            if state.locked_until and state.locked_until > now:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail='Too many failed login attempts. Try again later.',
                )
            if state.locked_until and state.locked_until <= now:
                self._login_failures.pop(username, None)

    def _record_login_failure(self, username: str) -> None:
        now = int(time.time())
        with self.lock:
            state = self._login_failures.get(username, FailedLoginState())
            state.failed_attempts += 1
            if state.failed_attempts >= self.settings.login_lockout_max_failures:
                state.locked_until = now + self.settings.login_lockout_seconds
            self._login_failures[username] = state

    def _reset_login_failures(self, username: str) -> None:
        with self.lock:
            self._login_failures.pop(username, None)

    def _ensure_ready(self) -> None:
        if self._ready_error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=self._ready_error)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b'=').decode('ascii')


def _b64decode(value: str) -> bytes:
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-SHA256 using a random salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PASSWORD_ITERATIONS)
    return f'{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}'


def verify_password(password: str, encoded: str) -> bool:
    """Verify a password against the stored PBKDF2-SHA256 hash."""
    try:
        scheme, iterations_raw, salt_b64, digest_b64 = encoded.split('$', 3)
    except ValueError:
        return False
    if scheme != PASSWORD_SCHEME:
        return False
    try:
        iterations = int(iterations_raw)
    except ValueError:
        return False
    salt = _b64decode(salt_b64)
    expected = _b64decode(digest_b64)
    candidate = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return hmac.compare_digest(candidate, expected)

