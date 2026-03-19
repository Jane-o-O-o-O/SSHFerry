# SSHFerry Frontend Build Guide

## Goal
This document defines the current frontend build and integration baseline for Phase 1.
The key change is that deployed-web no longer boots from a local token model.
It now boots from login session state plus the upload workspace.

## Stack
Keep the existing stack:

- React
- Vite
- TypeScript
- Zustand
- TanStack Query
- axios

## Startup Contract
The frontend bootstrap contract is:

1. `GET /api/health`
2. `GET /api/auth/me`
3. authenticated => app
4. anonymous => `/login`
5. request `401` => refresh once => retry once => `/login`

`GET /api/auth/session` is local-dev compatibility only.

## Providers and Hooks
Recommended flow:

1. `providers.tsx`
2. `useBackendSession.ts`
3. `useWorkspaceBootstrap.ts`
4. `useTaskSocket.ts`
5. page-level feature queries and mutations

`useWorkspaceBootstrap.ts` should no longer bootstrap from local drives in deployed-web mode.
It should prepare workspace path state for `/`.

## State Ownership
React Query should own:

- health and auth bootstrap queries
- sites and sessions
- workspace listing and workspace stat queries
- remote file listing queries
- mutations for login, logout, workspace upload/delete, sessions, remote file actions, and task creation

Zustand should own:

- auth status and current user
- protocol override
- selected site
- workspace pane layout and selection state
- remote pane selection state
- task socket status
- toasts, confirms, modal visibility

## HTTP Rules
The axios client should:

- use `baseURL` from `VITE_BACKEND_HTTP_URL`
- use `withCredentials=true`
- never persist access or refresh tokens in frontend state or storage
- centralize `401` handling
- refresh once on `401`
- redirect to `/login` if refresh fails

## WebSocket Rules
Task socket URL:

```text
ws://127.0.0.1:18080/api/ws/tasks
```

Rules:

- deployed-web reuses auth cookies
- local-dev compatibility may still keep token-based behavior, but that is not the main product path
- replace task store state from the latest `task_snapshot`
- fall back to polling only when needed

## Required UI Mapping
The current required structure is:

- left: sites and session control
- middle: upload workspace panel
- right: multi-remote workspace
- bottom: task center
- logs: owner-oriented raw log area only, until activity feed replaces it

## Upload Workspace Panel
The deployed-web middle panel must include:

- path input
- `..` to go to parent
- `Refresh`
- `Upload Files`
- `Upload Folder`
- multi-select list
- drag source behavior for workspace -> remote
- drop target behavior for remote -> workspace
- summary line for files, directories, and total size

The panel must not show drive pickers or user local disk semantics in deployed-web mode.

## Route Plan
Routes currently expected:

- `/` bootstrap page
- `/login` login page
- `/workspace` protected main workspace
- `/tasks` protected task page
- `/logs` protected owner-only raw logs page

## Local Development Checklist
Verify at least these points:

1. backend starts
2. `GET /api/health` works
3. `GET /api/auth/me` returns either current user or `401`
4. unauthenticated `/workspace` redirects to `/login`
5. login succeeds and enters the app
6. workspace list/stat/upload/delete all work
7. upload-from-workspace and download-to-workspace create tasks
8. task websocket receives snapshots

## Current Risks
Current remaining risks are not bootstrap-related anymore.
They are:

- workspace store names still use `local*` prefixes internally
- drag browser file directly into workspace panel is still pending
- activity feed has not replaced raw logs yet

Backend note:

- the frontend only receives `has_password` / `has_key_passphrase` flags for saved site secrets
- persisted site secrets are encrypted on the backend and are not exposed back to the browser

## Validation
Current frontend validation command:

```powershell
Set-Location frontend
npm.cmd run build
```