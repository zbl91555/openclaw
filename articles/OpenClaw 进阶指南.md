# OpenClaw 进阶指南：高级用法与最佳实践

> **作者**：老弟  
> **时间**：2026 年 2 月  
> **前置知识**：已掌握 OpenClaw 基础架构和核心概念  
> **适合人群**：开发者、运维工程师、企业技术团队

---

## 目录

1. [多 Agent 协作与编排](#1-多-agent-协作与编排)
2. [自定义工具开发](#2-自定义工具开发)
3. [高级记忆管理技巧](#3-高级记忆管理技巧)
4. [性能优化](#4-性能优化)
5. [复杂工作流设计](#5-复杂工作流设计)
6. [与外部系统集成](#6-与外部系统集成)
7. [监控与可观测性](#7-监控与可观测性)
8. [生产环境部署方案](#8-生产环境部署方案)

---

## 1. 多 Agent 协作与编排

### 1.1 三种协作模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **并行子 Agent** | 同时处理多个独立任务 | 批量数据处理、多文件分析 |
| **主从架构** | 主 Agent 规划，子 Agent 执行 | 复杂项目分解、多步骤任务 |
| **角色分离** | 按职责分配权限 | 企业环境、安全隔离需求 |

---

### 1.2 并行子 Agent 配置

```json
{
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8,
        "timeout": 300
      }
    }
  }
}
```

**实战场景**：
```
用户请求："分析这个 GitHub 项目的代码质量"
→ 主 Agent 分解任务
  → 子 Agent A：拉取代码 + 分析结构
  → 子 Agent B：检查 Issues + PRs
  → 子 Agent C：扫描安全漏洞
  → 子 Agent D：生成测试覆盖率报告
→ 主 Agent 汇总 → 返回用户
```

---

### 1.3 主从架构示例

```yaml
# workflow.lobster
name: "Project Analysis Pipeline"
steps:
  - run: spawn-agent --role "code-analyzer"
  - run: spawn-agent --role "security-scanner"
  - run: spawn-agent --role "doc-generator"
  - wait: all
  - run: merge-results
  - run: generate-report
```

---

### 1.4 角色分离配置

```json
{
  "agents": {
    "developer": {
      "tools": ["read", "write", "exec", "bash"],
      "sandbox": { "mode": "all", "scope": "session" },
      "budget": { "daily": 5.00 }
    },
    "email-handler": {
      "tools": ["read", "web_fetch"],
      "sandbox": { "mode": "all", "network": false },
      "budget": { "daily": 1.00 }
    },
    "data-analyst": {
      "tools": ["read", "write"],
      "sandbox": { "mode": "non-main" },
      "budget": { "daily": 2.00 }
    }
  }
}
```



---

## 1.5 社区实战案例

OpenClaw 社区中多 Agent 协作已从概念走向生产实践。以下是真实案例整理：

### 案例 1：多实例开发协调员（"Patch"监督者）

**场景**：开发者通过 Telegram 协调 5-20 个并行 Coding Agent

**架构图**：
```
用户（Telegram）
    ↓
Patch（Manager Agent）
    ↓
┌───────┬───────┬───────┬───────┐
│Worker1│Worker2│Worker3│ ...   │
│(SSH)  │(SSH)  │(SSH)  │       │
└───────┴───────┴───────┴───────┘
```

**工作流程**：
1. 用户手机发送高级指令："修复登录页面的 bug"
2. Patch 接收并拆解任务
3. 通过 SSH 在 tmux 启动多个 Claude Code 实例
4. 分配代码编写任务
5. Worker 完成后返回结果
6. Patch 审查输出 + 运行测试 + 合并代码
7. 返回用户

**配置示例**：
```json
{
  "agents": {
    "patch-manager": {
      "channels": ["telegram"],
      "tools": ["sessions_spawn", "bash", "ssh"],
      "subagents": {
        "maxConcurrent": 20,
        "timeout": 600
      }
    }
  }
}
```

**优势**：
- ✅ 手机即可完成复杂开发任务
- ✅ 并行处理，效率提升 5-10 倍
- ✅ 自动测试 + 审查，质量保证

---

### 案例 2：Reddit 自动增长引擎（3-Agent 委员会）

**场景**：100% 自动化社交媒体运营，4 小时构建完成

**角色分配**：

| Agent | 职责 | 特殊技能 |
|-------|------|---------|
| **增长引擎** | Reddit/Twitter 互动 | AppleScript 控制真实 Chrome |
| **创业导师** | 提供专业知识 | 播客转录文本 RAG 知识库 |
| **质量网关** | 内容评分与审核 | 基于 `content-quality-gate.md` |

**工作流程**：
```
1. 增长引擎：搜集热门话题 → 起草内容
                    ↓
2. 创业导师：@唤醒 → 提供专业素材
                    ↓
3. 质量网关：评分（满分 50）
        ↓
    ≥40 分？───→ 发布
        ↓
    <40 分？───→ 打回重写
```

**质量网关配置**：
```markdown
# content-quality-gate.md

## 评分标准（满分 50 分）
- 内容相关性：/10
- 专业深度：/10
- 可读性：/10
- 行动号召力：/10
- 品牌一致性：/10

## 阈值
- ≥40 分：自动发布
- 30-39 分：人工审核
- <30 分：打回重写
```

**优势**：
- ✅ 零代码配置（Markdown 文件）
- ✅ 质量保证自动化
- ✅ 专业知识即时调用

---

### 案例 3：多线程市场调研（并行子 Agent）

**场景**：同时研究 3 个竞争对手的定价策略

**工作流程**：
```
用户："研究这 3 个竞争对手并总结定价策略"
    ↓
主 Agent 分解任务
    ↓
┌────────────┬────────────┬────────────┐
│子 Agent A  │子 Agent B  │子 Agent C  │
│竞争对手 1   │竞争对手 2   │竞争对手 3   │
└────────────┴────────────┴────────────┘
    ↓            ↓            ↓
    └────────────┴────────────┘
              ↓
        结果合并 + 综合分析
              ↓
          返回用户
```

**工具调用示例**：
```json
{
  "tool_name": "sessions_spawn",
  "parameters": {
    "agentId": "market-researcher",
    "prompt": "研究竞争对手 X 的定价策略，返回详细报告",
    "timeoutMs": 300000
  }
}
```

**配置示例**：
```json
{
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8,
        "timeout": 300000
      }
    }
  }
}
```

---

### 案例 4：Clawe 开源多 Agent 协调框架

**场景**：模拟真实数字营销团队

**角色分配**：
- 📝 **内容编辑**：撰写博客草稿
- 🔍 **SEO 专家**：关键词优化
- 🎨 **设计师**：配图建议

**协作方式**：
```
内容编辑 → 写完草稿 → clawe deliver
                              ↓
                    共享后端存储任务
                              ↓
                    SEO Agent @mentions 通知
                              ↓
                    审查 + 优化建议
                              ↓
                    返回内容编辑
```

**命令行交互**：
```bash
# 提交任务
clawe deliver content-editor --task "写一篇关于 AI 趋势的文章"

# 通知 SEO Agent 审查
clawe notify seo-expert --mention "@seo-expert 请审查 draft.md"

# 查看任务状态
clawe status
```

---

### 案例 5：自治软件开发团队（Virtual Company）

**场景**：构建完整落地页（Landing Page）

**完整流程**：

```
┌─────────────────────────────────────────────────────────┐
│ 步骤 1：需求下发与状态初始化                              │
│ 用户 Telegram 发送指令                                   │
│ → 主控 Agent 创建 STATE.yaml（共享状态文件）              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 2：异步子任务分发                                    │
│ 主控 Agent → sessions_spawn → Agent 1（研究员）           │
│ 任务：搜集现代落地页流行设计趋势                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 3：代码生成与协作                                    │
│ 研究员完成 → 主控 Agent → Agent 2（程序员）               │
│ 任务：读取调研结果 → 生成 HTML/CSS 文件                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 4：跨 Agent 审查与反馈                               │
│ Agent 3（审查员）接手                                    │
│ → 浏览器工具打开本地网页 → 语义快照截图                   │
│ → 分析 UI 对齐情况                                        │
│ → sessions_send → 程序员（静默通信）                      │
│    "div 标签未居中，请修复 src/index.html"                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤 5：交付与通知                                        │
│ 审查员验证通过 → 主控 Agent → Telegram 发送用户           │
│ "项目完成！预览链接：http://localhost:3000"              │
└─────────────────────────────────────────────────────────┘
```

**核心工具调用**：

**1. 生成并行子 Agent**：
```json
{
  "tool_name": "sessions_spawn",
  "parameters": {
    "agentId": "researcher",
    "prompt": "搜集现代落地页流行设计趋势",
    "timeoutMs": 300000
  }
}
```

**2. 跨 Agent 静默通信**：
```json
{
  "tool_name": "sessions_send",
  "parameters": {
    "targetSessionKey": "agent:coder:local:session-123",
    "message": "UI 审查发现 <div> 标签未居中，请修复 src/index.html",
    "announceStep": "ANNOUNCE_SKIP"
  }
}
```

**STATE.yaml 示例**：
```yaml
# STATE.yaml - 跨 Agent 共享状态
project: landing-page
status: in_progress
current_step: code_review
tasks:
  - id: 1
    name: market_research
    status: completed
    assigned_to: researcher
  - id: 2
    name: code_generation
    status: in_progress
    assigned_to: coder
  - id: 3
    name: ui_review
    status: pending
    assigned_to: reviewer
progress: 60%
```

---

## 1.6 社区最佳实践总结

### 1. 用文本和文件代替复杂编排代码

**核心理念**：
- ✅ `STATE.yaml` 共享状态
- ✅ `Tasks.md` 任务追踪
- ✅ `@mentions` 通知机制
- ✅ Markdown 配置文件

**优势**：
- 易读易修改
- 人类可参与
- 版本控制友好

---

### 2. 会话级工具是核心

| 工具 | 用途 | 示例 |
|------|------|------|
| `sessions_spawn` | 生成子 Agent | 并行调研、代码审查 |
| `sessions_send` | 跨会话通信 | Agent 间反馈、静默协作 |
| `sessions_history` | 获取历史 | 上下文同步 |

---

### 3. 异步协作工作流

```
人类 → Manager Agent → Worker Agents
          ↓                  ↓
      状态文件 ←─────────────┘
          ↓
      人类查看进度（随时）
```

**特点**：
- ✅ 人类无需实时在线
- ✅ Agent 自主决策
- ✅ 状态透明可追踪

---

### 4. 质量门控机制

**三层审核**：
```
生成 → 自检 → 互检 → 人工（可选）→ 发布
```

**配置示例**：
```yaml
quality_gates:
  self_review: true
  peer_review: true
  human_review_threshold: 0.8
```


---

## 2. 自定义工具开发

### 2.1 三种开发方式

| 方式 | 难度 | 适用场景 |
|------|------|---------|
| **SKILL.md** | ⭐ | 简单任务，自然语言指令 |
| **脚本工具** | ⭐⭐ | 需要编程逻辑（Python/Node.js） |
| **MCP Server** | ⭐⭐⭐ | 复杂系统集成，标准化接口 |

---

### 2.2 SKILL.md 示例

```markdown
---
name: github-pr-review
description: 自动审查 GitHub PR
triggers: ["PR 审查", "pr review", "代码审查"]
---

## 执行步骤
1. 调用 GitHub API 获取 PR diff
2. 检查代码规范（ESLint/Prettier）
3. 扫描安全隐患（硬编码密码、SQL 注入）
4. 生成审查报告
5. 通过 GitHub API 提交评论

## 输出格式
- ✅ 通过项
- ⚠️ 警告项
- ❌ 必须修复项
```

---

### 2.3 脚本工具示例（Python）

```python
#!/usr/bin/env python3
# skills/my-skill/scripts/review.py

import sys
import json

def review_code(diff):
    issues = []
    
    # 检查硬编码密码
    if "password" in diff.lower():
        issues.append("⚠️ 发现硬编码密码")
    
    # 检查 SQL 注入风险
    if "execute(" in diff and "+" in diff:
        issues.append("❌ 潜在 SQL 注入风险")
    
    return {"status": "reviewed", "issues": issues}

if __name__ == "__main__":
    diff = sys.stdin.read()
    result = review_code(diff)
    print(json.dumps(result))
```

---

### 2.4 MCP Server 示例（TypeScript）

```typescript
// my-mcp-server/index.ts
import { Server } from '@modelcontextprotocol/sdk/server';

const server = new Server({
  name: "my-db-connector",
  version: "1.0.0"
});

server.tool("query-db", async ({ sql }) => {
  const result = await db.query(sql);
  return { 
    content: [{ 
      type: "text", 
      text: JSON.stringify(result, null, 2) 
    }] 
  };
});

server.tool("list-tables", async () => {
  const tables = await db.query("SHOW TABLES");
  return { content: [{ type: "text", text: tables }] };
});

await server.connect();
```

**OpenClaw 配置**：
```json
{
  "mcp": {
    "servers": {
      "my-db": {
        "command": "node",
        "args": ["/path/to/my-mcp-server/index.js"]
      }
    }
  }
}
```

---

## 3. 高级记忆管理技巧

### 3.1 记忆类型与用途

| 类型 | 文件 | 用途 | 触发条件 |
|------|------|------|---------|
| **短期记忆** | `memory/YYYY-MM-DD.md` | 当天对话日志 | 自动追加 |
| **长期记忆** | `MEMORY.md` | 用户偏好、核心事实 | Pre-Compaction Flush |
| **项目记忆** | `projects/xxx/MEMORY.md` | 项目特定上下文 | 手动创建 |
| **技能记忆** | `skills/xxx/.memory/` | 技能执行历史 | 自动管理 |

---

### 3.2 手动记忆注入

**通过 API 写入**：
```bash
curl -X POST http://localhost:8080/api/memory \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fact",
    "content": "用户 prefers 中文回复",
    "tags": ["preference", "language"]
  }'
```

---

### 3.3 记忆标签分类

```markdown
# MEMORY.md

## [FACT] 用户偏好
- prefers 中文回复
- 工作时间：9:00-18:00
- 通知渠道：Telegram

## [SKILL] 项目上下文
- 项目 X 使用 Python + FastAPI
- 数据库：PostgreSQL 15
- 部署环境：Docker + K8s

## [HISTORY] 重要决策
- 2026-02-20：选择 Claude 3.5 作为主模型
- 2026-02-21：启用沙箱隔离
- 2026-02-22：配置 Heartbeat 任务
```

---

### 3.4 记忆检索优化

```json
{
  "memory": {
    "retrieval": {
      "topK": 10,
      "minScore": 0.7,
      "hybridWeight": 0.7,
      "recencyBoost": 0.2
    },
    "compaction": {
      "threshold": 0.8,
      "flushBeforeCompact": true
    }
  }
}
```

**参数说明**：
- `topK`: 返回多少条记忆
- `minScore`: 最低相似度阈值
- `hybridWeight`: 向量检索权重（0.7 = 70% 向量 + 30% 关键词）
- `recencyBoost`: 近期记忆加权

---

## 4. 性能优化

### 4.1 并发控制

```json
{
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      }
    }
  },
  "retry": {
    "maxAttempts": 3,
    "backoff": "exponential",
    "maxDelay": 30
  },
  "timeouts": {
    "toolCall": 60,
    "llmRequest": 120,
    "session": 3600
  }
}
```

---

### 4.2 智能模型路由

```json
{
  "models": {
    "routing": {
      "rules": [
        {
          "if": { "taskType": "heartbeat" },
          "use": "gpt-4o-mini"
        },
        {
          "if": { "taskType": "complex-planning" },
          "use": "claude-3-5-sonnet"
        },
        {
          "if": { "tokenBudget": "<1000" },
          "use": "gemini-flash-lite"
        },
        {
          "if": { "requiresCode": true },
          "use": "claude-3-5-sonnet"
        }
      ],
      "fallback": "qwen3.5-plus"
    }
  }
}
```

**成本对比**：
| 任务类型 | 推荐模型 | 成本/1K tokens |
|---------|---------|---------------|
| 心跳检查 | GPT-4o-mini | $0.00015 |
| 复杂规划 | Claude 3.5 Sonnet | $0.003 |
| 简单问答 | Gemini Flash Lite | $0.000075 |
| 代码生成 | Claude 3.5 Sonnet | $0.003 |

---

### 4.3 预算控制

```json
{
  "budgets": {
    "daily": 10.00,
    "perSession": 2.00,
    "perAgent": {
      "developer": 5.00,
      "email-handler": 1.00
    },
    "alertThreshold": 0.8,
    "alertWebhook": "https://hooks.slack.com/xxx",
    "hardLimit": true
  }
}
```

---

### 4.4 Token 优化技巧

**1. 渐进式上下文加载**：
```json
{
  "context": {
    "skills": {
      "loadOnDemand": true,
      "preloadTriggers": false
    }
  }
}
```

**2. 记忆摘要压缩**：
```json
{
  "memory": {
    "compaction": {
      "enabled": true,
      "model": "gpt-4o-mini",
      "preserveFacts": true
    }
  }
}
```

**3. 工具描述精简**：
```markdown
# ❌ 冗长
这个工具可以用来执行 bash 命令，比如 ls、cd、cat 等等...

# ✅ 精简
执行 bash 命令（ls、cd、cat 等）
```

---

## 5. 复杂工作流设计

### 5.1 Lobster 工作流引擎

**官方推荐的强类型工作流 Shell**

**基础示例**：
```yaml
# workflow.lobster
name: "Email Triage Pipeline"
version: "1.0"
steps:
  - run: fetch-emails --unread
  - run: llm-task --prompt "Categorize these emails"
  - needs_approval: true
  - run: send-replies --from-stdin
```

---

### 5.2 条件分支

```yaml
name: "PR Review Workflow"
steps:
  - run: fetch-pr-diff
  - run: llm-review
  - if: "risk_score > 0.8"
    then:
      - run: notify-security-team
      - needs_approval: true
  - else:
      - run: approve-pr
```

---

### 5.3 错误处理

```yaml
name: "Data Sync Workflow"
steps:
  - run: fetch-data
    retry: 3
    backoff: exponential
  - on_error:
      - run: notify-admin
      - run: fallback-to-cache
  - run: process-data
    timeout: 300
```

---

### 5.4 人工审批门

```yaml
name: "Production Deployment"
steps:
  - run: build-docker-image
  - run: run-tests
  - if: "tests_passed == false"
    then:
      - run: notify-dev-team
      - exit: 1
  - needs_approval:
      required: true
      approvers: ["admin1", "admin2"]
      timeout: 3600
  - run: deploy-to-prod
  - run: smoke-test
```

**审批流程**：
```
1. 工作流执行到 needs_approval
2. 系统暂停，生成 resumeToken
3. 审批人收到通知（Telegram/Slack/邮件）
4. 审批人点击链接确认
5. 工作流继续执行
```

---

## 6. 与外部系统集成

### 6.1 Webhooks 集成

**接收外部事件**：
```bash
# GitHub → OpenClaw
curl -X POST http://localhost:8080/hooks/agent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "event": "github.push",
    "payload": {
      "repository": "my-repo",
      "commits": [...],
      "ref": "refs/heads/main"
    }
  }'
```

**配置 Webhook 处理器**：
```yaml
# config/webhooks.yaml
hooks:
  - event: "github.push"
    agent: "developer"
    prompt: "分析这次提交，检查是否有潜在问题"
  - event: "stripe.payment"
    agent: "finance-bot"
    prompt: "记录这笔收入并发送感谢邮件"
```

---

### 6.2 n8n 自动化

**架构图**：
```
GitHub New Issue → n8n → HTTP Request → OpenClaw Hook
                                      ↓
                              Agent 分析 Issue
                                      ↓
                              创建 Jira Ticket ← HTTP Response
```

**n8n Workflow JSON**：
```json
{
  "nodes": [
    {
      "name": "GitHub Trigger",
      "type": "n8n-nodes-github-trigger",
      "parameters": { "event": "issue", "action": "opened" }
    },
    {
      "name": "HTTP Request",
      "type": "n8n-nodes-http-request",
      "parameters": {
        "method": "POST",
        "url": "http://openclaw:8080/hooks/agent",
        "body": {
          "event": "github.issue",
          "payload": "={{ $json.body }}"
        }
      }
    }
  ]
}
```

---

### 6.3 Gmail Pub/Sub（实时触发）

**相比轮询的优势**：
- ✅ 延迟降至毫秒级
- ✅ 减少 API 调用 90%+
- ✅ 成本大幅降低

**配置步骤**：

1. **Google Cloud Pub/Sub 设置**：
```bash
gcloud pubsub topics create gmail-new-email
gcloud pubsub subscriptions create openclaw-sub \
  --topic gmail-new-email \
  --push-endpoint http://openclaw:8080/hooks/gmail
```

2. **Gmail API 监听规则**：
```python
from google.cloud import pubsub_v1

def on_new_email(message):
    """触发 OpenClaw 处理新邮件"""
    requests.post("http://localhost:8080/hooks/agent", json={
        "event": "gmail.new_message",
        "data": {
            "from": message.sender,
            "subject": message.subject,
            "snippet": message.snippet
        }
    })
```

---

### 6.4 数据库集成

**通过 MCP Server**：
```typescript
// db-mcp-server/index.ts
server.tool("query-users", async ({ filter }) => {
  const users = await db.users.findMany({ where: filter });
  return { content: [{ type: "text", text: JSON.stringify(users) }] };
});

server.tool("update-order", async ({ id, status }) => {
  await db.orders.update({ where: { id }, data: { status } });
  return { content: [{ type: "text", text: "Updated" }] };
});
```

**直接 SQL（需谨慎）**：
```json
{
  "tools": {
    "sql-executor": {
      "enabled": true,
      "readOnly": true,
      "allowedTables": ["users", "orders", "products"],
      "blockedCommands": ["DROP", "DELETE", "TRUNCATE"]
    }
  }
}
```

---

## 7. 监控与可观测性

### 7.1 两种主流方案对比

| 维度 | openclaw-telemetry | LangWatch |
|------|-------------------|-----------|
| **产品形态** | 专用插件 | 完整可观测性平台 |
| **开发者** | Knostic | LangWatch 团队 |
| **底层协议** | 绑定 OpenClaw 事件 | OpenTelemetry (OTEL) |
| **输出方式** | JSONL + Syslog | OTEL Export + UI |
| **可视化** | ❌ 需对接 SIEM | ✅ 内置 Dashboard |
| **成本追踪** | 基础 | ✅ 实时看板 |
| **调试工具** | ❌ 无 | ✅ 推理链追踪 |
| **部署方式** | 插件 | SaaS 或 Self-hosted |
| **定价** | 免费 | 免费 Self-hosted + 付费 SaaS |

---

### 7.2 openclaw-telemetry 配置

**安装**：
```bash
npm install -g @knostic/openclaw-telemetry
```

**基础配置**：
```json
{
  "plugins": {
    "entries": {
      "telemetry": {
        "enabled": true,
        "filePath": "~/.openclaw/logs/telemetry.jsonl"
      }
    }
  }
}
```

**高级安全配置**：
```json
{
  "telemetry": {
    "enabled": true,
    "syslog": {
      "enabled": true,
      "host": "syslog.yourcompany.local",
      "port": 514,
      "protocol": "udp",
      "format": "cef"
    },
    "redact": {
      "enabled": true,
      "replacement": "[REDACTED]",
      "patterns": [
        "sk-ant-[a-zA-Z0-9-]+",
        "Bearer [a-zA-Z0-9-]+"
      ]
    },
    "integrity": {
      "enabled": true,
      "algorithm": "sha256"
    },
    "rotation": {
      "enabled": true,
      "maxSize": "100M",
      "maxFiles": 10,
      "compress": true
    }
  }
}
```

---

### 7.3 LangWatch 配置

**安装 OTEL Collector**：
```bash
docker run -d \
  --name langwatch \
  -p 3000:3000 \
  -p 4317:4317 \
  langwatch/langwatch:latest
```

**OpenClaw 配置**：
```json
{
  "observability": {
    "otel": {
      "enabled": true,
      "endpoint": "http://langwatch:4317",
      "serviceName": "openclaw-production",
      "headers": {
        "x-langwatch-api-key": "${LANGWATCH_API_KEY}"
      }
    }
  }
}
```

**Dashboard 示例**：
```
┌─────────────────────────────────────────────────────────┐
│  LangWatch Dashboard - OpenClaw Production              │
├─────────────────────────────────────────────────────────┤
│  今日成本：$12.50  ↑ 15%                                │
│  平均延迟：2.3s   ↓ 5%                                 │
│  Token 用量：1.2M / 5M                                  │
├─────────────────────────────────────────────────────────┤
│  Top 5 高成本 Agent：                                   │
│  1. developer-agent    $4.20                            │
│  2. email-handler      $2.80                            │
│  3. pr-reviewer        $1.90                            │
├─────────────────────────────────────────────────────────┤
│  异常检测：                                              │
│  🚨 10:30 AM - executor-agent 调用 exec 工具 50 次/分钟    │
│  🚨 02:15 AM - 非工作时间活动 detected                   │
└─────────────────────────────────────────────────────────┘
```

---

### 7.4 Splunk 集成示例

**Filebeat 配置**：
```yaml
# filebeat.yml
filebeat.inputs:
  - type: filestream
    enabled: true
    paths:
      - ~/.openclaw/logs/telemetry.jsonl

processors:
  - decode_json_fields:
      field: message
      target: ""
      overwrite_keys: true

output.logstash:
  hosts: ["logstash:5044"]
```

**Splunk 查询示例**：
```spl
index=openclaw event="tool_call" tool="exec"
| stats count by agent, hour
| where count > 100
| table agent, hour, count
```

---

## 8. 生产环境部署方案

### 8.1 推荐架构

```
┌─────────────────────────────────────────────────────────┐
│                    公网层                                │
│  Cloudflare/Tailscale (零信任访问)                        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   代理层                                 │
│  LiteLLM Container (统一 API 网关 + 密钥管理 + 成本熔断)     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  应用层                                  │
│  OpenClaw Container (无根容器，切断入站网络)                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  网络层                                  │
│  Squid Proxy (域名白名单，仅允许访问必要 API)               │
└─────────────────────────────────────────────────────────┘
```

---

### 8.2 Docker Compose 完整配置

```yaml
version: '3.8'

services:
  openclaw:
    image: openclaw/openclaw:latest
    container_name: openclaw-prod
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    networks:
      - internal_only
    environment:
      - ANTHROPIC_API_KEY=${API_KEY}
      - HTTP_PROXY=http://squid:3128
      - HTTPS_PROXY=http://squid:3128
    volumes:
      - ./workspace:/workspace:ro
      - ./config:/config:ro
      - ./logs:/logs
    depends_on:
      - squid

  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - LITELLM_MASTER_KEY=${LITELLM_KEY}
    networks:
      - internal_only

  squid:
    image: ubuntu/squid:latest
    volumes:
      - ./squid.conf:/etc/squid/squid.conf:ro
    networks:
      - internal_only
      - external

  langwatch:
    image: langwatch/langwatch:latest
    ports:
      - "3000:3000"
      - "4317:4317"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    networks:
      - internal_only

networks:
  internal_only:
    internal: true
  external:
    internal: false
```

---

### 8.3 Squid 代理配置

```bash
# /etc/squid/squid.conf
http_port 3128

# 域名白名单
acl allowed_domains dstdomain \
    .anthropic.com \
    .openai.com \
    .googleapis.com \
    .github.com \
    .openclaw.ai

# 仅允许访问白名单域名
http_access allow allowed_domains
http_access deny all

# 日志
access_log /var/log/squid/access.log
cache_log /var/log/squid/cache.log
```

---

### 8.4 LiteLLM 配置（成本熔断）

```yaml
# litellm_config.yaml
model_list:
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20260205
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  set_verbose: true
  drop_params: true
  
  # 预算控制
  budget_limit: 10.00  # 每日$10
  
  # 超时设置
  request_timeout: 600
  
  # 重试策略
  num_retries: 3
```

---

### 8.5 安全加固清单

部署前逐项核对：

- [ ] Gateway 绑定 `127.0.0.1`（非 `0.0.0.0`）
- [ ] 启用网关 Token 认证
- [ ] 渠道配置白名单（非公开私聊）
- [ ] 敏感文件权限 `chmod 600`
- [ ] API Key 使用环境变量（非明文）
- [ ] 沙箱模式配置为 `non-main` 或 `all`
- [ ] 出站网络代理 + 域名白名单
- [ ] 安装 telemetry 监控插件
- [ ] 定期执行 `openclaw security audit`
- [ ] 配置预算告警
- [ ] 启用日志脱敏
- [ ] 配置备份策略

---

### 8.6 备份策略

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/openclaw"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份工作区
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz \
  ~/.openclaw/workspace/

# 备份配置
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
  ~/.openclaw/config.json \
  ~/.openclaw/config/

# 备份记忆
tar -czf $BACKUP_DIR/memory_$DATE.tar.gz \
  ~/.openclaw/workspace/memory/ \
  ~/.openclaw/workspace/MEMORY.md

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# 上传到云存储（可选）
aws s3 cp $BACKUP_DIR s3://my-bucket/openclaw-backups/
```

**Cron 配置**：
```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh
```

---

## 附录：参考资源

- **官方文档**：https://docs.openclaw.ai
- **GitHub**：https://github.com/openclaw/openclaw
- **技能市场**：https://clawhub.com
- **社区 Discord**：https://discord.gg/clawd
- **openclaw-telemetry**：https://github.com/knostic/openclaw-telemetry
- **LangWatch**：https://langwatch.ai
- **LiteLLM**：https://litellm.ai

---

*完*
