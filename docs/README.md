# SSHFerry Docs

这个目录用于放项目的分类文档，根目录只保留仓库入口文档。

## Structure

- `frontend/`
  - React 前端开发、联调、构建、交互设计和接口对接文档
- `backend/`
  - FastAPI 后端迁移、规划和实现说明
- `architecture/`
  - 架构说明、历史设计稿和参考性文档

## Current Docs

- [Frontend Build Guide](./frontend/FRONTEND_BUILD.md)
- [Frontend API Guide](./frontend/FRONTEND_API.md)
- [Frontend Design Specification](./frontend/Frontend-Design.md)
- [Backend TODO](./backend/BACKEND_TODO.md)
- [Web Deployment Plan](./architecture/WEB_DEPLOYMENT_PLAN.md)
- [Web Auth Login Module Plan](./architecture/AUTH_LOGIN_MODULE_PLAN.md)
- [Web Phase 1 Tasklist](./architecture/WEB_PHASE1_TASKLIST.md)
- [Historical Architecture Note](./architecture/agent.md)

## Frontend Reading Order

建议前端开发按这个顺序读：

1. [Frontend Build Guide](./frontend/FRONTEND_BUILD.md)
2. [Frontend API Guide](./frontend/FRONTEND_API.md)
3. [Frontend Design Specification](./frontend/Frontend-Design.md)

这样可以先确认工程约束，再确认接口契约，最后落具体交互和页面语义。

## Notes

- 仓库根目录保留 [README.md](../README.md) 和 `README_zh.md` 作为总入口。
- [docs/architecture/agent.md](./architecture/agent.md) 是历史设计文档，内容和当前实现可能不完全一致，阅读时以现有代码与最新迁移文档为准。
- [docs/architecture/WEB_DEPLOYMENT_PLAN.md](./architecture/WEB_DEPLOYMENT_PLAN.md) 记录的是面向部署到网页上的服务端工作台新方向，后续涉及上传工作区、双远端工作流和日志包装时，以这份计划为准。
- [docs/architecture/AUTH_LOGIN_MODULE_PLAN.md](./architecture/AUTH_LOGIN_MODULE_PLAN.md) 记录部署版登录与鉴权模块设计，并明确参考 full_stack_template 的认证逻辑但不复用其 UI 风格。
- [docs/architecture/WEB_PHASE1_TASKLIST.md](./architecture/WEB_PHASE1_TASKLIST.md) 是基于该计划继续拆出来的第一期执行清单，可直接用于排期和联调。







