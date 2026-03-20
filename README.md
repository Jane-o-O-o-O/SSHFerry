<p align="center">
  <img src="docs/assets/logo.png" alt="SSHFerry logo" width="220" />
</p>

<h1 align="center">SSHFerry</h1>

<p align="center">
  Multi-session SSH file transfer workspace for safe daily remote operations
</p>

<p align="center">
  <a href="README_zh.md">中文</a> | <strong>English</strong>
</p>

## Overview

SSHFerry is built for practical SSH file work: upload, download, remote-to-remote copy, visible task control, and safer operation boundaries through `remote_root` sandboxing.

## At A Glance

- 🖥️ Desktop client: Python + PySide6, the current primary product
- 🧩 Backend service: FastAPI local API layer
- 🌐 Frontend app: React + Vite UI under active integration
- 🔒 Safety first: `remote_root` limits remote operations to allowed paths
- 📊 Task visibility: pause, resume, cancel, restart, skip-aware progress
- ⚡ Fast transfer: parallel engines for larger files
- 🪟 Multi-session workflow: multiple remote sites in one window
- 🔀 Remote-to-remote copy: drag between remote panels

## Current Status

- ✅ Desktop client is usable and is the recommended entry point today
- 🔌 Backend is available and wired into the transfer logic
- 🚧 Frontend is present in the repo and still being integrated

## Repository Layout

```text
src/        Desktop app, transfer engines, scheduler, services, shared models
backend/    FastAPI backend service
frontend/   React + Vite frontend
docs/       Project docs and architecture notes
tests/      Pytest suite
tools/      Build and benchmark scripts
```

## Requirements

- 🐍 Python `3.11+`
- 📦 Node.js `18+` for frontend development
- 💻 Windows, Linux, or macOS for desktop development

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 🖥️ Run the desktop client

Windows:

```powershell
./run.bat
```

Linux or macOS:

```bash
./run.sh
```

Direct module entry:

```bash
python -m src.app.main
```

### 🔌 Run the backend

```bash
python -m backend.app.main
```

Backend environment variables:

- `SSHFERRY_BACKEND_HOST` default: `127.0.0.1`
- `SSHFERRY_BACKEND_PORT` default: `18080`
- `SSHFERRY_ALLOWED_ORIGINS`
- `SSHFERRY_LOCAL_TOKEN`

### 🌐 Run the frontend

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

## Desktop Workflow

1. ➕ Add a site manually or import from an SSH command.
2. 🧭 Set `remote_root` to a dedicated directory when possible.
3. 🧪 Run the built-in connection checks.
4. 🪟 Open one or more remote sessions.
5. ⬆️⬇️ Upload, download, or drag items between remote panels.
6. 📊 Monitor and control transfers in the task center.

Notes:

- `sftp` and `scp` are supported as site-level defaults.
- A window-level override can force `Auto`, `SFTP`, or `SCP`.
- If `remote_root` is empty, operations fall back to `/`.

## Transfer Engines

- 📁 `sftp`: default transfer engine
- ⚡ `parallel`: chunked transfer path for larger files
- 🧱 `scp`: manual overwrite-oriented alternative
- 🔀 Remote-to-remote transfers may use direct, relay, parallel bridge, or mixed directory strategies depending on file size and site capability

## Testing

Run the full suite:

```bash
pytest -q
```

Quick import check:

```bash
python -c "from src.shared.models import SiteConfig, Task; from src.core.scheduler import TaskScheduler; from src.services.connection_checker import ConnectionChecker; print('imports_ok')"
```

## Packaging

Windows packaging currently targets the desktop client.

Build:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -VenvPath .venv_compat
```

Debug build:

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

Expected output:

```text
release/SSHFerry-<version>-windows/
release/SSHFerry-<version>-windows.zip
release/SSHFerry-<version>-windows.sha256
```

Packaging notes:

- 📦 Publish the entire folder or generated `.zip`, not only the `.exe`
- 🧱 The build uses `onedir` layout for Qt runtime stability
- 🚫 UPX is disabled by default

## Performance Tuning

Default scheduler concurrency:

- `SSHFERRY_MAX_WORKERS_TOTAL=3`
- `SSHFERRY_MAX_WORKERS_SFTP=3`
- `SSHFERRY_MAX_WORKERS_SCP=2`
- `SSHFERRY_MAX_WORKERS_PARALLEL=1`

Common transfer tuning variables:

- `SSHFERRY_PARALLEL_THRESHOLD_BYTES`
- `SSHFERRY_PARALLEL_PRESET`
- `SSHFERRY_PARALLEL_UPLOAD_PRESET`
- `SSHFERRY_PARALLEL_DOWNLOAD_PRESET`
- `SSHFERRY_REMOTE_RELAY_DOWNLOAD_PRESET`
- `SSHFERRY_REMOTE_RELAY_UPLOAD_PRESET`
- `SSHFERRY_PARALLEL_WORKERS`
- `SSHFERRY_PARALLEL_CHUNK_BYTES`
- `SSHFERRY_PARALLEL_WARMUP_BATCH`
- `SSHFERRY_PARALLEL_WARMUP_DELAY`
- `SSHFERRY_PARALLEL_MAX_CHUNK_RETRIES`
- `SSHFERRY_STRICT_HOSTKEY`

Benchmark example:

```bash
python tools/benchmark_transfer.py --site "<your-site-name>" --size-mb 512 --iterations 2
```

## Storage And Safety

- 🔐 Passwords are not persisted by default
- 💾 If password saving is enabled, credentials are stored locally on the current machine
- 🛡️ Prefer least-privilege accounts and a non-root `remote_root`

Site store path:

- Windows: `%USERPROFILE%\AppData\Local\SSHFerry\sites.json`
- Linux and macOS: `~/.config/sshferry/sites.json`

## Documentation

- 📘 [docs/README.md](docs/README.md)
- 🧱 [docs/frontend/FRONTEND_BUILD.md](docs/frontend/FRONTEND_BUILD.md)
- 🔌 [docs/frontend/FRONTEND_API.md](docs/frontend/FRONTEND_API.md)
- 🛠️ [docs/backend/BACKEND_TODO.md](docs/backend/BACKEND_TODO.md)
- 🗂️ [docs/architecture/agent.md](docs/architecture/agent.md)
