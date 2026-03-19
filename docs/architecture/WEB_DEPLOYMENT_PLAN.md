# SSHFerry Web Deployment Plan

## Background
SSHFerry originally assumed a local desktop-style flow:

- local backend
- local file panel
- local token bootstrap
- raw logs visible by default

The deployed-web direction changes that model.
The product is now defined as:

- browser-based access to SSHFerry
- formal login and auth baseline
- server-side upload workspace instead of browsing the user's disk
- multi-remote transfer workflow preserved
- raw logs no longer treated as a normal end-user feature

## Fixed Decisions
Current fixed Phase 1 decisions:

- no public signup
- no OAuth2
- no password reset
- no email verification
- auth baseline is `access token + refresh token + HttpOnly cookie`
- frontend startup path is `GET /api/health -> GET /api/auth/me`
- anonymous users must be redirected to `/login`
- websocket auth must reuse login session state
- middle panel must be the upload workspace in deployed-web mode
- roles must reserve `owner / operator / viewer`, but Phase 1 may ship only `owner`

## Current Completed Status
As of 2026-03-19, the repository already has a minimum runnable chain for Milestone 1 through Milestone 4.

Completed auth baseline:

- runtime modes
- `login / me / refresh / logout`
- cookie-based auth
- protected routes
- refresh-once handling for `401`
- websocket auth aligned with login cookies
- owner bootstrap path

Completed workspace baseline:

- `/api/workspace/items`
- `/api/workspace/items/stat`
- `POST /api/workspace/uploads`
- `DELETE /api/workspace/items`
- per-user workspace isolation
- folder upload relative path restoration

Completed task bridge baseline:

- `POST /api/tasks/upload-from-workspace`
- `POST /api/tasks/download-to-workspace`
- frontend queue creation switched to workspace task requests
- task labels mapped to `workspace -> remote` and `remote -> workspace`
- remote-copy remains available

Completed secret handling baseline:

- saved site passwords are encrypted at rest
- saved key passphrases are encrypted at rest
- deployed-web requires `SSHFERRY_SITE_SECRET` for decrypting persisted site secrets
- local-dev can fall back to an instance-local `.site_store.key` only for developer convenience
- site edit flow preserves an existing stored secret when the password/passphrase field is left blank

Completed ownership baseline:

- persisted sites are scoped by `owner_user_id`
- in-memory remote sessions are filtered by the current user
- task listing and task control are filtered by the current user
- raw logs are restricted to `owner` as a transitional baseline

## Current Phase 1 Transitional Choice
The current Phase 1 task bridge uses `workspace_path` as the minimum viable identifier.
That is acceptable for now.
If stronger object identity is needed later, the system can evolve to `workspace_item_id` without changing the product direction.

## Remaining Phase 1 Risks
Still pending:

- remaining ownership rules for future activity events and any later shared-resource model
- operator/viewer permission matrix
- activity feed replacing raw logs for normal users
- upload limits, cleanup policy, and audit strategy

## Recommended Order
1. replace raw logs with activity feed
2. harden deployment limits and cleanup rules
3. add role-aware permission enforcement
4. finish ownership rules for future events and shared resources
5. revisit durable workspace object ids only if path-based identity becomes insufficient