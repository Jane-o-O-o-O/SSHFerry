# SSHFerry Backend Overview

[中文](BACKEND_OVERVIEW_zh.md) | **English**

## Purpose

This document describes the backend as it exists now: a local FastAPI service that exposes site management, file browsing, task creation, task control, and realtime task/log snapshots for the frontend.

## Entry Point

Run locally:

```bash
python -m backend.app.main
```

Default bind:

- Host: `127.0.0.1`
- Port: `18080`

## Main Responsibilities

- Manage saved site configurations
- Run connection checks
- Manage remote session contexts
- Expose local filesystem browsing APIs
- Expose remote filesystem browsing and operations APIs
- Create and control transfer tasks through `TaskScheduler`
- Stream task and log snapshots over websocket

## Backend Structure

```text
backend/app/
  main.py
  api/
    routes/
  schemas/
  services/
```

Key service modules:

- `app_state.py`
- `site_service.py`
- `connection_service.py`
- `local_file_service.py`
- `remote_file_service.py`
- `task_service.py`
- `log_service.py`

## Current API Surface

- Health and auth bootstrap
- Sites
- Connections and sessions
- Local files
- Remote files
- Tasks
- Logs
- Websocket snapshots for tasks and logs

## Relationship To Desktop Code

The backend reuses core transfer and scheduler logic from `src/` rather than reimplementing everything from scratch. The PySide6 desktop app is still a first-class client of the same product, not a deprecated legacy shell.

## Operational Notes

- The backend is local-first, not a remote hosted service.
- The auth token is meant for trusted local frontend bootstrapping.
- Remote operations still respect `remote_root` sandboxing rules.
- If behavior documentation drifts, backend route and service code are the final source of truth.

## Related Docs

- [Frontend Build Guide](../frontend/FRONTEND_BUILD.md)
- [Frontend API Guide](../frontend/FRONTEND_API.md)
