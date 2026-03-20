<p align="center">
  <img src="docs/assets/logo.png" alt="SSHFerry 标识" width="220" />
</p>

<h1 align="center">SSHFerry</h1>

<p align="center">
  面向日常远程操作的多会话 SSH 文件传输工作区
</p>

<p align="center">
  <strong>中文</strong> | <a href="README.md">English</a>
</p>

## 项目概览

SSHFerry 面向真实的 SSH 文件处理场景，重点解决上传、下载、远端到远端复制、任务过程可见，以及通过 `remote_root` 提供更安全的操作边界。

## 快速了解

- 🖥️ 桌面客户端：基于 Python + PySide6，是当前主要产品形态
- 🧩 后端服务：基于 FastAPI 的本地 API 层
- 🌐 前端应用：基于 React + Vite，仍在持续集成中
- 🔒 安全边界：使用 `remote_root` 限制远程操作路径
- 📊 任务可视化：支持暂停、继续、取消、重试和跳过感知进度
- ⚡ 传输提速：大文件可使用并行传输引擎
- 🪟 多会话工作流：一个窗口可同时打开多个远端站点
- 🔀 远端互传：可在两个远端面板之间直接拖拽复制

## 当前状态

- ✅ 桌面客户端已可用，也是当前推荐的使用入口
- 🔌 后端已接入核心传输逻辑
- 🚧 前端已在仓库中，但仍处于持续集成阶段

## 仓库结构

```text
src/        桌面应用、传输引擎、调度器、服务层、共享模型
backend/    FastAPI 后端服务
frontend/   React + Vite 前端
docs/       项目文档与架构说明
tests/      Pytest 测试
tools/      构建与基准脚本
```

## 环境要求

- 🐍 Python `3.11+`
- 📦 Node.js `18+`，用于前端开发
- 💻 Windows、Linux 或 macOS，用于桌面端开发

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 🖥️ 运行桌面客户端

Windows：

```powershell
./run.bat
```

Linux 或 macOS：

```bash
./run.sh
```

直接模块启动：

```bash
python -m src.app.main
```

### 🔌 运行后端

```bash
python -m backend.app.main
```

后端环境变量：

- `SSHFERRY_BACKEND_HOST` 默认值：`127.0.0.1`
- `SSHFERRY_BACKEND_PORT` 默认值：`18080`
- `SSHFERRY_ALLOWED_ORIGINS`
- `SSHFERRY_LOCAL_TOKEN`

### 🌐 运行前端

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
2. 🧭 尽量将 `remote_root` 设置为专用目录。
3. 🧪 先执行内置连接检查。
4. 🪟 打开一个或多个远端会话。
5. ⬆️⬇️ 上传、下载，或在远端面板之间拖拽项目。
6. 📊 在任务中心查看并控制传输进度。

说明：

- 站点级默认协议支持 `sftp` 和 `scp`。
- 窗口级覆盖可以强制使用 `Auto`、`SFTP` 或 `SCP`。
- 如果 `remote_root` 为空，操作会回退到 `/`。

## 传输引擎

- 📁 `sftp`：默认传输引擎
- ⚡ `parallel`：面向大文件的分块并行传输路径
- 🧱 `scp`：偏向覆盖式行为的手动替代方案
- 🔀 远端到远端传输会根据文件规模和站点能力，自动选择 direct、relay、parallel bridge 或 mixed directory 策略

## 测试

运行完整测试：

```bash
pytest -q
```

快速导入检查：

```bash
python -c "from src.shared.models import SiteConfig, Task; from src.core.scheduler import TaskScheduler; from src.services.connection_checker import ConnectionChecker; print('imports_ok')"
```

## 打包

当前 Windows 打包主要面向桌面客户端。

构建：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows.ps1 -VenvPath .venv_compat
```

Debug 构建：

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

预期输出：

```text
release/SSHFerry-<version>-windows/
release/SSHFerry-<version>-windows.zip
release/SSHFerry-<version>-windows.sha256
```

打包说明：

- 📦 发布时请分发整个目录或生成的 `.zip`，不要只发 `.exe`
- 🧱 打包使用 `onedir` 布局，以保证 Qt 运行时稳定
- 🚫 默认禁用 UPX

## 性能调优

默认调度并发：

- `SSHFERRY_MAX_WORKERS_TOTAL=3`
- `SSHFERRY_MAX_WORKERS_SFTP=3`
- `SSHFERRY_MAX_WORKERS_SCP=2`
- `SSHFERRY_MAX_WORKERS_PARALLEL=1`

常用传输调优变量：

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

基准脚本示例：

```bash
python tools/benchmark_transfer.py --site "<your-site-name>" --size-mb 512 --iterations 2
```

## 存储与安全

- 🔐 默认不持久化保存密码
- 💾 如果启用了密码保存，凭据只会保存在当前机器本地
- 🛡️ 更安全的做法是使用最小权限账号，并限制 `remote_root`

站点存储路径：

- Windows：`%USERPROFILE%\AppData\Local\SSHFerry\sites.json`
- Linux 与 macOS：`~/.config/sshferry/sites.json`

## 文档

- 📘 [docs/README.md](docs/README.md)
- 🧱 [docs/frontend/FRONTEND_BUILD.md](docs/frontend/FRONTEND_BUILD.md)
- 🔌 [docs/frontend/FRONTEND_API.md](docs/frontend/FRONTEND_API.md)
- 🛠️ [docs/backend/BACKEND_TODO.md](docs/backend/BACKEND_TODO.md)
- 🗂️ [docs/architecture/agent.md](docs/architecture/agent.md)
