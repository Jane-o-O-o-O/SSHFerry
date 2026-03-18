# SSHFerry

[中文](README_zh.md) | English

SSHFerry is an SSH file transfer workspace focused on safe remote operations, practical transfer behavior, and clear task visibility.

Today the repository contains three layers:

- A working desktop client built with Python + PySide6
- A local FastAPI backend that exposes the core transfer logic as APIs
- A React + Vite frontend that is being integrated against that backend

The desktop client is still the primary runnable app. The backend and frontend are already in the repo and are intended for the next UI architecture.

## Highlights

- Sandbox-protected remote operations through `remote_root`
- Upload and download for files and folders
- Resume and skip-aware transfer behavior
- Built-in connection checking for TCP / SSH / SFTP / read-write access
- Task center with pause / resume / cancel / restart
- Parallel chunk transfer for large files
- Multiple remote sessions in one window
- Remote-to-remote copy by dragging between remote sessions

## Current Architecture

### Desktop client

- Runtime: Python `3.11+`
- UI: `PySide6`
- Entry point: `python -m src.app.main`

### Backend

- Runtime: Python `3.11+`
- Framework: `FastAPI` + `uvicorn`
- Entry point: `python -m backend.app.main`

### Frontend

- Runtime: Node.js
- Stack: `React` + `TypeScript` + `Vite`
- Dev server: `npm run dev` inside `frontend/`

### Transfer engines

- `sftp`: default transfer engine
- `parallel`: optimized chunked transfer for large files
- `scp`: manual protocol override with overwrite-oriented behavior

### Task states

- `pending`
- `running`
- `paused`
- `done`
- `failed`
- `canceled`
- `skipped`

## Repository Layout

```text
src/        Desktop app, transfer engines, scheduler, shared models
backend/    FastAPI backend service
frontend/   React frontend
docs/       Architecture and migration docs
tests/      Pytest suite
tools/      Build and benchmark scripts
```

## Documentation

- Overview docs: [docs/README.md](docs/README.md)
- Frontend build notes: [docs/frontend/FRONTEND_BUILD.md](docs/frontend/FRONTEND_BUILD.md)
- Frontend API notes: [docs/frontend/FRONTEND_API.md](docs/frontend/FRONTEND_API.md)
- Backend worklist: [docs/backend/BACKEND_TODO.md](docs/backend/BACKEND_TODO.md)
- Historical architecture notes: [docs/architecture/agent.md](docs/architecture/agent.md)

## Quick Start

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Run the desktop client

Windows:

```powershell
./run.bat
```

Cross-platform:

```bash
python -m src.app.main
```

### Run the backend

```bash
python -m backend.app.main
```

Optional environment variables:

- `SSHFERRY_BACKEND_HOST`
- `SSHFERRY_BACKEND_PORT`
- `SSHFERRY_ALLOWED_ORIGINS`
- `SSHFERRY_LOCAL_TOKEN`

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Build:

```bash
cd frontend
npm install
npm run build
```

## Desktop Usage

1. Add a site manually or paste an SSH command.
2. Set `remote_root` to a dedicated directory when possible.
3. Run the connection check.
4. Open one or more remote sessions.
5. Upload or download files and folders.
6. Drag between remote panels to create remote-to-remote tasks.
7. Watch and control work in the task center.

Notes:

- Site-level default protocol can be `sftp` or `scp`
- Main window task override can force `Auto / SFTP / SCP`
- If `remote_root` is empty, it defaults to `/`

## Verification

Run tests:

```bash
pytest -q
```

Quick import check:

```bash
python -c "from src.shared.models import SiteConfig, Task; from src.core.scheduler import TaskScheduler; from src.services.connection_checker import ConnectionChecker; print('imports_ok')"
```

## Packaging The Desktop App

Windows packaging is still aimed at the PySide6 desktop client.

Build:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -VenvPath .venv_compat
```

Debug build first:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -Clean -Debug -VenvPath .venv_compat
```

Release build:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -Clean -VenvPath .venv_compat
```

Wrapper:

```bat
tools\build_windows.bat
```

Output:

```text
release/SSHFerry-<version>-windows/
release/SSHFerry-<version>-windows.zip
release/SSHFerry-<version>-windows.sha256
```

Important notes:

- Publish the whole folder or the generated `.zip`, not only the `.exe`
- The build uses `onedir` layout for Qt runtime stability
- UPX is disabled by default

## Performance Notes

- Large files switch to parallel SFTP automatically once the threshold is reached
- Default preset policy is direction-aware:
  - upload: `medium`
  - download: `high`
- Default scheduler concurrency:
  - `max_workers_total=3`
  - `max_workers_sftp=3`
  - `max_workers_scp=2`
  - `max_workers_parallel=1`

Useful environment variables:

- `SSHFERRY_PARALLEL_WORKERS`
- `SSHFERRY_PARALLEL_CHUNK_BYTES`
- `SSHFERRY_PARALLEL_WARMUP_BATCH`
- `SSHFERRY_PARALLEL_WARMUP_DELAY`
- `SSHFERRY_PARALLEL_MAX_CHUNK_RETRIES`
- `SSHFERRY_STRICT_HOSTKEY`

Benchmark script:

```bash
python tools/benchmark_transfer.py --site "<your-site-name>" --size-mb 512 --iterations 2
```

## Storage And Safety

- Passwords are not persisted by default
- If `Save password to sites.json` is enabled for a password site, the password is stored locally on this machine
- Site store path:
  - Windows: `%USERPROFILE%\AppData\Local\SSHFerry\sites.json`
  - Linux / macOS: `~/.config/sshferry/sites.json`
- For safer operation, prefer least-privilege accounts and a non-root `remote_root`

## Current Status

The project is in a transition phase:

- The PySide6 desktop app is usable and still the main runnable product
- The FastAPI backend is already connected to the core transfer logic
- The React frontend is present and under active integration

If you are starting product work today, treat the desktop app as the stable entry point and the backend/frontend split as the next architecture being built out.
