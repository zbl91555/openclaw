# MEMORY.md - 林哥的长期记忆

> 最后更新：2026-02-23  
> 维护原则：只记录核心事实和偏好，日常日志放在 `memory/YYYY-MM-DD.md`

---

## [FACT] 用户信息

| 项目 | 值 |
|------|-----|
| **称呼** | 林哥 |
| **语言** | 中文（简体） |
| **时区** | Asia/Shanghai |
| **系统** | macOS (MacBook Pro) |
| **Node 版本** | v22.22.0 |

---

## [FACT] 用户偏好

### 沟通风格
- ✅ 通俗易懂，简洁干练
- ✅ 直言不讳，直击痛点
- ✅ 透明度："做了什么"、"为什么做"、"好坏是什么"
- ❌ 不说废话，不绕弯子

### 技术偏好
- ✅ 最佳实践驱动
- ✅ 追求工程化和健壮性
- ✅ 高内聚低耦合
- ✅ 谋定而后动（先确认方案再执行）

### 通知渠道
- **主要**：Telegram
- **语音**：Azure Neural TTS
  - 声音：`zh-CN-XiaoxiaoNeural`
  - 语速：`1.3`（比标准快 30%）

---

## [FACT] 工作环境

### OpenClaw 配置
| 项目 | 值 |
|------|-----|
| **工作区** | `~/.openclaw/workspace` |
| **主模型** | `dashscope/qwen3.5-plus` (别名：qwen) |
| **备选模型** | `dashscope/qwen3-max-2026-01-23` (别名：max) |
| **网关端口** | 18789 |
| **网关绑定** | `loopback` (127.0.0.1) |
| **渠道** | Telegram (dmPolicy: open) |

### 已安装技能
- `web-search-pro` (Tavily API)
- `perplexity`

### 浏览器配置
- **默认 Profile**：`openclaw`
- **CDP 端口**：18800
- **Chrome Profile**：`chrome` (CDP 端口：18792)

---

## [PROJECT] OpenClaw 知识库

### NotebookLM 知识库
| 名称 | 数据源 | 用途 |
|------|--------|------|
| **OpenClaw 统一知识库 (2026)** | 190 个 URL | 技术资料查询 |
| **个人分享** | 2 篇文章 | 技术分享文档 |

### 已创建文章
| 文件名 | 字数 | 状态 |
|--------|------|------|
| **OpenClaw 技术分享.md** | ~10,000 字 | ✅ 完成 |
| **OpenClaw 进阶指南.md** | ~24,500 字 | ✅ 完成 |

### 文章位置
```
/Users/mudandan/.openclaw/workspace/articles/
├── OpenClaw 技术分享.md
└── OpenClaw 进阶指南.md
```

---

## [PREFERENCE] 交互规则

### 会话启动
1. 读取 `SOUL.md`（人格设定）
2. 读取 `USER.md`（用户信息）
3. 读取 `MEMORY.md`（长期记忆，仅主会话）
4. 读取今日/昨日 `memory/YYYY-MM-DD.md`

### 回复规则
- ✅ 默认中文回复
- ✅ 代码、命令、变量名保持英文
- ✅ 使用 emoji 增加可读性（☕️🦞✅❌）
- ✅ 复杂任务前先提方案并获确认
- ✅ 涉及配置修改必须事先授权

### 消息规则
- Telegram 渠道
- 支持 inline buttons
- TTS 自动播放（always 模式）

---

## [TODO] 待办事项

### 高优先级
- [ ] 配置 Lobster 工作流（个人知识库同步）
- [ ] 创建 Trello/Notion 集成

### 中优先级
- [ ] 配置 Cron 定时任务
- [ ] 设置记忆检索优化参数

### 低优先级
- [ ] 探索多 Agent 协作案例
- [ ] 测试 openclaw-telemetry 监控

---

## [HISTORY] 重要决策

| 日期 | 决策 | 说明 |
|------|------|------|
| 2026-02-23 | 创建 NotebookLM 统一知识库 | 合并 8 个旧笔记本，整合 190 个 URL |
| 2026-02-23 | 创建技术分享文章 | 基础入门 + 进阶指南，共 34,500 字 |
| 2026-02-23 | 配置并发控制 | maxConcurrent: 4, subagents: 8 |
| 2026-02-24 | NotebookLM 播客生成实战 | 首次生成两个播客（个人分享 + 统一知识库），验证子 Agent 监控模式 |

---

## [SKILL] 常用命令

### OpenClaw 管理
```bash
# 查看状态
openclaw status

# 重启网关
openclaw gateway restart

# 列出会话
openclaw sessions list

# 安装技能
openclaw skill install <skill-name>
```

### NotebookLM
```bash
# 创建笔记本
notebooklm create "名称"

# 添加数据源
notebooklm source add "URL"

# 列出笔记本
notebooklm list

# 提问
notebooklm ask "问题" -n <notebook-id>

# 生成播客
notebooklm generate audio "描述" -n <notebook-id> --language zh_Hans

# 等待播客完成（子 Agent 后台监控）
notebooklm artifact wait <artifact-id> -n <notebook-id> --timeout 1800

# 下载播客
notebooklm download audio ./output.mp3 -a <artifact-id> -n <notebook-id>
```

---

## [NOTE] 备注

- **记忆维护**：定期（每几天）review `memory/YYYY-MM-DD.md`，将有价值的内容提炼到本文件
- **文件位置**：`~/.openclaw/workspace/MEMORY.md`
- **权限**：`chmod 600`（仅当前用户可读）

---

## [LESSON] 任务监控方案选择 ⚠️

**2026-02-24 播客生成实战教训**：

| 场景 | ✅ 正确方案 | ❌ 错误方案 | 原因 |
|------|-----------|-----------|------|
| **长时间任务监控**（>10 分钟） | 子 Agent 后台 + `artifact wait` | 心跳 | 心跳间隔 30 分钟，太慢 |
| **定期检查**（邮箱/日历） | 心跳（30 分钟一次） | - | 合适的时间粒度 |
| **精确时间任务**（9:00 AM 提醒） | Cron | 心跳 | 心跳时间不精确 |
| **即时通知**（任务完成） | 子 Agent + `openclaw system event` | 心跳 | 需要 push-based 通知 |

**播客生成最佳实践**：
```bash
# 1. 生成播客
notebooklm generate audio "描述" -n <id> --json

# 2. 子 Agent 后台监控（非阻塞）
Task(prompt="notebooklm artifact wait <id> -n <notebook-id> --timeout 1800 && notebooklm download audio ./podcast.mp3 -a <id> -n <notebook-id>")

# 3. 完成后自动通知
# 子 Agent 内添加：openclaw system event --text "播客完成" --mode now
```

**Telegram 文件限制**：最大 16MB，大文件需云存储或本地路径分享。

---

## [LESSON] TTS 语音格式规范 ⚠️

**2026-02-25 教训**：发送 TTS 语音时，文本中混入了 markdown 格式（**加粗**）和 emoji（🦞☕️），导致语音引擎直接读出这些字符，听起来很怪。

**正确做法**：
- TTS 文本必须是纯文本
- 不使用任何 markdown 格式（**加粗**、`代码`、- 列表等）
- 不使用 emoji 表情
- 数字、英文、专有名词用中文口吻表达（如 "memu 点 bot"、"1 万 5 千星"）

**错误示例**：
```
**第一个，memU** —— 记忆框架，1 万 5 千星 🦞
```

**正确示例**：
```
第一个，memU，记忆框架，1 万 5 千星。
```

**执行标准**：以后所有 TTS 语音发送前，必须检查文本是否为纯文本，无格式、无 emoji。

---

## [PREFERENCE] 总结输出格式 ⚠️

**2026-02-25 新增**：GitHub Trending、资讯类总结、调研报告等长内容，**语音 + 文字一起发**。

**适用场景**：
- GitHub Trending 总结
- 社区案例调研
- 技术资讯简报
- 项目分析报告

**执行标准**：
1. 先发 TTS 语音（纯文本，无格式无 emoji）
2. 紧接着发文字版总结（可带 markdown 和 emoji）

**例外**：用户明确要求只要语音或只要文字时，按用户要求。

---

## [LESSON] 子 Agent 超时排查 ⚠️

**2026-02-25 问题**：子 agent 分析 stitch-mcp 源码时超时（5 分钟限制）。

**根因**：
1. 子 agent 启动时检测到网关未响应，尝试自动启动网关
2. 网关实际已在运行（端口被占用），但子 agent 无法检测
3. 反复重试启动网关约 10 次（每次 10 秒），占用 100 秒
4. 加上源码分析时间，总计超过 5 分钟

**解决方案**：
1. **增加超时时间**：源码分析类任务 `timeoutSeconds: 600`（10 分钟）
2. **任务分解**：大任务拆成多个小任务（克隆→分析 A→分析 B→汇总）
3. **预检查网关**：spawn 前先 `openclaw gateway status`

**最佳实践**：
- 简单任务（问答/总结）：300 秒
- 中等任务（单文件分析）：400 秒
- 复杂任务（多文件源码分析）：600 秒+
- 超复杂任务（跨项目调研）：任务分解 + 多子 agent

---

*最后同步：2026-02-25*

### agents_list 工具语义 ⚠️

**2026-02-26 新增**：`agents_list` 工具返回的是当前会话可 target 的 Agent allowlist（用于 `sessions_spawn`），不是已配置的 Agent 列表。

**正确做法**：
- 查询 Agent 配置状态，直接用 `openclaw agents list` 命令
- 不要依赖 `agents_list` 工具判断 Agent 是否配置
- 工具返回的信息可能是片面的，需要多角度验证

