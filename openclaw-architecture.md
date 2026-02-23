# OpenClaw 技术架构图

## 整体架构概览

```mermaid
flowchart TB
    subgraph Input["📥 输入层 - 12+ 消息平台"]
        TG[Telegram]
        WA[WhatsApp]
        DC[Discord]
        SK[Slack]
        SG[Signal]
        iMSG[iMessage]
        OTHER[其他平台...]
    end

    subgraph Gateway["🎯 Gateway 网关层 - 控制中枢"]
        direction TB
        ADAPTER[🔄 通道适配器层<br/>输入标准化]
        SESSION[📋 会话管理器<br/>Session per Channel]
        QUEUE[⏱️ 命令队列<br/>每会话串行执行]
        ROUTE[🛣️ 多代理路由<br/>不同联系人/群组不同 Agent]
        UI[🖥️ Control UI + WebChat<br/>Port 18789]
        
        ADAPTER --> SESSION
        SESSION --> QUEUE
        QUEUE --> ROUTE
        ROUTE --> UI
    end

    subgraph Memory["🧠 记忆系统 - 三层存储"]
        direction TB
        TIER1[📝 Tier 1: 临时记忆<br/>会话上下文 + Daily Logs<br/>memory/YYYY-MM-DD.md]
        TIER2[📚 Tier 2: 持久记忆<br/>SOUL.md / USER.md<br/>MEMORY.md / TOOLS.md]
        TIER3[🔍 Tier 3: 语义检索<br/>SQLite-vec 向量搜索<br/>按需检索]
        
        TIER1 <--> TIER2
        TIER2 <--> TIER3
    end

    subgraph LLM["🤖 LLM 层 - 决策大脑"]
        direction LR
        MODEL1[Claude]
        MODEL2[GPT]
        MODEL3[Gemini]
        MODEL4[DeepSeek]
        MODEL5[Llama 本地]
        SWITCH[🔄 模型切换<br/>按任务选择]
        
        MODEL1 --- SWITCH
        MODEL2 --- SWITCH
        MODEL3 --- SWITCH
        MODEL4 --- SWITCH
        MODEL5 --- SWITCH
    end

    subgraph Tools["🛠️ 工具/技能层 - 执行手脚"]
        direction TB
        SKILL[📦 技能系统<br/>SKILL.md 按需加载]
        BROWSER[🌐 浏览器控制<br/>Playwright]
        EXEC[💻 命令执行<br/>Shell/PTY]
        MCP[🔌 MCP 集成<br/>外部工具]
        SUBAGENT[👥 子代理<br/>sessions_spawn]
        
        SKILL --> BROWSER
        BROWSER --> EXEC
        EXEC --> MCP
        MCP --> SUBAGENT
    end

    subgraph Heartbeat["💓 心跳系统 - 主动自治"]
        direction TB
        CHECK[✅ 廉价检查优先<br/>确定性脚本]
        ESCALATE[⬆️ 升级判断<br/>轻量模型 GPT-4o-mini]
        DECIDE[🧠 LLM 决策<br/>仅必要时调用]
        NOTIFY[📤 主动通知<br/>多平台推送]
        
        CHECK --> ESCALATE
        ESCALATE --> DECIDE
        DECIDE --> NOTIFY
    end

    Input --> ADAPTER
    Gateway <--> Memory
    Gateway --> LLM
    LLM --> Tools
    Gateway --> Heartbeat
    Heartbeat --> Gateway
    Tools --> Gateway

    style Gateway fill:#e1f5ff,stroke:#0077b6
    style Memory fill:#fff4e1,stroke:#ff8c00
    style LLM fill:#e8f5e9,stroke:#2e7d32
    style Tools fill:#f3e5f5,stroke:#7b1fa2
    style Heartbeat fill:#ffebee,stroke:#c62828
```

---

## 核心组件详解

### 1️⃣ Gateway 网关层（中枢神经）

```mermaid
flowchart LR
    subgraph Adapter["通道适配器"]
        WA_IN[WhatsApp<br/>Baileys]
        TG_IN[Telegram<br/>grammY]
        DC_IN[Discord<br/>discord.js]
    end

    subgraph Normalize["标准化"]
        NORM[统一消息对象<br/>sender + body + attachments + metadata]
    end

    subgraph Session["会话管理"]
        S1[会话 A<br/>Channel X]
        S2[会话 B<br/>Channel Y]
        S3[会话 C<br/>Group Z]
    end

    subgraph Queue["命令队列"]
        Q1[⏱️ 串行执行<br/>防止状态冲突]
    end

    Adapter --> Normalize
    Normalize --> Session
    Session --> Queue

    style Adapter fill:#e1f5ff
    style Normalize fill:#fff4e1
    style Session fill:#e8f5e9
    style Queue fill:#ffebee
```

**关键设计：**
- ✅ **输入标准化**：12+ 平台不同协议 → 统一消息对象
- ✅ **每会话串行**：防止工具冲突和状态不一致
- ✅ **多代理路由**：不同联系人/群组可配置不同 Agent

---

### 2️⃣ 记忆系统（三层架构）

```mermaid
flowchart TB
    subgraph Tier1["Tier 1: 临时记忆"]
        CTX[会话上下文<br/>当前对话历史]
        DAILY[Daily Logs<br/>memory/YYYY-MM-DD.md]
    end

    subgraph Tier2["Tier 2: 持久记忆"]
        SOUL[SOUL.md<br/>人格/原则]
        USER[USER.md<br/>用户信息]
        MEM[MEMORY.md<br/>长期记忆]
        TOOLS[TOOLS.md<br/>工具配置]
    end

    subgraph Tier3["Tier 3: 语义检索"]
        SQLITE[(SQLite-vec<br/>向量数据库)]
        SEARCH[语义搜索<br/>memory_search]
        FETCH[片段读取<br/>memory_get]
    end

    Tier1 -.->|按需检索 | Tier2
    Tier2 -.->|定期整理 | Tier3
    Tier3 -->|返回相关片段 | Tier1

    style Tier1 fill:#fff4e1
    style Tier2 fill:#e8f5e9
    style Tier3 fill:#e1f5ff
```

**关键特性：**
- ✅ **无外部数据库**：纯 Markdown + SQLite，简单可靠
- ✅ **按需加载**：不把所有记忆注入上下文，避免膨胀
- ✅ **自动整理**：定期将 Daily Logs 提炼到 MEMORY.md

---

### 3️⃣ 技能系统（USB 式插件）

```mermaid
flowchart TB
    subgraph Registry["技能注册"]
        SKILL_DIR[~/.openclaw/skills/]
        SKILL_MD[SKILL.md<br/>触发规则 + 执行逻辑]
    end

    subgraph Loading["加载策略"]
        LIST[技能列表<br/>名称 + 描述 + 路径]
        DECIDE[LLM 决策<br/>选择相关技能]
        LOAD[按需读取<br/>SKILL.md 全文]
    end

    subgraph Execution["执行"]
        TRIGGER[触发条件匹配]
        RUN[执行技能逻辑]
        RESULT[返回结果]
    end

    Registry --> Loading
    Loading --> Execution

    style Registry fill:#f3e5f5
    style Loading fill:#e1f5ff
    style Execution fill:#e8f5e9
```

**关键创新：**
- ✅ **不注入全文**：只注入技能列表，按需读取 SKILL.md
- ✅ **低门槛**：类似 USB 即插即用
- ✅ **社区生态**：ClawHub 技能市场

---

### 4️⃣ 心跳系统（主动自治）

```mermaid
flowchart TB
    TRIGGER[⏰ 定时触发<br/>Cron / Heartbeat 轮询]
    
    subgraph Cheap["廉价检查优先"]
        SCRIPT[确定性脚本<br/>检查邮件/日历/系统]
        LIGHT[轻量模型<br/>GPT-4o-mini / GPT-5-Nano]
    end

    subgraph Expensive["昂贵判断"]
        URGENT{是否紧急？}
        LLM[主 LLM 决策<br/>Claude/GPT-4]
    end

    subgraph Action["执行动作"]
        NOTIFY[📤 推送通知]
        EXEC[⚙️ 执行操作]
        LOG[📝 记录日志]
    end

    TRIGGER --> SCRIPT
    SCRIPT --> LIGHT
    LIGHT --> URGENT
    URGENT -->|是 | LLM
    URGENT -->|否 | LOG
    LLM --> Action

    style Cheap fill:#e8f5e9
    style Expensive fill:#ffebee
    style Action fill:#e1f5ff
```

**关键设计：**
- ✅ **廉价优先**：先跑脚本，再升级 LLM
- ✅ **主动通知**：3am 服务器宕机 → Telegram 推送
- ✅ **成本优化**：90% 检查不消耗昂贵 API

---

## 数据流向

```mermaid
sequenceDiagram
    participant User as 👤 用户
    participant Platform as 📱 消息平台
    participant Gateway as 🎯 Gateway
    participant Memory as 🧠 记忆系统
    participant LLM as 🤖 LLM
    participant Tools as 🛠️ 工具层

    User->>Platform: 发送消息
    Platform->>Gateway: 原始消息
    Gateway->>Gateway: 通道适配标准化
    Gateway->>Memory: 读取会话上下文
    Gateway->>Memory: 语义检索相关信息
    Gateway->>LLM: 上下文 + 消息
    LLM->>LLM: ReAct 循环推理
    LLM->>Gateway: 请求工具调用
    Gateway->>Tools: 执行技能/命令
    Tools-->>Gateway: 返回结果
    Gateway->>LLM: 工具执行结果
    LLM->>Gateway: 生成回复
    Gateway->>Memory: 更新会话历史
    Gateway->>Platform: 发送回复
    Platform->>User: 接收消息
```

---

## 部署架构

```mermaid
flowchart TB
    subgraph Local["🏠 本地部署"]
        GATEWAY[Gateway 守护进程<br/>Node.js]
        WORKSPACE[~/clawd/workspace<br/>配置 + 记忆 + 技能]
        SQLITE[(SQLite-vec<br/>向量索引)]
    end

    subgraph Cloud["☁️ 云服务"]
        LLM_API[LLM API<br/>Claude/GPT/Gemini]
        MCP[MCP 服务器<br/>外部工具]
    end

    subgraph Platforms["📱 消息平台"]
        TG[Telegram]
        WA[WhatsApp]
        DC[Discord]
    end

    Platforms <--> GATEWAY
    GATEWAY <--> WORKSPACE
    GATEWAY <--> SQLITE
    GATEWAY <--> LLM_API
    GATEWAY <--> MCP

    style Local fill:#e8f5e9
    style Cloud fill:#e1f5ff
    style Platforms fill:#fff4e1
```

**部署特点：**
- ✅ **本地优先**：所有数据存储在本地
- ✅ **混合云**：LLM 可本地可云端
- ✅ **单进程**：单个 Gateway 管理所有会话

---

## 安全边界

```mermaid
flowchart TB
    subgraph Safe["✅ 安全操作"]
        READ[读取文件]
        SEARCH[搜索网络]
        ORGANIZE[整理记忆]
        COMMIT[Git 提交]
    end

    subgraph Ask["⚠️ 需确认"]
        EMAIL[发送邮件]
        TWEET[社交媒体]
        PUBLIC[公开发布]
        EXTERNAL[任何出站操作]
    end

    subgraph Deny["❌ 禁止操作"]
        EXFIL[数据外泄]
        DESTRUCT[破坏性命令<br/>rm 无确认]
        SELF[自我复制/传播]
        BYPASS[绕过安全限制]
    end

    Safe --> Gateway
    Ask --> Gateway
    Deny -.->|阻止 | Gateway

    style Safe fill:#e8f5e9
    style Ask fill:#fff4e1
    style Deny fill:#ffebee
```

---

## 性能优化

| 优化点 | 策略 | 效果 |
|--------|------|------|
| **上下文管理** | 技能列表注入，按需读取 | 减少 90% token 消耗 |
| **会话队列** | 每会话串行执行 | 避免状态冲突 |
| **记忆分层** | 临时/持久/语义三层 | 按需检索，避免膨胀 |
| **心跳分级** | 廉价检查优先 | 减少 90% LLM 调用 |
| **模型切换** | 按任务选择模型 | 成本优化 50-80% |

---

*生成时间：2026-02-23 | 基于 28 个高质量源*
