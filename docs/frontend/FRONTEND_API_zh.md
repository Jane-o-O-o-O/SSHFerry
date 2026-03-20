# SSHFerry 前端接口指南

**中文** | [English](FRONTEND_API.md)

## 目的

这份文档是当前本地 FastAPI 后端的前端接口摘要，重点说明真正需要用到的路由分组，以及前端必须遵守的鉴权与初始化规则。

统一前缀：

```text
/api
```

## 运行基线

- 后端默认 HTTP 地址：`http://127.0.0.1:18080`
- 后端默认 WS 地址：`ws://127.0.0.1:18080`
- 鉴权请求头：`X-SSHFerry-Token`

## 推荐初始化顺序

1. `GET /api/health`
2. `GET /api/auth/session`
3. 保存返回的 token
4. 后续 API 请求统一带 `X-SSHFerry-Token`
5. 需要实时能力时再连接 websocket

## 路由分组

### 健康检查与鉴权

- `GET /api/health`
- `GET /api/auth/session`

### 站点管理

- `GET /api/sites`
- `POST /api/sites`
- `PUT /api/sites/{site_name}`
- `DELETE /api/sites/{site_name}`

### 连接检查与会话

- `POST /api/connections/check`
- `GET /api/sessions`
- `POST /api/sessions/open`
- `POST /api/sessions/close`

### 本地文件

- `GET /api/local-files/drives`
- `GET /api/local-files/list?path=...`
- `GET /api/local-files/stat?path=...`

### 远端文件

- `GET /api/remote-files/list?session_id=...&path=...`
- `GET /api/remote-files/stat?session_id=...&path=...`
- `POST /api/remote-files/mkdir`
- `POST /api/remote-files/rename`
- `POST /api/remote-files/delete`

### 任务

- `GET /api/tasks`
- `POST /api/tasks/upload`
- `POST /api/tasks/download`
- `POST /api/tasks/remote-copy`
- `POST /api/tasks/{task_id}/pause`
- `POST /api/tasks/{task_id}/resume`
- `POST /api/tasks/{task_id}/cancel`
- `POST /api/tasks/{task_id}/restart`
- `DELETE /api/tasks/finished`

### 日志

- `GET /api/logs`
- `DELETE /api/logs`

### WebSocket

- `GET ws://127.0.0.1:18080/api/ws/tasks?token=...`
- `GET ws://127.0.0.1:18080/api/ws/logs?token=...`

## 响应约定

- 常规 REST 成功状态码：`200`、`201`、`204`
- REST 错误返回遵循 FastAPI `{"detail": ...}` 形式
- 当前任务 websocket 推送的是完整 `task_snapshot`，不是细粒度事件流
- 当前日志 websocket 推送的是 `log_snapshot`

## 前端实现注意事项

- 如果文档与后端代码不一致，以后端代码行为为准。
- 不要假设任务流已经支持更细的事件类型。
- 不要假设远端 `session_id` 在后端重启后仍然有效。
- 即使是本地开发，也不要跳过后端鉴权初始化步骤。

## 相关文档

- [前端构建指南](FRONTEND_BUILD_zh.md)
- [前端设计指南](FRONTEND_DESIGN_zh.md)
- [后端总览](../backend/BACKEND_OVERVIEW_zh.md)
