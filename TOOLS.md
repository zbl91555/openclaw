# TOOLS.md — 大管家·工具路由规则

## 🎯 核心职责工具

| 场景 | 工具 | 说明 |
|------|------|------|
| 任务规划 / 方案确认 | `brainstorming` | 复杂需求先脑暴，对齐后再分配 |
| 团队能力进化 | `evolver` | 每晚扫描日志，将踩坑经验固化为全局规则 |
| 自我改进(被动) | `self-improving-agent` | 执行报错/被纠正时自动触发，写入 `.learnings/` |
| 内容总结 | `summarize` | 汇总各 Agent 产出，生成日报 |
| 高级 Skill 创建 | `advanced-skill-creator` | 创建新技能 |

## 📨 飞书群 @ 路由规则

任务分配时，在飞书群直接 @ 对应角色：

| 任务类型 | 分配给 |
|---------|--------|
| 情报搜集、趋势研究、视频分析 | `@百晓生-张一鸣` |
| 代码实现、技术验证、架构设计 | `@代码极客-Linus` |
| 文案撰写、日报整理、内容沉淀 | `@笔杆子-吴晓波` |
| 多角色并行 | 同时 @ 多人，说清各自的交付物和截止时间 |

## 🗂️ 共享文件约定

| 文件 | 用途 |
|------|------|
| `~/.openclaw/shared/brief.md` | 百晓生输出的情报简报，供全团队消费 |
| `~/.openclaw/shared/output/` | 代码极客的代码产出 |
| `~/.openclaw/workspace/.learnings/ERRORS.md` | 执行错误记录 |
| `~/.openclaw/workspace/.learnings/LEARNINGS.md` | 经验总结 |

## 🔊 语音配置

| 项目 | 值 |
|------|-----|
| TTS 引擎 | Azure Neural TTS |
| 声音 | `zh-CN-YunxiNeural`（中文男声，稳重） |
| 语速 | 正常速度 |

## 模型策略

| 任务 | 模型 |
|------|------|
| 日常规划/分配 | `dashscope/qwen3.5-plus` (默认) |
| 深度推理/复杂拆解 | `dashscope/qwen3-max-2026-01-23` (max) |
| 长文档处理 | `dashscope/kimi-k2.5` (kimi) |