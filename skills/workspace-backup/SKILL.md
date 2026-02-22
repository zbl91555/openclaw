---
name: workspace-backup
description: 运用语义化快照策略自动化备份和还原工作区配置。保障因误操作引起的数据遗失，能够通过语义化描述无痕回滚至之前安全版本。
when: "当用户要求 '备份工作区', '还原', 'backup config', 'restore workspace', '工作区备份', '查看历史备份', '创建快照' 时"
examples:
  - "帮我创建一个当前的 workspace 配置快照，备注刚才写完了用户登录页"
  - "我现在有哪些之前的工作区备份？"
  - "我刚才操作错误，快帮我还原回昨天打包那份关于数据库修改的备份！"
  - "执行工作区快照备份"
metadata:
  openclaw:
    requires:
      bins: ["bash", "tar", "ls", "grep", "sed"]
    emoji: "📦"
---

# Workspace Backup

You are now equipped with the `workspace-backup` skill. Please apply structured cognitive processing while balancing speed and accuracy based on specific situational requirements. 
作为专门负责处理工作区数据安全的专家，您的使命是管理本地的隐藏备份记录 `.backups/`，并且在**备份和还原的过程中贯彻“语义化”原则**，让冰冷的备份包变成包含业务意义的时光机。

## 功能说明与脚本映射

所有的逻辑操作均交由外部脚本实现，提升触发准确性和维护性。

### 1. 创建语义化备份 (Semantic Backup)
当用户需要将当前的配置与状态封存起来时：
- **必须的语义化操作**：您需要为本次备份提供一段简练且包含业务逻辑的**语义化描述**（例如："完成用户登录页面的UI设计" 或 "重写了数据库存储逻辑"）。如果用户在指令中未提供，您应主动根据上下文推断并总结当前工作进度。
- **执行指令**：`bash skills/workspace-backup/scripts/backup.sh "<您的语义化描述>"`
- 该脚本会自动打包文件并在本地存储配套的 metadata，用来永远铭记该状态。

### 2. 查看备份历史 (List History)
当用户迷失方向，需要知道手头上有哪些"时光机"可以回溯时：
- **执行指令**：`bash skills/workspace-backup/scripts/list.sh`
- 该脚本会输出带有详细**语义化说明**的历史备份记录。您应将其包装为友好易读的报表（含时间、用途、文件名等）反馈给用户。

### 3. 指定还原 (Restore)
用户选择特定快照后请求时光倒流：
- **操作前警告**：告知这将会**覆盖并抹除现有修改**。
- **执行指令**：`bash skills/workspace-backup/scripts/restore.sh <backup_filename>`
- **还原后的语义化说明**：在恢复成功并且脚本提供输出了还原的语义化信息后，**向用户进行语义化的人性化汇报**。例如："已成功为您将系统时光倒流至『完成用户登录页面的UI设计』时的状态，现在的代码已经恢复纯净。"

## 系统执行准则
- 无论何时，**备份都需要提供一段关于功能或业务的语义化总结**。
- 不进行任何侵略性操作（如从远端随意下载）。
- 提醒用户清理巨大体积的过期备份。
