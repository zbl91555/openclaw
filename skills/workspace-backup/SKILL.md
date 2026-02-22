---
name: workspace-backup
description: 通过 Git 将工作区配置推送到 GitHub 实现语义化云端备份，并支持通过 Commit ID 精准还原至任意历史快照。
when: "当用户要求 '备份工作区', '还原', 'backup config', 'restore workspace', '工作区备份', '查看历史备份', '创建快照', '提交备份', '回滚' 时"
examples:
  - "帮我创建一个当前的 workspace 配置快照，备注刚才写完了用户登录页"
  - "我现在有哪些之前的工作区备份？"
  - "我刚才操作错误，快帮我还原回昨天那次关于数据库修改的备份！"
  - "执行工作区快照备份，推送到 GitHub"
metadata:
  openclaw:
    requires:
      bins: ["bash", "git"]
    emoji: "📦"
---

# Workspace Backup

You are now equipped with the `workspace-backup` skill. 作为专门负责工作区数据安全的专家，您的使命是通过 **Git + GitHub** 对工作区进行**语义化云端备份与版本管理**，让每一次提交都携带业务语义，成为可随时回溯的"时光机"。

> **核心原理**：备份 = Git Commit + Push to GitHub；还原 = 找到目标 Commit → 恢复文件内容。

## 功能说明与脚本映射

所有逻辑操作均通过外部脚本实现。脚本需在工作区根目录（即 Git 仓库根目录）中执行。

---

### 1. 创建语义化备份 (Backup → Commit & Push)

当用户需要将当前的配置与状态备份到 GitHub 时：

- **语义化描述（必须）**：为本次 commit 提供简练的业务语义描述。若用户未提供，您应主动根据上下文推断并总结当前工作进度。
- **执行指令**：
  ```bash
  bash skills/workspace-backup/scripts/backup.sh "<您的语义化描述>"
  ```
- 脚本将执行 `git add -A && git commit -m "<描述>" && git push`，同步到 GitHub 远端仓库。
- 若工作区无任何变更，脚本会友好提示，不执行无效操作。

---

### 2. 查看备份历史 (List → Git Log)

当用户需要浏览可回溯的历史快照时：

- **执行指令**：
  ```bash
  bash skills/workspace-backup/scripts/list.sh
  ```
- 脚本输出最近 20 条 commit 历史（含编号、Commit ID、时间、语义描述）。
- 您应将输出整理为友好的报表格式反馈给用户，重点展示每条记录的**Commit ID** 和**语义描述**。

---

### 3. 指定还原 (Restore → Git Checkout)

用户选择特定历史快照后请求回滚时：

- **操作前警告**：告知用户这将**覆盖当前文件内容**，未提交的变更会被暂存（stash）。
- **执行指令**：
  ```bash
  bash skills/workspace-backup/scripts/restore.sh <commit_id>
  ```
  其中 `<commit_id>` 为目标 commit 的短 ID（前7位即可，如 `abc1234`）。
- 脚本将使用 `git checkout <commit_id> -- .` 将工作区文件还原为目标版本，**HEAD 不变**，方便用户确认后再决定是否永久推送。
- **还原后汇报**：向用户语义化汇报，例如："已成功将工作区还原至『完成用户登录页面设计』时的状态（commit: abc1234，2024-03-15 10:30）。"

---

## 系统执行准则

- 备份时**必须提供语义化 commit message**，直白描述当前工作内容或业务里程碑。
- 执行还原前，**必须先展示 list 历史**（若用户未指定 commit），让用户选择目标快照。
- 还原操作执行后，明确告知用户：当前是"文件内容回滚"而非"永久重置"，如需永久回滚并同步 GitHub 远端，需额外执行 `git push --force`。
- 若遇到推送失败（网络/权限问题），本地 commit 已保留，提示用户稍后重试 `git push`。
