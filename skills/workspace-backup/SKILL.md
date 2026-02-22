---
name: workspace-backup
description: Backup and restore OpenClaw workspace configurations and important files. Supports creating snapshots and reverting back to previous states to prevent data loss.
when: "When user mentions '备份工作区', '还原备份', 'backup workspace', 'restore config', '配置备份', '保存工作区状态', '备份', '恢复'"
examples:
  - "帮我把当前的 workspace 配置备份一下"
  - "还原到昨天的备份"
  - "备份配置文件"
  - "查看所有备份"
  - "restore workspace"
metadata:
  openclaw:
    requires:
      bins: ["tar", "mkdir", "bash", "ls"]
---

# Workspace Backup & Restore

This skill provides the ability to safely backup and restore the user's workspace configurations, securing their environment against unintended changes.

## Backup Directory Location
All backups are stored locally in the workspace under the `<workspace_root>/.backups/` directory.

## 1. Creating a Backup (备份)
When the user requests to backup the workspace configuration, execute the following steps:
1. **Ensure the backup directory exists:**
   ```bash
   mkdir -p .backups
   ```
2. **Create a compressed archive:**
   Create a timestamped archive containing the workspace files, ensuring that heavy or unnecessary directories (like `node_modules`, `.git`, `.tmp`, and `.backups` itself) are excluded to save space.
   ```bash
   tar -czvf .backups/workspace_backup_$(date +%Y%m%d_%H%M%S).tar.gz --exclude='.git' --exclude='node_modules' --exclude='.backups' --exclude='.tmp' .
   ```
3. **Confirm success:**
   Notify the user that the backup was created successfully, providing the exact filename of the new backup.

## 2. Viewing Backups (查看备份列表)
When the user wants to see available backups:
1. **List the backups:**
   ```bash
   ls -lh .backups/
   ```
2. **Display to user:**
   Present the list of backups in a clean, readable Markdown list or table, showing the filename, date/time, and file size.

## 3. Restoring a Backup (还原)
When the user requests to restore the workspace or configurations from a backup:
1. If the user hasn't specified which backup to use, first list the available backups and ask them to choose.
2. **Execute the restore command:**
   Extract the archive over the current workspace. *Warning: Ensure the user is aware this will overwrite current files.*
   ```bash
   tar -xzvf .backups/<backup_filename.tar.gz> -C ./
   ```
3. **Confirm success:**
   Notify the user that the workspace has been successfully restored from the selected backup.

## Security & Best Practices
- Never include sensitive global keys that are outside the workspace.
- Always prompt for confirmation before restoring, as it overrides current uncommitted work.
- Suggest to the user to clean up old backups if the `.backups/` folder grows too large.
