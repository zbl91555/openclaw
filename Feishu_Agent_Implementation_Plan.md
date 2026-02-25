# OpenClaw 飞书多 Agent 协作系统架构方案

基于 OpenClaw 原生底层架构结合社区飞书插件的能力，构建支持“多 Bot 群聊透明可见” + “卡片式进度折叠” + “一键打断”的 **A+ 架构**。

## 目标与背景

改造现有 `openclaw` 的配置与架构，使其能够：
1. **精简实体绑定**：将生硬的职位名称转换为行业顶尖大佬的拟人化角色（大管家-马云、百晓生-张一鸣、代码极客-Linus、笔杆子-吴晓波），绑定到飞书群聊中的 4 个不同 Bot。
2. **多模态与语音调度**：主 Agent (大管家-马云) 支持接收语音输入，理解意图并分发任务。
3. **预设专业 Skills 上膛**：为每个 Agent 配置符合其角色的工具（如 web-search-pro, notebooklm 等），大幅增强专业能力。
4. **原生自我进化**：通过本地工作区自带的 `self-improving-agent` 和 `evolver` 实现 Agent 经验自动捕获和全局能力升级。
5. **卡片折叠与一键打断**：避免子任务刷屏，长耗时任务使用飞书交互卡片展示进度，提供随时撤销按钮，并在飞书多维表格（Bitable）留痕。
6. **日常汇报机制**：通过 Cron 机制，让各个 Agent 每天自动工作并汇总至会议群。

## Recommended Approach: 飞书原生 A+ 模式

### 核心架构

使用社区成熟的 NPM 飞书插件 `@openclaw-plugins/feishu-plus` 作为通信管道，复用 OpenClaw 的 `bindings` 和事件总线机制。全员进入同一个飞书群。

```mermaid
graph TD
    User((User)) <--> |日常沟通/打断| FeishuDaily[飞书日常沟通群]
    User <--> |接收汇报/审批| FeishuFormal[飞书正式会议群]
    User <--> |Review 任务状态| FeishuBitable[(飞书多维表格 Kanban)]
    
    FeishuDaily <--> |Webhook| FeishuPlugin[OpenClaw Feishu Plugin]
    FeishuFormal <--> |Webhook| FeishuPlugin
    
    FeishuPlugin <-->|路由分配| OpenClawCore[OpenClaw Agent Core]
    FeishuPlugin -.->|Bitable API 写入进展| FeishuBitable
    
    subgraph "🤖 Agent 团队 (拟人化角色划分 & 独立运行)"
        Main[👑 大管家-马云: 任务拆解与进度把控]
        ResearchIdea[🔍 百晓生-张一鸣: 情报搜集与创意发想]
        Coding[💻 代码极客-Linus: 架构验证与撸代码]
        Writing[✍️ 笔杆子-吴晓波: 优美文案与干货沉淀]
        
        SubCode1[子 Coding Agent - 前端]
        SubCode2[子 Coding Agent - 后端]
        
        Main -->|@ 任务分配| ResearchIdea
        Main -->|@ 任务分配| Coding
        Main -->|@ 任务分配| Writing
        
        Coding -.->|CallSubAgent API 分发| SubCode1
        Coding -.->|CallSubAgent API 分发| SubCode2
        
        ResearchIdea -.->|同步任务状态| OpenClawCore
        Coding -.->|同步任务状态| OpenClawCore
    end
    
    CronScheduler((Cron 定时任务)) -->|每日触发| ResearchIdea
    CronScheduler -->|每日触发| Writing
    
    CronScheduler -->|每日总结数据| Main
    Main -->|发送正式日报| FeishuFormal
    
    Research -.->|日常沟通| FeishuDaily
    Coding -.->|进度卡片| FeishuDaily
```

### 关键机制设计

#### 1. 任务派发与干活
- 此阶段均在**日常沟通群**内发生，确保头脑风暴和协作过程随时可见、不干扰正式汇报节奏。
- 您在群里发消息：`@大管家-马云 帮我分析最近 AI 的发展，并写一个前端展示页面。`
- `大管家-马云` 理解后，在群里回复：`@百晓生-张一鸣 去搜集热点资料并梳理脑暴维度。 @代码极客-Linus 去写页面代码进行技术验证。 @笔杆子-吴晓波 根据实现梳理对外推文。` 

#### 2. Agent 预设 Skills 配置 (复用本地工作区)
根据您在本地 `/Users/mudandan/.openclaw/workspace/skills` 下已有的技能，我们将它们精准下发给对应的角色：
* **👑 大管家-马云 (Main)**：预设 `brainstorming` (脑暴规划), `advanced-skill-creator`, `evolver`, `self-improving-agent`, `summarize`。负责统筹、规划和系统进化决策。
* **🔍 百晓生-张一鸣 (PdM)**：预设 `exa-web-search-free`, `web-search-pro`, `notebooklm`, `universal-video-analyzer`。负责图文与视频资料获取、前沿探索。
* **💻 代码极客-Linus (SWE)**：预设 `cliproxyapi`, `gemini-cli`, `cloudflare-tunnel`, `find`, `ui-ux-pro-max` 以及原生的底层能力。负责架构执行与 UI/UX 落地。
* **✍️ 笔杆子-吴晓波 (Writer)**：预设 `notebooklm`, `summarize` 等。专精长文本提炼与优美文案撰写。 

#### 2. “卡片式”进度管理与打断 (Coding & 子 Agent 场景)
当 `Coding Agent` 分配子任务给后台其他的 `子 Agent` 时（非群聊 @ 实体），为避免在群内刷屏，会发送一张 **飞书互动卡片** 到日常群里：
* 卡片内容：动态更新每个子任务的进度状态 `[进行中 / 已完成 / 出错]`。
* 打断按钮：卡片底部配有 `[ 🛑 终止任务 ]` 和 `[ 暂停 ]` 按钮。点击后，OpenClaw 通过飞书插件的回调直接打断执行流。
* **Review 机制**：子任务代码生成完毕后，触发 `Coding Agent` 的 Review Tool，在卡片上展示结论等待确认。

#### 4. 任务看板可视化留痕 (Feishu Bitable Kanban) - 【可行性验证通过 ✅】
`@openclaw-plugins/feishu-plus` 原生深度集成了飞书开放平台的 API，能够直接读写多维表格（Bitable）。该方案 100% 技术可行：
* 我们将在飞书内建立一个专属的**任务多维表格（看板模式）**。
* 每当任何 Agent（无论是 PM 分配的大任务，还是 SWE 分配的子任务），都会通过插件自动调用 `/bitable/v1/apps/{app_token}/tables/{table_id}/records` 向多维表格写入一条记录。
* 卡片操作或状态流转时（Todo -> Doing -> Done -> Reviewing），自动更新该行数据。
* 您可以随时打开该飞书多维表格的**看板视图**，对所有 Agent 的进展进行一目了然的追溯。

#### 4. 强大的自我进化引擎 (Self-Evolution)
不再把日常琐碎的经验浪费掉！该架构引入了深度的原生自我完善闭环：
* **痛点截获 (self-improving-agent)**：当执行终端命令失败、或者您对 Agent 纠错时，它将自动利用低开销 Hooks，向 `~/.openclaw/workspace/.learnings/` 写入报错或教导文档（`ERRORS.md` / `LEARNINGS.md`）。
* **提纯重组 (evolver)**：`大管家-马云` 每晚定时通过 `evolver` 扫描日志，识别出高频踩坑点，一旦满足提权阈值（比如某报错出现了 3 次），立刻将避雷指引写入到系统的全局 Prompt（如 `AGENTS.md` 或 `SOUL.md`），或者自动打包成全新的 Skill 进行反哺，实现团队基因的迭代进化！

#### 5. 双群隔离与每日汇报会议机制
不再把日常琐碎的 Agent 对话和正式总结混在一起：
* **日常信息搜捕**：`百晓生-张一鸣` 自动调用新闻源工具，在**日常沟通群**内抛出话题并作分析；`笔杆子-吴晓波` 辅助成文。
* **正式会议与决策**：定义 `大管家-马云` 汇总团队在日常群的产出及核心成果，每天定点将规范排版好的《项目日报》发送至专门的**正式会议群**。您仅需在此群中批复进度或阅读摘要。

#### 6. 飞书 Bot 凭证记录 (Feishu Credentials)
为了长期维护方便，以下是用于飞书通道与 Agent 分发绑定的真实凭证矩阵：

| 角色设定 | Agent ID | App ID (作为 Bot ID) | App Secret |
| :--- | :--- | :--- | :--- |
| **👑 大管家-马云** | `main` | `cli_a915e7fc0a389cc4` | `UYHKRiK5TaJtTYLHUc6KAbTlKB7qhQb3` |
| **🔍 百晓生-张一鸣** | `pdm` | `cli_a915e01fcbb89cd4` | `E47kKPaxUeHyaq1aOJVImfvmCEdu6p2q` |
| **💻 代码极客-Linus** | `swe` | `cli_a915e08562b9dcb5` | `ykvhJvssJgVJHWSXgyMWkg8eXmcgvfW0` |
| **✍️ 笔杆子-吴晓波** | `writer` | `cli_a915e1384f389ced` | `D1yd8OfXAjHuJTZYNauPxbybvkWplUyK` |

---

### YAGNI 验证与取舍说明
* **弃用自己手写 Feishu Channel**：避免重复造轮子，全面拥抱社区长轮询、媒体解析的飞书插件。
* **弃用纯后台黑盒协作**：因为“子 Agent 派发和查阅进度”是您的核心关注点，纯黑盒不利于直接管理和打断。

## User Review Required

> [!IMPORTANT]
> 这是重构方案的设计底座。方案的落地方向是基于您的 Option C（原生 OpenClaw 架构演进）。
> 请确认以下关于**汇报与协作**的设计逻辑：
> 1. 大家在一个飞书群聊。
> 2. 长耗时/多后台的子任务将折叠到“活体卡片”中显示进度，由按钮触发打断。
> 3. 您可以通过语音输入由 Main Agent 识别分发。
> 
> 请**审核该方案**。如果您觉得符合期待，我们将以此为依据开始落地的 Checklist。
