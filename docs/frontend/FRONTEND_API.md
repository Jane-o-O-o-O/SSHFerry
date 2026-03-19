# SSHFerry Frontend API Guide

## Scope
This document defines the current frontend integration baseline for SSHFerry Phase 1.
The deployed-web main path is now:

- formal login and auth cookies
- upload workspace instead of browsing the user's local disk
- protected routes
- refresh-once handling for `401`
- websocket auth via the same login session

Source of truth:

- backend route modules under `backend/app/api/routes/`
- backend schemas under `backend/app/schemas/`
- frontend request/response types in `frontend/src/api/types.ts`

## Runtime Modes
Two runtime modes exist:

- `local-dev`: compatibility mode for local development
- `deployed-web`: deployment mode and the main Phase 1 target

The frontend must treat `deployed-web` as the primary product path.

## Startup Flow
The startup flow is fixed:

1. `GET /api/health`
2. `GET /api/auth/me`
3. `200` => authenticated, enter app
4. `401` => anonymous, redirect to `/login`
5. business `401` => `POST /api/auth/refresh` once, retry once, then redirect to `/login`

The frontend must not depend on `GET /api/auth/session` as the deployed-web startup path.

## Health
`GET /api/health` returns core startup status plus deployment fields.
Important fields:

- `ready`
- `startup_error`
- `runtime_mode`
- `auth_mode`
- `access_cookie_name`
- `refresh_cookie_name`
- `workspace_root`

The frontend should only use `workspace_root` for diagnostics. It is not a user-facing disk path.

## Auth Endpoints
Primary deployed-web auth endpoints:

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

Current login request body:

```json
{
  "username": "owner",
  "password": "your-password"
}
```

Current user response fields:

- `id`
- `username`
- `display_name`
- `role`
- `auth_scheme`
- `session_id`
- `session_expires_at`

Current Phase 1 role delivery is `owner`, but the response shape already reserves `role` for `owner / operator / viewer`.

### Local-Dev Compatibility
`GET /api/auth/session` still exists for local-dev compatibility.
It should not be used as the deployed-web main path.

## Workspace API
The deployed-web middle pane now uses the server-side upload workspace.
All workspace paths are virtual user-relative paths such as `/`, `/uploads/a.txt`, `/releases/build/app.tar`.

Implemented endpoints:

### `GET /api/workspace/items?path=...`
List workspace directory entries.
If `path` is omitted, the backend lists `/`.

Response fields:

- `current_path`
- `parent_path`
- `items`
- `total`

Each entry returns:

- `name`
- `path`
- `is_dir`
- `size`
- `mtime`
- `exists`

### `GET /api/workspace/items/stat?path=...`
Return metadata plus aggregate directory statistics.

Response fields:

- `entry`
- `file_count`
- `dir_count`
- `total_size`

### `POST /api/workspace/uploads`
Browser upload endpoint.
Uses `multipart/form-data` with:

- `target_path`
- repeated `files`
- repeated `relative_paths`

This supports both file uploads and folder uploads with relative path restoration.

### `DELETE /api/workspace/items`
Delete workspace items.
Current request body:

```json
{
  "paths": ["/uploads/a.txt"]
}
```

The backend forbids deleting the workspace root `/`.

## Core Business API Families
Existing non-auth business families remain active:

- `GET /api/sites`
- `POST /api/sites`
- `PUT /api/sites/{site_name}`
- `DELETE /api/sites/{site_name}`
- `POST /api/connections/check`
- `GET /api/sessions`
- `POST /api/sessions/open`
- `POST /api/sessions/close`
- `GET /api/remote-files/list`
- `POST /api/remote-files/mkdir`
- `POST /api/remote-files/rename`
- `POST /api/remote-files/delete`

## Task API
Task list:

- `GET /api/tasks`
- `POST /api/tasks/upload-from-workspace`
- `POST /api/tasks/download-to-workspace`
- `POST /api/tasks/remote-copy`
- `POST /api/tasks/{task_id}/pause`
- `POST /api/tasks/{task_id}/resume`
- `POST /api/tasks/{task_id}/cancel`
- `POST /api/tasks/{task_id}/restart`
- `DELETE /api/tasks/finished`

Current deployed-web task request shapes:

### Upload From Workspace
```json
{
  "session_id": "dst-session",
  "workspace_path": "/uploads/a.txt",
  "remote_path": "/root/autodl-tmp/a.txt",
  "engine": "auto"
}
```

### Download To Workspace
```json
{
  "session_id": "src-session",
  "remote_path": "/root/autodl-tmp/a.txt",
  "workspace_path": "/downloads/a.txt",
  "engine": "auto"
}
```

### Remote Copy
```json
{
  "src_session_id": "src-session",
  "dst_session_id": "dst-session",
  "src_path": "/root/autodl-tmp/a.txt",
  "dst_path": "/root/autodl-tmp-copy/a.txt",
  "engine": "auto"
}
```

Task response conventions:

- `src_endpoint_type` and `dst_endpoint_type` may now be `workspace` or `remote`
- `src` and `dst` use virtual workspace paths when the source or target is the upload workspace
- `src_label` and `dst_label` are already UI-ready labels
- folder tasks use `subtask_count`, `subtask_done`, and `current_file`

## WebSocket
Primary task socket:

- `GET /api/ws/tasks`

Deployed-web auth behavior:

- same-origin websocket reuses auth cookies
- do not append long-lived auth tokens to the query string as the main path

Legacy raw log socket still exists:

- `GET /api/ws/logs`

This is still an implementation-oriented channel, not the final product activity feed.

## Legacy Compatibility
The following endpoints still exist for local-dev or compatibility, but deployed-web frontend code should not depend on them:

- `GET /api/auth/session`
- `/api/local-files/*`
- `POST /api/tasks/upload`
- `POST /api/tasks/download`

## Validation
Current validation commands used with this baseline:

- `python -m pytest tests/test_backend_workspace.py tests/test_backend_tasks.py tests/test_backend_auth.py tests/test_backend_health.py tests/test_backend_ws.py`
- `npm.cmd run build`