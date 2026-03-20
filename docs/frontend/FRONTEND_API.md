# SSHFerry Frontend API Guide

[中文](FRONTEND_API_zh.md) | **English**

## Purpose

This is the frontend-facing API summary for the current local FastAPI backend. It documents the route groups that matter in practice and the authentication/bootstrap rules that frontend code should follow.

Base prefix:

```text
/api
```

## Runtime Baseline

- Backend default HTTP URL: `http://127.0.0.1:18080`
- Backend default WS URL: `ws://127.0.0.1:18080`
- Auth header: `X-SSHFerry-Token`

## Bootstrap Sequence

1. `GET /api/health`
2. `GET /api/auth/session`
3. Store the returned token
4. Add `X-SSHFerry-Token` to later API calls
5. Connect to websocket endpoints if needed

## Route Groups

### Health And Auth

- `GET /api/health`
- `GET /api/auth/session`

### Sites

- `GET /api/sites`
- `POST /api/sites`
- `PUT /api/sites/{site_name}`
- `DELETE /api/sites/{site_name}`

### Connections And Sessions

- `POST /api/connections/check`
- `GET /api/sessions`
- `POST /api/sessions/open`
- `POST /api/sessions/close`

### Local Files

- `GET /api/local-files/drives`
- `GET /api/local-files/list?path=...`
- `GET /api/local-files/stat?path=...`

### Remote Files

- `GET /api/remote-files/list?session_id=...&path=...`
- `GET /api/remote-files/stat?session_id=...&path=...`
- `POST /api/remote-files/mkdir`
- `POST /api/remote-files/rename`
- `POST /api/remote-files/delete`

### Tasks

- `GET /api/tasks`
- `POST /api/tasks/upload`
- `POST /api/tasks/download`
- `POST /api/tasks/remote-copy`
- `POST /api/tasks/{task_id}/pause`
- `POST /api/tasks/{task_id}/resume`
- `POST /api/tasks/{task_id}/cancel`
- `POST /api/tasks/{task_id}/restart`
- `DELETE /api/tasks/finished`

### Logs

- `GET /api/logs`
- `DELETE /api/logs`

### WebSocket

- `GET ws://127.0.0.1:18080/api/ws/tasks?token=...`
- `GET ws://127.0.0.1:18080/api/ws/logs?token=...`

## Response Conventions

- Standard REST success codes: `200`, `201`, `204`
- Error payloads follow FastAPI `{"detail": ...}` patterns for REST routes
- Task websocket currently sends full `task_snapshot` payloads, not fine-grained task events
- Log websocket currently sends `log_snapshot` payloads

## Important Frontend Rules

- Treat backend code as the final source of truth if docs drift.
- Do not assume a richer task event model than the current snapshot stream.
- Do not assume remote session IDs survive backend restarts.
- Do not bypass backend auth bootstrap even in local development.

## Related Docs

- [Frontend Build Guide](FRONTEND_BUILD.md)
- [Frontend Design Guide](FRONTEND_DESIGN.md)
- [Backend Overview](../backend/BACKEND_OVERVIEW.md)
