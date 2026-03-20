# SSHFerry Frontend Build Guide

[中文](FRONTEND_BUILD_zh.md) | **English**

## Purpose

This guide defines the current frontend development baseline. It is intentionally practical: what exists now, how to run it, how it connects to the backend, and what should remain stable during ongoing integration.

## Current Stack

- Framework: `React 18`
- Build tool: `Vite 5`
- Language: `TypeScript`
- Router: `react-router-dom`
- Server state: `@tanstack/react-query`
- Local UI state: `zustand`
- HTTP client: `axios`

## Source Of Truth

- Frontend code: `frontend/`
- Backend entry: `python -m backend.app.main`
- Desktop entry: `python -m src.app.main`

The desktop client remains the main shipped experience. The frontend is an active parallel implementation, not yet a full replacement.

## Run Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Build Frontend

```bash
cd frontend
npm install
npm run build
```

Build output:

```text
frontend/dist
```

## Backend Contract For Frontend Work

Start the backend locally before frontend integration work:

```bash
python -m backend.app.main
```

Recommended frontend bootstrap order:

1. `GET /api/health`
2. `GET /api/auth/session`
3. Store the returned token
4. Add `X-SSHFerry-Token` to later REST requests
5. Connect to websocket streams if needed

## Suggested Local Environment

Create frontend env files only when needed. Suggested values:

```env
VITE_BACKEND_HTTP_URL=http://127.0.0.1:18080
VITE_BACKEND_WS_URL=ws://127.0.0.1:18080
```

## Implementation Boundaries

- Do not hardcode backend URLs inside components.
- Do not bypass the local backend for filesystem or SSH access.
- Do not reduce the product into a single-remote-pane web file browser.
- Preserve the multi-session workspace model from the desktop app.

## Related Docs

- [Frontend API Guide](FRONTEND_API.md)
- [Frontend Design Guide](FRONTEND_DESIGN.md)
- [Backend Overview](../backend/BACKEND_OVERVIEW.md)
