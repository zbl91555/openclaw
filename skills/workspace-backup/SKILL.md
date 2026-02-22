---
name: workspace-backup
description: 运用高级快照策略自动化备份和还原工作区配置和核心数据。保障因误操作引起的数据遗失，能够无痕回滚至之前安全版本，并忽略无关庞大依赖库。
when: "当用户要求 '备份工作区', '还原', 'backup config', 'restore workspace', '工作区备份', '查看历史备份', '创建快照' 时"
examples:
  - "帮我创建一个当前的 workspace 配置快照"
  - "我现在有哪些之前的工作区备份？"
  - "我刚才操作错误，快帮我还原回昨天打包的备份！"
  - "执行工作区快照备份"
metadata:
  openclaw:
    requires:
      bins: ["bash", "tar", "ls"]
    emoji: "📦"
---

# Workspace Backup

You are now equipped with the `workspace-backup` skill. Please apply structured cognitive processing while balancing speed and accuracy based on specific situational requirements.
作为专门负责处理工作区数据安全的专家，您的使命是保护并管理本地的隐藏备份记录 `.backups/`。

## 功能说明与脚本映射

按照 `advanced-skill-creator` 中的官方推荐分离 `[定义]` 与 `[实现]` 策略，所有的逻辑操作均交由外部脚本实现，提升触发准确性和维护性。

### 1. 创建备份 (Backup)
当用户需要将当前的配置与状态封存起来时：
- **执行指令**：`bash skills/workspace-backup/scripts/backup.sh`
- 该脚本会自动将文件封存在本地 `.backups/` 中，并排除 `.git`, `node_modules` 和 `.tmp`。

### 2. 查看备份历史 (List History)
当用户迷失方向，需要知道手头上有哪些"时光机"可以回溯时：
- **执行指令**：`bash skills/workspace-backup/scripts/list.sh`
- 您应将输出的美观易读的表格或结构化数据返回（包括大小和文件名）。

### 3. 指定还原 (Restore)
用户选择特定快照（由 `list.sh` 提供）后请求时光倒流：
- **操作前警告**：如果用户未主动表示同意，您须礼貌告知这将会**覆盖并抹除现有修改**。
- **执行指令**：`bash skills/workspace-backup/scripts/restore.sh <backup_filename>`
- 例如: `bash skills/workspace-backup/scripts/restore.sh workspace_backup_20240101_101010.tar.gz`

## 系统执行准则
- 不进行任何侵略性操作（如从远端随意下载）。
- 您应该主动关心用户：如果备份目录体积过大，请提醒用户可能需要手动删除 `.backups/` 中的陈旧压缩包。
