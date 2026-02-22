# TOOLS.md — 工具路由规则

> 严格遵守此文件。**Token/密码禁止明文**，统一放 `~/.openclaw/.env`。

## 🔊 语音配置

| 项目 | 值 |
|------|-----|
| TTS 引擎 | Azure Neural TTS |
| 声音 | `zh-CN-XiaoxiaoNeural`（中文女声） |
| 语速 | `1.3`（比标准快 30%） |

> 配置文件：`config/voice_settings.json`

## 技能链（常见组合）

| 场景 | 链路 |
|------|------|
| 复杂任务 | `brainstorming` 确认方案 → 对应执行 skill |
| 视频分析后建库 | `universal-video-analyzer` → `notebooklm` |
| 长期自我改进 | `self-improving-agent`（被动积累）→ `evolver`（主动进化） |

## 搜索工具

| 场景 | 使用 |
|------|------|
| 日常查询、快速问答 | 内置 `web_search` |
| 技术文档、代码、语义搜索 | `exa-web-search-free`（无需 Key，优先于 web-search-pro） |
| 需要过滤域名 / 时间范围 / 新闻模式 | `web-search-pro` |

## 技能路由

| Skill | 触发时机 | 注意事项 |
|-------|---------|---------| 
| ⚠️ **brainstorming** | **任何复杂任务前**（规划/新功能/改行为/解决问题） | **HARD-GATE：必须先提方案并获用户确认，再执行** |
| **workspace-backup** | 备份、快照、还原工作区 | 每次操作必须附带语义化说明 |
| **notebooklm / summarize** | 建知识库、生成摘要、做播客 | 输出默认中文 |
| **self-improving-agent** | 命令报错、被用户纠正、发现更好的做法 | 自动触发，沉淀到 `.learnings/` |
| **gemini-cli** | 代码审查/注释/测试、commit/PR、文档翻译、日志分析、批量脚本、DevOps 配置 | Headless 模式；Gemini 3 优先，不可用降级 2.5 |
| **evolver** | 需要主动修复历史错误、批量进化 Agent 能力 | **手动调用**，不自动触发；用 `--review` 模式 |
| **universal-video-analyzer** | YouTube/Bilibili 链接、「分析视频」「提取字幕」「做播客」 | Bilibili 加 `--cookies-from-browser chrome` |
| **cloudflare-tunnel** | 「内网穿透」「暴露端口」「公网访问本地服务」 | 临时隧道一行命令；固定隧道需配 DNS |
| **ui-ux-pro-max** | 「设计界面」「UX 优化」「做组件」「设计系统」「改样式」 | 交付顺序：UI → UX → 设计系统 → 代码实现 |
| **advanced-skill-creator** | 「写一个 skill」「创建技能」「写触发」「openclaw skill」 | 必须完整走 5-step 研究流程，禁止跳步 |
| **cliproxyapi** | 修改本机 AI 代理配置、添加 AI 提供商、改模型别名、重启代理 | 配置 `/usr/local/etc/cliproxyapi.conf`；curl 必须用 `/usr/bin/curl --noproxy localhost` |