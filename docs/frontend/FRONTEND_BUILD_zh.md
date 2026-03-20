# SSHFerry 前端构建指南

**中文** | [English](FRONTEND_BUILD.md)

## 目的

这份文档用于固定当前前端开发基线，只回答实际问题：现在用什么技术、怎么启动、如何和后端对接、哪些约束需要保持稳定。

## 当前技术栈

- 框架：`React 18`
- 构建工具：`Vite 5`
- 语言：`TypeScript`
- 路由：`react-router-dom`
- 服务端状态：`@tanstack/react-query`
- 本地 UI 状态：`zustand`
- HTTP 客户端：`axios`

## 当前事实基线

- 前端代码目录：`frontend/`
- 后端入口：`python -m backend.app.main`
- 桌面端入口：`python -m src.app.main`

当前仍以桌面客户端为主产品形态。前端是并行推进中的实现，不是已经完成的正式替代品。

## 启动前端开发环境

```bash
cd frontend
npm install
npm run dev
```

## 构建前端

```bash
cd frontend
npm install
npm run build
```

构建输出：

```text
frontend/dist
```

## 前后端联调约定

做前端联调前，先本地启动后端：

```bash
python -m backend.app.main
```

推荐的前端初始化顺序：

1. `GET /api/health`
2. `GET /api/auth/session`
3. 保存返回的 token
4. 后续 REST 请求统一带 `X-SSHFerry-Token`
5. 需要实时能力时再建立 websocket 连接

## 建议的本地环境变量

只有在确实需要时再创建前端 env 文件。建议值：

```env
VITE_BACKEND_HTTP_URL=http://127.0.0.1:18080
VITE_BACKEND_WS_URL=ws://127.0.0.1:18080
```

## 实现边界

- 不要在组件里写死后端地址。
- 不要绕过本地后端直接访问文件系统或 SSH。
- 不要把产品降级成单远端面板的网页文件浏览器。
- 必须保留桌面版的多会话工作区模型。

## 相关文档

- [前端接口指南](FRONTEND_API_zh.md)
- [前端设计指南](FRONTEND_DESIGN_zh.md)
- [后端总览](../backend/BACKEND_OVERVIEW_zh.md)
