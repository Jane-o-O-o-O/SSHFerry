# SSHFerry Web Phase 1 Tasklist

## Scope
Phase 1 is split into five milestones:

1. deployment auth baseline
2. upload workspace backend
3. frontend workspace replacement
4. task model migration
5. activity feed direction

This file tracks the current repository status as of 2026-03-19.

## Milestone 1 - Deployment Auth Baseline
Status: mostly complete

Completed:

- runtime modes: `local-dev` and `deployed-web`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- access and refresh cookie baseline
- protected route flow
- websocket auth aligned to login session
- workspace root configuration
- owner bootstrap path
- health response deployment fields
- frontend bootstrap changed to `health -> me`
- refresh-once handling for `401`
- site passwords and key passphrases are encrypted at rest
- site update flow preserves stored password/passphrase when the field is left blank
- deployed-web requires `SSHFERRY_SITE_SECRET` for persisted site secret decryption
- backend routes now scope sites, sessions, remote file operations, and tasks to the current user
- raw logs are now owner-only as a transitional baseline before activity feed

Still pending:

- deployment-oriented CORS tightening
- fuller reverse-proxy deployment notes
- stronger startup-error coverage for every deployment misconfiguration

## Milestone 2 - Upload Workspace Backend
Status: minimum runnable chain complete

Completed:

- workspace schema and service
- per-user isolated workspace root mapping
- list endpoint
- stat endpoint
- multipart upload endpoint
- relative path restoration for folder uploads
- delete endpoint
- path escape protection
- backend tests for workspace flows

Still pending:

- explicit conflict policy for duplicate names
- stable error code catalog for upload and workspace failures
- quotas, size limits, and retention policy

## Milestone 3 - Frontend Workspace Replacement
Status: minimum runnable chain complete

Completed:

- middle panel wording switched to workspace semantics
- `/login` page added
- protected route guard added
- bootstrap page switched to login-session bootstrap semantics
- `frontend/src/api/workspace.ts` added
- workspace listing/stat/upload/delete wired to middle pane
- file upload button
- folder upload button
- directory browsing, parent navigation, refresh, select, delete
- summary line for file count, directory count, and total size
- workspace entries remain drag sources for remote upload tasks

Still pending:

- rename internal store fields away from `local*`
- drag browser files directly onto the workspace panel
- richer upload failure and edge-state UX

## Milestone 4 - Task Model Migration
Status: minimum runnable chain complete

Completed:

- `POST /api/tasks/upload-from-workspace`
- `POST /api/tasks/download-to-workspace`
- request body uses `workspace_path`
- scheduler still reuses current backend transfer engine
- task presentation maps server paths to `workspace` endpoint labels
- remote-copy capability preserved
- frontend queue creation switched to workspace task endpoints

Still pending:

- deeper verification for pause/resume/cancel/restart under every migrated path
- stronger UI-oriented error messages for task failures
- possible future move from `workspace_path` to durable workspace object ids

## Milestone 5 - Activity Feed
Status: not started

Still pending:

- activity event model
- user-readable activity stream
- raw log de-emphasis for normal users
- admin-only or dev-only raw log access strategy

## Recommended Next Steps
1. replace raw logs with activity feed
2. rename remaining `local*` frontend state to workspace-oriented names
3. add deployment hardening: limits, cleanup, and audit
4. add role-aware permission enforcement
5. finish ownership rules for future activity events and shared-resource scenarios