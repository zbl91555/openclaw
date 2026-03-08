# TOOLS.md - Main Routing

## Core Tools

| 场景 | 工具 | 说明 |
|------|------|------|
| 复杂需求对齐 | `brainstorming` | 先对齐再执行 |
| 汇总输出 | `summarize` | 压缩多方结果 |
| 系统演进 | `evolver` | 固化可复用规则 |
| 自我修正 | `self-improving-agent` | 记录错误和经验 |

## Routing

- 编码、调试、测试、重构、评审：派给 `swe`
- 搜集、分析、写作：派给 `research-writer`
- 直接发给 `swe` 或 `research-writer` 的任务默认抄收
- 只有出现阻塞、超时、跨域协作时，`main` 介入
- 禁止通过 `main` 让 `swe` 和 `research-writer` 直接互聊

## Session Rules

- 会话解析只使用 `agentId`
- 不使用展示名解析会话
- 默认 agent 是 `main`

## Shared Paths

| 路径 | 用途 |
|------|------|
| `~/.openclaw/workspace/.learnings/ERRORS.md` | 错误记录 |
| `~/.openclaw/workspace/.learnings/LEARNINGS.md` | 经验沉淀 |
| `~/.openclaw/workspace/research/` | 主工作区研究材料 |
| `~/.openclaw/workspace/research-writer/output/` | 研究写作产出 |
