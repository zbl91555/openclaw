---
name: gemini-cli
description: Google Gemini CLI Headless 模式自动化。通过 -p 传入 prompt、管道输入文件内容、JSON 结构化输出，供脚本/Agent 调用。不支持交互式命令（/、@、!）。
when: "当用户需要用 Gemini CLI 完成代码分析、文档处理、自动化脚本或任何 AI 辅助任务时触发。"
examples:
  - "gemini 帮我写一个快排"
  - "用 gemini 分析这个文件的安全漏洞"
  - "cat README.md | gemini -p '翻译成英文'"
  - "gemini 帮我生成 git commit message"
metadata:
  openclaw:
    emoji: "♊️"
    requires:
      bins: ["gemini", "bash"]
---

# Gemini CLI — Headless 执行指南

> ⚠️ 只能使用 Headless 模式（`-p` 参数或 stdin 管道）。
> 交互式命令（`/model`、`@文件`、`!shell` 等）仅在人工终端 session 中有效，脚本不可用。

## 环境

```bash
# 默认通过 Google 账号 OAuth 登录，无需 API Key
# 首次运行 `gemini` 会自动引导完成登录

# 可选：预设默认模型（开启 previewFeatures 后 Gemini 3 可用）
export GEMINI_MODEL="gemini-3-flash-preview"
```

## 核心调用

```bash
# 直接提问
gemini -p "问题"

# 管道输入（最常用）
cat file.py | gemini -p "审查安全漏洞"

# JSON 输出（Agent 解析推荐）
cat file.py | gemini -p "..." --output-format json | jq -r '.response'

# 流式 JSON（监控长任务，返回 JSONL）
gemini -p "..." --output-format stream-json
```

## 子命令

```bash
gemini mcp                  # 管理 MCP 服务器
gemini extensions <cmd>     # 管理扩展
gemini skills <cmd>         # 管理 Agent Skills
gemini hooks <cmd>          # 管理 Hooks
```

## 关键参数

| 参数 | 说明 |
|------|------|
| `-p / --prompt` | Headless 模式，传递提示词 |
| `-m / --model` | 指定模型 |
| `-o / --output-format` | `text` / `json` / `stream-json` |
| `--raw-output` | 禁用输出净化，获取原始文本（管道处理时用） |
| `-s / --sandbox` | 启用沙箱隔离 |
| `--approval-mode` | `auto_edit`（自动接受编辑）/ `yolo`（全自动）/ `plan`（只读规划） |
| `--allowed-tools` | 指定无需确认直接运行的工具 |
| `--allowed-mcp-server-names` | 限定允许使用的 MCP 服务器 |
| `-r / --resume` | 恢复上次 session（`latest` 或序号，如 `--resume 5`） |
| `--list-sessions` | 列出当前项目所有可用 session |
| `--delete-session` | 按序号删除 session |
| `--include-directories` | 额外包含目录（逗号分隔） |
| `-d / --debug` | 调试模式 |

## 模型策略（Gemini 3 优先，不可用时降级）

```bash
# Gemini 3 需开启 previewFeatures: true
gemini -m gemini-3-flash-preview -p "..." 2>/dev/null \
  || gemini -m gemini-2.5-flash -p "..."

# 复杂推理用 Pro
gemini -m gemini-3-pro-preview -p "..." 2>/dev/null \
  || gemini -m gemini-2.5-pro -p "..."
```

| 模型 | 用途 |
|------|------|
| `gemini-3-flash-preview` | 首选，速度快，大多数任务 |
| `gemini-3-pro-preview` | 复杂推理、多步骤规划 |
| `gemini-2.5-flash` | Gemini 3 不可用时的快速备选 |
| `gemini-2.5-pro` | Gemini 3 不可用时的强推理备选 |

## GEMINI.md — 项目上下文注入

每次调用时自动加载，无需在 prompt 里重复背景信息。

```
~/.gemini/GEMINI.md        # 全局（所有项目）
<项目根>/GEMINI.md         # 项目级
<子目录>/GEMINI.md         # 模块级
```

```bash
# 快速生成项目上下文文件
(cat package.json && ls src/) | gemini -p "生成 GEMINI.md：项目说明、技术栈、编码规范" > GEMINI.md
```

## 常见场景速查

```bash
# 代码审查
cat src/auth.py | gemini -p "安全审查：漏洞、最佳实践" | --output-format json | jq -r '.response'

# Commit message
git diff --cached | gemini -p "生成 Conventional Commits 风格的提交消息"

# PR 描述
git diff main...HEAD | gemini -p "生成 PR 描述：变更摘要、测试点、影响范围"

# 添加注释
cat src/api.ts | gemini -p "为所有函数添加 JSDoc 注释"

# 生成单元测试
cat src/utils.js | gemini -p "生成完整的 Jest 单元测试，含边界用例"

# 翻译文档
cat README.md | gemini -p "翻译为中文，保持 Markdown 格式" > README_CN.md

# 日志分析
tail -1000 /var/log/app.log | gemini -p "统计错误类型，给出修复优先级"

# 批量处理
for f in src/*.py; do
  cat "$f" | gemini -p "找出潜在 bug" --output-format json \
    | jq -r '.response' > "reports/$(basename $f).md"
done

# 生成 Dockerfile
cat package.json | gemini -p "生成生产级多阶段 Dockerfile"

# 生成 GitHub Actions CI
gemini -p "生成 GitHub Actions CI：Node.js，含 lint/test/build/docker push"
```

## settings.json 关键配置

```json
// ~/.gemini/settings.json
{
  "general": { "previewFeatures": true },   // 解锁 Gemini 3 模型
  "context": { "fileName": ["GEMINI.md"] },
  "tools": { "autoAccept": false }
}
```
