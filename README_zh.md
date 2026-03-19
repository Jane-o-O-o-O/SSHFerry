<p align="center">
  <img src="docs/assets/logo.png" alt="SSHFerry 标识" width="" />
</p>

# SSHFerry

中文 | [English](README.md)



SSHFerry 是一个面向多会话 SSH 文件传输场景的工作区，重点关注远端操作安全、任务过程可见，以及贴近日常使用的传输体验。

## 概览

- 🖥️ 桌面客户端：基于 Python + PySide6，目前仍是主要可运行应用
- 🧩 后端服务：基于 FastAPI，对外提供本地传输 API
- 🌐 前端应用：基于 React + Vite，正在持续接入中

## 亮点

- 🔒 基于 `remote_root` 的远端操作沙箱保护
- 📁 同时支持文件与文件夹的上传下载
- 🔁 支持断点续传与跳过逻辑的传输行为
- 🧪 内置 TCP / SSH / SFTP / 写入权限连接检查
- 📊 任务中心支持暂停、继续、取消、重试
- ⚡ 大文件自动启用并行分块传输
- 🪟 单窗口内支持多个远端 session
- 🔀 支持远端到远端拖拽复制

## 架构

### 🖥️ 桌面客户端

- 运行时：Python `3.11+`
- UI：`PySide6`
- 启动入口：`python -m src.app.main`

### 🧩 后端

- 运行时：Python `3.11+`
- 框架：`FastAPI` + `uvicorn`
- 启动入口：`python -m backend.app.main`

### 🌐 前端

- 运行时：Node.js
- 技术栈：`React` + `TypeScript` + `Vite`
- 开发服务器：在 `frontend/` 下执行 `npm run dev`

### 🚚 传输引擎

- `sftp`：默认传输引擎
- `parallel`：面向大文件的分块并行传输
- `scp`：手动协议覆盖时可选，偏向覆盖式行为

### 📌 任务状态

- `pending`
- `running`
- `paused`
- `done`
- `failed`
- `canceled`
- `skipped`

## 仓库结构

```text
src/        桌面应用、传输引擎、调度器、共享模型
backend/    FastAPI 后端服务
frontend/   React 前端
docs/       架构与迁移文档
tests/      Pytest 测试
tools/      构建与性能脚本
```

## 文档

- 📘 总览文档：[docs/README.md](docs/README.md)
- 🧱 前端构建说明：[docs/frontend/FRONTEND_BUILD.md](docs/frontend/FRONTEND_BUILD.md)
- 🔌 前端 API 说明：[docs/frontend/FRONTEND_API.md](docs/frontend/FRONTEND_API.md)
- 🛠️ 后端待办清单：[docs/backend/BACKEND_TODO.md](docs/backend/BACKEND_TODO.md)
- 🗂️ 历史架构记录：[docs/architecture/agent.md](docs/architecture/agent.md)

## 快速开始

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 运行桌面客户端

Windows：

```powershell
./run.bat
```

跨平台：

```bash
python -m src.app.main
```

### 3. 运行后端

```bash
python -m backend.app.main
```

可选环境变量：

- `SSHFERRY_BACKEND_HOST`
- `SSHFERRY_BACKEND_PORT`
- `SSHFERRY_ALLOWED_ORIGINS`
- `SSHFERRY_LOCAL_TOKEN`

### 4. 运行前端

```bash
cd frontend
npm install
npm run dev
```

构建：

```bash
cd frontend
npm install
npm run build
```

## 桌面端工作流

1. ➕ 手动添加站点，或从 SSH 命令快速导入。
2. 🧭 尽量将 `remote_root` 设为专用目录。
3. 🧪 先执行连接检查。
4. 🪟 打开一个或多个远端 session。
5. ⬆️⬇️ 上传或下载文件、文件夹。
6. 🔀 在远端面板之间拖拽，创建远端到远端传输。
7. 📊 在任务中心中查看并控制任务进度。

说明：

- 站点默认协议可为 `sftp` 或 `scp`
- 窗口级协议覆盖可强制使用 `Auto / SFTP / SCP`
- 若 `remote_root` 为空，会自动回退到 `/`

## 验证

运行测试：

```bash
pytest -q
```

快速导入检查：

```bash
python -c "from src.shared.models import SiteConfig, Task; from src.core.scheduler import TaskScheduler; from src.services.connection_checker import ConnectionChecker; print('imports_ok')"
```

## 打包

当前 Windows 打包主要面向 PySide6 桌面客户端。

构建：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -VenvPath .venv_compat
```

先做 Debug 构建：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -Clean -Debug -VenvPath .venv_compat
```

Release 构建：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -Clean -VenvPath .venv_compat
```

包装脚本：

```bat
tools\build_windows.bat
```

输出：

```text
release/SSHFerry-<version>-windows/
release/SSHFerry-<version>-windows.zip
release/SSHFerry-<version>-windows.sha256
```

重要说明：

- 📦 发布时请分发整个目录或生成的 `.zip`，不要只发 `.exe`
- 🧱 打包使用 `onedir` 布局，以保证 Qt 运行时稳定
- 🚫 默认禁用 UPX

## 性能说明

- ⚡ 大文件在达到阈值后会自动切换到并行 SFTP
- 🎛️ 默认预设策略会根据传输方向自动调整
- 🧵 调度器并发度会按引擎类型分别控制

默认调度并发：

- `max_workers_total=3`
- `max_workers_sftp=3`
- `max_workers_scp=2`
- `max_workers_parallel=1`

可用环境变量：

- `SSHFERRY_MAX_WORKERS_TOTAL`
- `SSHFERRY_MAX_WORKERS_SFTP`
- `SSHFERRY_MAX_WORKERS_SCP`
- `SSHFERRY_MAX_WORKERS_PARALLEL`
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

性能脚本：

```bash
python tools/benchmark_transfer.py --site "<your-site-name>" --size-mb 512 --iterations 2
```

## 存储与安全

- 🔐 默认不持久化保存密码
- 💾 如果启用了密码保存，凭据会保存在当前机器本地
- 🧱 更安全的做法是使用最小权限账户，并限制 `remote_root`

站点存储路径：

- Windows：`%USERPROFILE%\AppData\Local\SSHFerry\sites.json`
- Linux / macOS：`~/.config/sshferry/sites.json`

## 当前状态

- ✅ PySide6 桌面客户端可用，仍是当前主要入口
- 🔌 FastAPI 后端已接入核心传输逻辑
- 🚧 React 前端已在仓库中并持续集成中

如果你现在就要开始实际使用或继续开发，建议把桌面端视为稳定入口，把前后端拆分架构视为下一阶段演进方向。
