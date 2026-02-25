# TOOLS.md — 代码极客·工具路由规则

## 💻 AI 编程 CLI 工具

| 工具 | 场景 | 命令 |
|------|------|------|
| **Claude Code** | 写文件、重构、复杂自动化 | `claude --dangerously-skip-permissions -p "..."` |
| **Gemini CLI** | 代码审查、建议、分析 | `gemini -p "审查这段代码"` |
| **Codex** | 批量任务、多文件改造 | `codex exec --full-auto "..."` |

## 🛠️ Skill 路由

| Skill | 触发时机 |
|-------|---------|
| `gemini-cli` | 代码 review、注释生成、commit 信息 |
| `ui-ux-pro-max` | 前端 UI 设计 → 实现 |
| `cloudflare-tunnel` | 内网穿透、暴露本地服务到公网 |
| `cliproxyapi` | 修改 AI 代理配置、添加模型 |
| `find` | 在文件系统中精确查找文件/内容 |

## 🔄 子 Agent 调度

```bash
# 并行启动前端子任务
bash pty:true workdir:~/project background:true \
  command:"claude --dangerously-skip-permissions -p '实现前端页面'"

# 并行启动后端子任务
bash pty:true workdir:~/project background:true \
  command:"claude --dangerously-skip-permissions -p '实现后端 API'"
```

## 📏 代码交付标准

每次交付前自动执行：
1. `gemini -p "review 这段代码，找出明显问题"` — 自动 review
2. 确认代码可在本地运行
3. 提供测试命令

## ⚠️ 禁止事项

- 禁止在 `~/.openclaw/` 目录下使用 coding-agent（可能破坏配置）
- 禁止在未确认的情况下做 `rm -rf` 等破坏性操作
