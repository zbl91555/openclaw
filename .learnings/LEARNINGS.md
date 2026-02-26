# LEARNINGS.md - 经验沉淀

> 由各 Agent 主动记录，大管家每晚用 `evolver` 提炼并写回全局 SOUL.md / TOOLS.md。

格式：
```
## [YYYY-MM-DD] 经验标题
**Agent：** [角色名]
**场景：** [什么情况下发现的]
**发现：** [具体经验/最佳实践]
**应用：** [如何在未来使用这个经验]
```

---

## [2026-02-26] agents_list 工具语义陷阱 ⚠️

**Agent：** 大管家 - 马云

**场景：** 用户问"你有什么 skill"和验证多 Agent 配置时

**发现：** 
- `agents_list` 工具返回的是**当前会话可 target 的 Agent allowlist**（用于 `sessions_spawn`）
- 不是已配置的 Agent 列表
- 正确的查看方式是 `openclaw agents list` 命令

**应用：** 
- 以后查询 Agent 配置状态，直接用 `openclaw agents list` 命令
- 不要依赖 `agents_list` 工具判断 Agent 是否配置
- 工具返回的信息可能是片面的，需要多角度验证

---
