from __future__ import annotations
import base64, hashlib, hmac, json, logging, re, secrets, time
from dataclasses import dataclass
from threading import RLock
from typing import Any
from uuid import uuid4
from fastapi import HTTPException, status
from fastapi.responses import Response
from backend.app.config import RuntimeSettings

PASSWORD_SCHEME='pbkdf2_sha256'
PASSWORD_ITERATIONS=600_000
ROLE_OWNER='owner'
ROLE_OPERATOR='operator'
LOCAL_DEV_USER_ID='local-dev-owner'
USERNAME_PATTERN=re.compile(r'^(?=.{3,254}$)[a-zA-Z0-9_.@+-]+$')
CAPTCHA_ALPHABET='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
CAPTCHA_TTL_SECONDS=5*60
MIN_PASSWORD_LENGTH=8
MAX_PASSWORD_LENGTH=256

@dataclass(slots=True)
class AuthUser:
    user_id:str
    username:str
    display_name:str
    role:str
    is_local_dev:bool=False

@dataclass(slots=True)
class AuthSession:
    session_id:str
    user_id:str
    username:str
    role:str
    refresh_token_hash:str
    created_at:int
    expires_at:int
    last_refreshed_at:int
    client_ip:str|None=None
    user_agent:str|None=None
    revoked_at:int|None=None
    @property
    def is_active(self)->bool:
        return self.revoked_at is None and self.expires_at>int(time.time())

@dataclass(slots=True)
class AuthTokens:
    access_token:str
    refresh_token:str
    access_expires_at:int
    refresh_expires_at:int

@dataclass(slots=True)
class AuthContext:
    user:AuthUser
    session:AuthSession
    auth_scheme:str
    def to_response(self)->dict[str,Any]:
        return {
            'id':self.user.user_id,
            'username':self.user.username,
            'display_name':self.user.display_name,
            'role':self.user.role,
            'auth_scheme':self.auth_scheme,
            'session_id':self.session.session_id,
            'session_expires_at':self.session.expires_at,
        }

@dataclass(slots=True)
class FailedLoginState:
    failed_attempts:int=0
    locked_until:int|None=None

@dataclass(slots=True)
class CaptchaChallenge:
    captcha_id:str
    code:str
    expires_at:int

class AuthService:
    def __init__(self, settings:RuntimeSettings, logger:logging.Logger|None=None)->None:
        self.settings=settings
        self.logger=logger or logging.getLogger(__name__)
        self.lock=RLock()
        self.owner_user:AuthUser|None=None
        self.local_dev_user=AuthUser(user_id=LOCAL_DEV_USER_ID, username='localdev', display_name='Local Development', role=ROLE_OWNER, is_local_dev=True)
        self._secret=(settings.auth_secret or secrets.token_urlsafe(48)).encode('utf-8')
        self._sessions_by_id:dict[str,AuthSession]={}
        self._session_ids_by_refresh_hash:dict[str,str]={}
        self._rate_limit_buckets:dict[str,list[int]]={}
        self._login_failures:dict[str,FailedLoginState]={}
        self._captchas_by_id:dict[str,CaptchaChallenge]={}
        self._users_by_id:dict[str,AuthUser]={}
        self._password_hashes_by_user_id:dict[str,str]={}
        self._user_ids_by_username:dict[str,str]={}
        self._created_at_by_user_id:dict[str,int]={}
        self._ready_error:str|None=None
    @property
    def is_ready(self)->bool:
        return self._ready_error is None
    @property
    def ready_error(self)->str|None:
        return self._ready_error
    def start(self)->None:
        self.settings.workspace_root.mkdir(parents=True, exist_ok=True)
        self.settings.owner_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings.users_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._load_or_create_users()
            self._ready_error=None
        except Exception as exc:
            self._ready_error=str(exc)
            self.logger.error('Auth service failed to initialize: %s', exc)
            raise
    def stop(self)->None:
        with self.lock:
            self._sessions_by_id.clear(); self._session_ids_by_refresh_hash.clear(); self._rate_limit_buckets.clear(); self._login_failures.clear(); self._captchas_by_id.clear()
    def login(self, username:str, password:str, client_ip:str|None, user_agent:str|None)->tuple[AuthContext,AuthTokens]:
        normalized_username=self._normalize_username(username)
        if not normalized_username or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username and password are required.')
        self._ensure_ready()
        self._check_rate_limit(key=f'login:{client_ip or "unknown"}', window_seconds=self.settings.login_rate_limit_window_seconds, max_attempts=self.settings.login_rate_limit_max_attempts, detail='Too many login attempts. Try again later.')
        self._ensure_login_not_locked(normalized_username)
        user=self._get_user_by_username(normalized_username)
        password_hash=self._password_hashes_by_user_id.get(user.user_id) if user else None
        if user is None or not password_hash or not verify_password(password, password_hash):
            self._record_login_failure(normalized_username)
            self.logger.warning('Login failed for username=%s ip=%s', normalized_username, client_ip or 'unknown')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password.')
        self._reset_login_failures(normalized_username)
        context,tokens=self._issue_session(user, client_ip=client_ip, user_agent=user_agent)
        self.logger.info('Login succeeded for username=%s ip=%s', normalized_username, client_ip or 'unknown')
        return context,tokens
    def issue_captcha(self)->CaptchaChallenge:
        now=int(time.time())
        captcha=CaptchaChallenge(captcha_id=uuid4().hex, code=''.join(secrets.choice(CAPTCHA_ALPHABET) for _ in range(4)), expires_at=now+CAPTCHA_TTL_SECONDS)
        with self.lock:
            self._purge_expired_captchas(now)
            self._captchas_by_id[captcha.captcha_id]=captcha
        return captcha
    def verify_captcha(self, captcha_id:str, captcha_code:str)->None:
        normalized_id=(captcha_id or '').strip()
        normalized_code=(captcha_code or '').strip().upper()
        if not normalized_id or not normalized_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Captcha is required.')
        now=int(time.time())
        with self.lock:
            self._purge_expired_captchas(now)
            challenge=self._captchas_by_id.pop(normalized_id, None)
        if challenge is None or challenge.expires_at<=now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Captcha expired. Please refresh and try again.')
        if not hmac.compare_digest(challenge.code, normalized_code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect captcha code.')
    def signup(self, username:str, password:str, display_name:str|None, client_ip:str|None, user_agent:str|None)->tuple[AuthContext,AuthTokens]:
        self._ensure_ready()
        normalized_username=self._validate_username(username)
        normalized_display_name=self._normalize_display_name(display_name, normalized_username)
        self._validate_password(password)
        self._check_rate_limit(key=f'signup:{client_ip or "unknown"}', window_seconds=self.settings.login_rate_limit_window_seconds, max_attempts=self.settings.login_rate_limit_max_attempts, detail='Too many signup attempts. Try again later.')
        created_at=int(time.time())
        with self.lock:
            if normalized_username in self._user_ids_by_username:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username is already registered.')
            user=AuthUser(user_id=f'user-{uuid4().hex}', username=normalized_username, display_name=normalized_display_name, role=ROLE_OPERATOR)
            self._users_by_id[user.user_id]=user
            self._password_hashes_by_user_id[user.user_id]=hash_password(password)
            self._user_ids_by_username[user.username]=user.user_id
            self._created_at_by_user_id[user.user_id]=created_at
            self._persist_users_locked()
        context,tokens=self._issue_session(user, client_ip=client_ip, user_agent=user_agent)
        self.logger.info('Signup succeeded for username=%s ip=%s', normalized_username, client_ip or 'unknown')
        return context,tokens
    def auto_login_local_dev(self, client_ip:str|None, user_agent:str|None)->tuple[AuthContext,AuthTokens]:
        self._ensure_ready()
        context,tokens=self._issue_session(self.local_dev_user, client_ip=client_ip, user_agent=user_agent)
        self.logger.info('Issued local-dev auth session for ip=%s', client_ip or 'unknown')
        return context,tokens
    def authenticate_access_token(self, access_token:str)->AuthContext:
        self._ensure_ready(); payload=self._decode_access_token(access_token)
        if payload.get('typ')!='access':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token.')
        session_id=str(payload.get('session_id') or '')
        if not session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token payload.')
        with self.lock:
            session=self._sessions_by_id.get(session_id)
            if session is None or not session.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired or revoked.')
        user=self._get_user_by_id(session.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exists.')
        return AuthContext(user=user, session=session, auth_scheme='cookie')
    def authenticate_refresh_token(self, refresh_token:str, client_ip:str|None, user_agent:str|None)->tuple[AuthContext,AuthTokens]:
        self._ensure_ready()
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing refresh token.')
        self._check_rate_limit(key=f'refresh:{client_ip or "unknown"}', window_seconds=self.settings.refresh_rate_limit_window_seconds, max_attempts=self.settings.refresh_rate_limit_max_attempts, detail='Too many refresh attempts. Try again later.')
        refresh_hash=self._hash_refresh_token(refresh_token); now=int(time.time())
        with self.lock:
            self._purge_expired_sessions(now)
            session_id=self._session_ids_by_refresh_hash.get(refresh_hash)
            session=self._sessions_by_id.get(session_id) if session_id else None
            if session is None or not session.is_active or not hmac.compare_digest(session.refresh_token_hash, refresh_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired refresh token.')
            user=self._get_user_by_id(session.user_id)
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exists.')
            new_refresh_token=self._generate_refresh_token(); new_refresh_hash=self._hash_refresh_token(new_refresh_token)
            self._session_ids_by_refresh_hash.pop(session.refresh_token_hash, None)
            session.refresh_token_hash=new_refresh_hash; session.expires_at=now+self.settings.refresh_token_ttl_seconds; session.last_refreshed_at=now
            session.client_ip=client_ip or session.client_ip; session.user_agent=user_agent or session.user_agent
            self._session_ids_by_refresh_hash[new_refresh_hash]=session.session_id
            access_token,access_expires_at=self._create_access_token(user, session)
            context=AuthContext(user=user, session=session, auth_scheme='cookie')
            tokens=AuthTokens(access_token=access_token, refresh_token=new_refresh_token, access_expires_at=access_expires_at, refresh_expires_at=session.expires_at)
        self.logger.info('Refresh succeeded for session=%s ip=%s', context.session.session_id, client_ip or 'unknown')
        return context,tokens
    def logout(self, refresh_token:str|None=None, access_token:str|None=None)->None:
        with self.lock:
            if refresh_token:
                refresh_hash=self._hash_refresh_token(refresh_token)
                session_id=self._session_ids_by_refresh_hash.pop(refresh_hash, None)
                if session_id and session_id in self._sessions_by_id:
                    self._sessions_by_id[session_id].revoked_at=int(time.time())
            elif access_token:
                try:
                    payload=self._decode_access_token(access_token)
                except HTTPException:
                    return
                session_id=str(payload.get('session_id') or '')
                session=self._sessions_by_id.get(session_id)
                if session is not None:
                    self._session_ids_by_refresh_hash.pop(session.refresh_token_hash, None)
                    session.revoked_at=int(time.time())
    def attach_auth_cookies(self, response:Response, tokens:AuthTokens)->Response:
        response.set_cookie(key=self.settings.access_cookie_name, value=tokens.access_token, httponly=True, secure=self.settings.cookie_secure, samesite=self.settings.cookie_samesite, max_age=self.settings.access_token_ttl_seconds, path='/')
        response.set_cookie(key=self.settings.refresh_cookie_name, value=tokens.refresh_token, httponly=True, secure=self.settings.cookie_secure, samesite=self.settings.cookie_samesite, max_age=self.settings.refresh_token_ttl_seconds, path='/')
        return response
    def clear_auth_cookies(self, response:Response)->Response:
        response.delete_cookie(key=self.settings.access_cookie_name, path='/', secure=self.settings.cookie_secure, httponly=True, samesite=self.settings.cookie_samesite)
        response.delete_cookie(key=self.settings.refresh_cookie_name, path='/', secure=self.settings.cookie_secure, httponly=True, samesite=self.settings.cookie_samesite)
        return response
    def get_access_cookie(self, cookies:dict[str,str])->str|None:
        return cookies.get(self.settings.access_cookie_name)
    def get_refresh_cookie(self, cookies:dict[str,str])->str|None:
        return cookies.get(self.settings.refresh_cookie_name)
    def get_local_dev_context(self)->AuthContext:
        now=int(time.time())
        session=AuthSession(session_id='local-dev-legacy', user_id=self.local_dev_user.user_id, username=self.local_dev_user.username, role=self.local_dev_user.role, refresh_token_hash='', created_at=now, expires_at=now+self.settings.refresh_token_ttl_seconds, last_refreshed_at=now)
        return AuthContext(user=self.local_dev_user, session=session, auth_scheme='local-token')
    def _load_or_create_users(self)->None:
        with self.lock:
            users_payload=self._load_users_payload_locked()
            owner_payload=self._load_owner_bootstrap_payload_locked()
            changed=False
            if owner_payload is not None:
                owner_username=self._normalize_username(str(owner_payload.get('username') or ''))
                owner_payload['username']=owner_username
                owner_payload['display_name']=self._normalize_display_name(owner_payload.get('display_name'), owner_username)
                owner_payload['role']=ROLE_OWNER
                existing_index=next((index for index,item in enumerate(users_payload) if self._normalize_username(str(item.get('username') or ''))==owner_username or str(item.get('id') or '')==str(owner_payload.get('id') or '')), None)
                if existing_index is None:
                    users_payload.append(owner_payload); changed=True
                else:
                    users_payload[existing_index]={**users_payload[existing_index], **owner_payload, 'role':ROLE_OWNER}; changed=True
            users_by_id:dict[str,AuthUser]={}; password_hashes_by_user_id:dict[str,str]={}; user_ids_by_username:dict[str,str]={}; created_at_by_user_id:dict[str,int]={}
            owner_user:AuthUser|None=None; normalized_payloads:list[dict[str,Any]]=[]
            for item in users_payload:
                username=self._validate_username(str(item.get('username') or ''))
                password_hash=str(item.get('password_hash') or '').strip()
                if not password_hash:
                    raise RuntimeError(f'User {username!r} is missing password_hash.')
                user_id=str(item.get('id') or f'user-{uuid4().hex}').strip()
                role=str(item.get('role') or ROLE_OPERATOR).strip() or ROLE_OPERATOR
                display_name=self._normalize_display_name(item.get('display_name'), username)
                created_at=int(item.get('created_at') or int(time.time()))
                if username in user_ids_by_username:
                    raise RuntimeError(f'Duplicate username found in users file: {username}.')
                user=AuthUser(user_id=user_id, username=username, display_name=display_name, role=role)
                users_by_id[user.user_id]=user; password_hashes_by_user_id[user.user_id]=password_hash; user_ids_by_username[user.username]=user.user_id; created_at_by_user_id[user.user_id]=created_at
                normalized_payloads.append({'id':user.user_id,'username':user.username,'display_name':user.display_name,'role':user.role,'password_hash':password_hash,'created_at':created_at})
                if user.role==ROLE_OWNER and owner_user is None:
                    owner_user=user
            if self.settings.is_deployed_web and owner_user is None:
                raise RuntimeError('No owner account is initialized. Configure SSHFERRY_OWNER_USERNAME together with SSHFERRY_OWNER_PASSWORD or SSHFERRY_OWNER_PASSWORD_HASH before starting deployed-web mode.')
            self._users_by_id=users_by_id; self._password_hashes_by_user_id=password_hashes_by_user_id; self._user_ids_by_username=user_ids_by_username; self._created_at_by_user_id=created_at_by_user_id; self.owner_user=owner_user
            if changed or normalized_payloads!=users_payload:
                self._write_users_file_locked(normalized_payloads)
            if owner_user is not None:
                self._write_owner_file_locked(owner_user, password_hashes_by_user_id[owner_user.user_id], created_at_by_user_id[owner_user.user_id])
    def _load_users_payload_locked(self)->list[dict[str,Any]]:
        if not self.settings.users_file.exists():
            return []
        payload=json.loads(self.settings.users_file.read_text(encoding='utf-8'))
        items=payload.get('items', []) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise RuntimeError(f'Users file {self.settings.users_file} must contain a list of users.')
        return [dict(item) for item in items]
    def _load_owner_bootstrap_payload_locked(self)->dict[str,Any]|None:
        if self.settings.owner_file.exists():
            payload=json.loads(self.settings.owner_file.read_text(encoding='utf-8'))
            password_hash=str(payload.get('password_hash') or '').strip(); username=self._normalize_username(str(payload.get('username') or ''))
            if not username or not password_hash:
                raise RuntimeError(f'Owner file {self.settings.owner_file} is missing username or password_hash.')
            return {'id':str(payload.get('id') or 'owner'),'username':username,'display_name':self._normalize_display_name(payload.get('display_name'), username),'role':ROLE_OWNER,'password_hash':password_hash,'created_at':int(payload.get('created_at') or int(time.time()))}
        username=self._normalize_username(self.settings.owner_username or '')
        password_hash=(self.settings.owner_password_hash or '').strip(); password=self.settings.owner_password or ''
        if not username:
            return None
        if not password_hash and not password:
            raise RuntimeError('Owner bootstrap requires SSHFERRY_OWNER_PASSWORD or SSHFERRY_OWNER_PASSWORD_HASH when the owner file does not exist.')
        if not password_hash:
            password_hash=hash_password(password)
        return {'id':'owner','username':username,'display_name':self._normalize_display_name(self.settings.owner_display_name, username),'role':ROLE_OWNER,'password_hash':password_hash,'created_at':int(time.time())}
    def _persist_users_locked(self)->None:
        payload=[]
        for user in sorted(self._users_by_id.values(), key=lambda item:(item.role!=ROLE_OWNER, item.username)):
            payload.append({'id':user.user_id,'username':user.username,'display_name':user.display_name,'role':user.role,'password_hash':self._password_hashes_by_user_id[user.user_id],'created_at':self._created_at_by_user_id[user.user_id]})
        self._write_users_file_locked(payload)
        if self.owner_user is not None:
            self._write_owner_file_locked(self.owner_user, self._password_hashes_by_user_id[self.owner_user.user_id], self._created_at_by_user_id[self.owner_user.user_id])
    def _write_users_file_locked(self, payload:list[dict[str,Any]])->None:
        self.settings.users_file.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding='utf-8')
    def _write_owner_file_locked(self, owner_user:AuthUser, password_hash:str, created_at:int)->None:
        self.settings.owner_file.write_text(json.dumps({'id':owner_user.user_id,'username':owner_user.username,'display_name':owner_user.display_name,'role':ROLE_OWNER,'password_hash':password_hash,'created_at':created_at}, ensure_ascii=True, indent=2), encoding='utf-8')
    def _issue_session(self, user:AuthUser, client_ip:str|None, user_agent:str|None)->tuple[AuthContext,AuthTokens]:
        session_id=str(uuid4()); now=int(time.time()); refresh_token=self._generate_refresh_token()
        session=AuthSession(session_id=session_id, user_id=user.user_id, username=user.username, role=user.role, refresh_token_hash=self._hash_refresh_token(refresh_token), created_at=now, expires_at=now+self.settings.refresh_token_ttl_seconds, last_refreshed_at=now, client_ip=client_ip, user_agent=user_agent)
        with self.lock:
            self._purge_expired_sessions(now)
            self._sessions_by_id[session_id]=session; self._session_ids_by_refresh_hash[session.refresh_token_hash]=session_id
        access_token,access_expires_at=self._create_access_token(user, session)
        return AuthContext(user=user, session=session, auth_scheme='cookie'), AuthTokens(access_token=access_token, refresh_token=refresh_token, access_expires_at=access_expires_at, refresh_expires_at=session.expires_at)
    def _create_access_token(self, user:AuthUser, session:AuthSession)->tuple[str,int]:
        now=int(time.time()); expires_at=now+self.settings.access_token_ttl_seconds
        payload={'sub':user.user_id,'username':user.username,'role':user.role,'session_id':session.session_id,'iat':now,'exp':expires_at,'typ':'access'}
        payload_bytes=json.dumps(payload, ensure_ascii=True, separators=(',', ':'), sort_keys=True).encode('utf-8')
        encoded_payload=_b64encode(payload_bytes)
        signature=hmac.new(self._secret, encoded_payload.encode('ascii'), hashlib.sha256).digest()
        return f'v1.{encoded_payload}.{_b64encode(signature)}', expires_at
    def _decode_access_token(self, token:str)->dict[str,Any]:
        try:
            version,encoded_payload,encoded_signature=token.split('.', 2)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token.') from exc
        if version!='v1':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unsupported access token version.')
        expected_signature=hmac.new(self._secret, encoded_payload.encode('ascii'), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64encode(expected_signature), encoded_signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token signature.')
        try:
            payload=json.loads(_b64decode(encoded_payload).decode('utf-8'))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Malformed access token payload.') from exc
        if int(payload.get('exp') or 0)<=int(time.time()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token expired.')
        return payload
    def _get_user_by_id(self, user_id:str)->AuthUser|None:
        if user_id==self.local_dev_user.user_id:
            return self.local_dev_user
        return self._users_by_id.get(user_id)
    def _get_user_by_username(self, username:str)->AuthUser|None:
        user_id=self._user_ids_by_username.get(username)
        return self._users_by_id.get(user_id) if user_id else None
    def _hash_refresh_token(self, refresh_token:str)->str:
        return hmac.new(self._secret, refresh_token.encode('utf-8'), hashlib.sha256).hexdigest()
    def _generate_refresh_token(self)->str:
        return secrets.token_urlsafe(48)
    def _purge_expired_sessions(self, now:int)->None:
        expired_ids=[session_id for session_id,session in self._sessions_by_id.items() if session.expires_at<=now]
        for session_id in expired_ids:
            session=self._sessions_by_id.pop(session_id, None)
            if session is not None:
                self._session_ids_by_refresh_hash.pop(session.refresh_token_hash, None)
    def _purge_expired_captchas(self, now:int)->None:
        expired_ids=[captcha_id for captcha_id,captcha in self._captchas_by_id.items() if captcha.expires_at<=now]
        for captcha_id in expired_ids:
            self._captchas_by_id.pop(captcha_id, None)
    def _check_rate_limit(self, key:str, window_seconds:int, max_attempts:int, detail:str)->None:
        now=int(time.time())
        with self.lock:
            attempts=[stamp for stamp in self._rate_limit_buckets.get(key, []) if stamp>now-window_seconds]
            if len(attempts)>=max_attempts:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)
            attempts.append(now); self._rate_limit_buckets[key]=attempts
    def _ensure_login_not_locked(self, username:str)->None:
        now=int(time.time())
        with self.lock:
            state=self._login_failures.get(username)
            if state is None:
                return
            if state.locked_until and state.locked_until>now:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Too many failed login attempts. Try again later.')
            if state.locked_until and state.locked_until<=now:
                self._login_failures.pop(username, None)
    def _record_login_failure(self, username:str)->None:
        now=int(time.time())
        with self.lock:
            state=self._login_failures.get(username, FailedLoginState())
            state.failed_attempts+=1
            if state.failed_attempts>=self.settings.login_lockout_max_failures:
                state.locked_until=now+self.settings.login_lockout_seconds
            self._login_failures[username]=state
    def _reset_login_failures(self, username:str)->None:
        with self.lock:
            self._login_failures.pop(username, None)
    def _ensure_ready(self)->None:
        if self._ready_error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=self._ready_error)
    @staticmethod
    def _normalize_username(username:str)->str:
        return username.strip().lower()
    def _validate_username(self, username:str)->str:
        normalized=self._normalize_username(username)
        if not normalized:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username is required.')
        if not USERNAME_PATTERN.fullmatch(normalized):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username must be 3-254 characters and contain only letters, numbers, dot, dash, underscore, plus, or at sign.')
        return normalized
    @staticmethod
    def _normalize_display_name(display_name:str|None, fallback_username:str)->str:
        value=(display_name or '').strip() or fallback_username
        return value[:64]
    @staticmethod
    def _validate_password(password:str)->None:
        if len(password)<MIN_PASSWORD_LENGTH:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
        if len(password)>MAX_PASSWORD_LENGTH:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Password must be at most {MAX_PASSWORD_LENGTH} characters.')

def _b64encode(value:bytes)->str:
    return base64.urlsafe_b64encode(value).rstrip(b'=').decode('ascii')

def _b64decode(value:str)->bytes:
    return base64.urlsafe_b64decode(value + ('=' * (-len(value) % 4)))

def hash_password(password:str)->str:
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PASSWORD_ITERATIONS)
    return f'{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}'

def verify_password(password:str, encoded:str)->bool:
    try:
        scheme,iterations_raw,salt_b64,digest_b64=encoded.split('$', 3)
    except ValueError:
        return False
    if scheme!=PASSWORD_SCHEME:
        return False
    try:
        iterations=int(iterations_raw)
    except ValueError:
        return False
    candidate=hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), _b64decode(salt_b64), iterations)
    return hmac.compare_digest(candidate, _b64decode(digest_b64))

def render_captcha_svg(code:str)->str:
    width=132
    height=44
    chars=[]
    for index,char in enumerate(code):
        x=18 + index*26
        y=30 + (-1 if index % 2 == 0 else 2)
        rotation=-12 + index*8
        chars.append(
            f"<text x='{x}' y='{y}' font-size='24' font-family='monospace' fill='#214857' transform='rotate({rotation} {x} {y})'>{char}</text>"
        )
    lines=[
        "<line x1='10' y1='12' x2='122' y2='34' stroke='#c7d8dd' stroke-width='2' />",
        "<line x1='16' y1='38' x2='112' y2='10' stroke='#e5d8c4' stroke-width='2' />",
    ]
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}' role='img' aria-label='captcha'>"
        "<rect width='100%' height='100%' rx='10' fill='#f7f4ee' />"
        + ''.join(lines)
        + ''.join(chars)
        + "</svg>"
    )
