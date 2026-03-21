# SSHFerry Docs

[中文](README_zh.md) | **English**

This directory contains the maintained project documentation set. Files that were only historical notes, outdated migration plans, or duplicate assets have been removed so the remaining docs are easier to trust.

## Document Map

- 📘 [Frontend Build Guide](frontend/FRONTEND_BUILD.md)
- 🔌 [Frontend API Guide](frontend/FRONTEND_API.md)
- 🎨 [Frontend Design Guide](frontend/FRONTEND_DESIGN.md)
- 🛠️ [Backend Overview](backend/BACKEND_OVERVIEW.md)

- [传输规则对齐说明（中文）](backend/TRANSFER_RULES_zh.md)

## Recommended Reading Order

### For general contributors

1. Root [README.md](../README.md)
2. [Backend Overview](backend/BACKEND_OVERVIEW.md)

### For frontend work

1. [Frontend Build Guide](frontend/FRONTEND_BUILD.md)
2. [Frontend API Guide](frontend/FRONTEND_API.md)
3. [Frontend Design Guide](frontend/FRONTEND_DESIGN.md)

## Scope Rules

- Root `README.md` and `README_zh.md` are the product-facing entry points.
- `docs/` contains implementation-oriented reference material.
- API behavior should follow the current backend code first, then these docs.
- If a design note and current code disagree, code wins until the docs are updated.
