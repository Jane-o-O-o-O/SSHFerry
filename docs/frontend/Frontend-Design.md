# SSHFerry Frontend Design Specification

## Purpose
This document defines the current Phase 1 frontend product baseline.
The goal is not to build a generic SaaS dashboard.
The goal is to preserve SSHFerry's operator-style workspace while adapting it to deployed-web auth and the upload workspace model.

## Visual Direction
Keep the existing SSHFerry visual language:

- light neutral workspace feel
- strong panel structure
- practical operator UI, not marketing UI
- no Chakra UI look
- no generic SaaS login page style

Reference style sources in the codebase:

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/index.css`
- `frontend/src/pages/bootstrap/BootstrapPage.tsx`
- `frontend/src/components/layout/AppTopBar.tsx`

## Layout
The core workspace layout remains:

- left: sites and sessions
- middle: upload workspace panel or pinned remote pane
- right: additional remote panes
- bottom: task center

The middle panel is no longer a local disk browser in deployed-web mode.
It is the server-side upload workspace.

## Upload Workspace Panel
The upload workspace panel must preserve file-browser semantics.
It must include:

- path navigation
- parent navigation
- refresh
- upload files
- upload folder
- multi-select list
- summary metadata
- drag source for workspace -> remote
- drop target for remote -> workspace
- delete selected

Behavior rules:

- directory-first sorting
- path changes clear stale selection
- errors render inside the panel, not only in toast
- root `/` cannot be deleted

## Remote Workspace
The remote area must preserve the multi-session value of SSHFerry.
Required behavior:

- multiple open sessions at the same time
- per-pane refresh, close, path navigation, and selection
- clear stale-session state when backend session no longer exists
- remote -> remote transfer remains supported

## Task Center
Task UI must show:

- direction
- engine
- status
- progress
- speed
- current item
- failure details
- task actions: pause, resume, cancel, restart

Task labels must clearly show:

- `workspace -> remote`
- `remote -> workspace`
- `remote -> remote`

## Route and Guard Rules
Current route rules:

- `/` runs bootstrap checks
- `/login` is the only auth entry page
- `/workspace`, `/tasks`, and `/logs` are protected routes
- authenticated users reaching `/login` should be redirected back into the app

## Login Page
The login page must follow SSHFerry's existing visual language.
It should feel like an operator login entry, not a generic SaaS hero page.
Phase 1 login page scope is intentionally narrow:

- username
- password
- submit
- auth notice or session-expired notice
- login error feedback

Phase 1 does not include:

- signup
- OAuth2
- password reset
- email verification

## Session Expired UX
Session expiration UX is fixed:

- business request returns `401`
- frontend attempts refresh once
- if refresh succeeds, retry original request once
- if refresh fails, clear auth state and redirect to `/login`

## Logs
Raw logs are still available as an implementation channel, but they are not the final user-facing product direction.
The long-term design target is an activity feed with filtered, user-readable events.

## Phase 1 Non-Goals
Still out of scope:

- public registration
- multi-role permission matrix enforcement in UI
- browser download to user disk as a primary product path
- full activity feed replacement
- encrypted secret management UI

## Current Status
Current UI baseline already includes:

- `/login`
- protected routes
- upload workspace panel semantics
- workspace-based task creation
- top bar user display and logout
- 401 refresh flow