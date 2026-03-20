# SSHFerry Frontend Design Guide

[中文](FRONTEND_DESIGN_zh.md) | **English**

## Design Goal

The frontend should preserve the product identity of SSHFerry as a practical desktop-style transfer workspace, not flatten it into a generic web file browser.

## Product Shape To Preserve

- Left area: site and session controls
- Middle area: local file browser
- Right area: multiple remote panes in parallel
- Bottom area: task center, with room for logs

This structure is more important than cosmetic modernization.

## Interaction Principles

- Make task status obvious.
- Keep file operations dense and efficient.
- Prefer explicit controls over hidden gestures.
- Treat drag-and-drop as a first-class workflow.
- Confirm destructive actions clearly.

## Visual Direction

- Style: industrial desktop tool, not SaaS dashboard
- Density: information-rich but readable
- Color: calm neutrals with strong status accents
- Typography: professional sans plus monospace for paths and IDs
- Motion: minimal, structural, and purposeful

## Required Capabilities In Phase 1

- Site management
- Quick import from basic SSH command forms
- Local file browsing
- Multiple remote sessions in one workspace
- Local-to-remote, remote-to-local, and remote-to-remote drag workflows
- Task center with live status and control actions

## Non-Goals For Phase 1

- Decorative landing-page visuals
- Single-pane remote-only file manager layout
- Heavy animation-first UI
- Advanced conflict-resolution wizards
- Full observability console replacing the task-first layout

## Design Review Checklist

- Can users still understand the "sites + local + multi-remote + tasks" structure immediately?
- Does the interface still feel optimized for repeated file transfer work?
- Are task failures and current transfer targets easy to inspect?
- Are destructive actions explicit and hard to trigger accidentally?

## Related Docs

- [Frontend Build Guide](FRONTEND_BUILD.md)
- [Frontend API Guide](FRONTEND_API.md)
