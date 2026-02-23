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
```

---

## [NOTE] 备注

- **记忆维护**：定期（每几天）review `memory/YYYY-MM-DD.md`，将有价值的内容提炼到本文件
- **文件位置**：`~/.openclaw/workspace/MEMORY.md`
- **权限**：`chmod 600`（仅当前用户可读）

---

*最后同步：2026-02-23*
