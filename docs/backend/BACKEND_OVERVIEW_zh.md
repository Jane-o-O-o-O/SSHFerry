# SSHFerry 后端总览

**中文** | [English](BACKEND_OVERVIEW.md)

## 目的

这份文档说明当前真实存在的后端形态：一个本地 FastAPI 服务，为前端提供站点管理、文件浏览、任务创建、任务控制，以及任务和日志的实时快照能力。

## 启动入口

本地运行：

```bash
python -m backend.app.main
```

默认监听：

- Host：`127.0.0.1`
- Port：`18080`

## 核心职责

- 管理已保存的站点配置
- 执行连接检查
- 管理远端会话上下文
- 提供本地文件系统浏览接口
- 提供远端文件浏览与操作接口
- 通过 `TaskScheduler` 创建和控制传输任务
- 通过 websocket 推送任务与日志快照

## 后端结构

```text
backend/app/
  main.py
  api/
    routes/
  schemas/
  services/
```

关键服务模块：

- `app_state.py`
- `site_service.py`
- `connection_service.py`
- `local_file_service.py`
- `remote_file_service.py`
- `task_service.py`
- `log_service.py`

## 当前 API 能力范围

- 健康检查与本地鉴权初始化
- 站点管理
- 连接检查与会话管理
- 本地文件接口
- 远端文件接口
- 任务接口
- 日志接口
- 任务与日志 websocket 快照

## 与桌面端代码的关系

后端复用了 `src/` 里的核心调度与传输逻辑，而不是完全重写。PySide6 桌面客户端仍然是当前产品的一等入口，不是已经废弃的旧壳。

## 运行说明

- 后端是本地优先形态，不是远程部署服务。
- 本地 auth token 主要用于可信前端的初始化与访问控制。
- 远端操作仍然遵守 `remote_root` 沙箱规则。
- 如果文档描述与实现不一致，以后端路由和服务代码为准。

## 相关文档

- [前端构建指南](../frontend/FRONTEND_BUILD_zh.md)
- [前端接口指南](../frontend/FRONTEND_API_zh.md)
