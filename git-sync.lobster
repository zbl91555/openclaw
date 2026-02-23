name: "Workspace Git Backup & Sync"
description: "安全地将 OpenClaw Workspace 的配置变更备份到远程 Git 仓库"
version: "1.0"
author: "林哥"

# 全局配置
config:
  workspace_dir: "~/.openclaw/workspace"
  git_remote: "origin"
  git_branch: "main"
  timeout_ms: 30000

steps:
  # ============================================
  # 步骤 1: 检查 Git 状态
  # ============================================
  - name: check_git_status
    description: "检查本地 git 状态并获取变更列表"
    run: exec --json --shell "git -C {{config.workspace_dir}} status --porcelain"
    timeoutMs: 10000
    on_error:
      - run: notify-user --message "❌ Git 状态检查失败，请确认工作区已初始化 Git"
      - exit: 1

  # ============================================
  # 步骤 2: 如果有变更，获取详细 diff
  # ============================================
  - name: get_diff
    description: "获取详细的文件变更内容"
    run: exec --json --shell "git -C {{config.workspace_dir}} diff --stat"
    timeoutMs: 10000
    condition: "$check_git_status.stdout != ''"

  # ============================================
  # 步骤 3: 使用 LLM 总结变更内容
  # ============================================
  - name: summarize_changes
    description: "让 AI 分析变更并生成 commit message"
    run: llm-task --prompt "分析以下 Git 变更，用一句话总结修改内容（中文）：\n{{get_diff.stdout}}"
    stdin: $get_diff.stdout
    timeoutMs: 30000
    condition: "$get_diff.success == true"

  # ============================================
  # 步骤 4: 人工审批门（防误覆盖）
  # ============================================
  - name: human_review
    description: "等待用户确认是否提交变更"
    needs_approval: true
    preview: |
      📋 发现配置变更，确认提交到 GitHub？
      
      变更摘要：{{summarize_changes.text}}
      
      变更文件：
      {{check_git_status.stdout}}
      
      [✅ 批准提交] [❌ 拒绝]
    timeoutMs: 3600000  # 1 小时超时

  # ============================================
  # 步骤 5: Git Add + Commit
  # ============================================
  - name: git_commit
    description: "执行 Git 添加和提交"
    run: exec --shell "git -C {{config.workspace_dir}} add . && git -C {{config.workspace_dir}} commit -m '{{summarize_changes.text}}'"
    condition: "$human_review.approved == true"
    timeoutMs: 30000

  # ============================================
  # 步骤 6: Git Push 到远程仓库
  # ============================================
  - name: git_push
    description: "将变更推送到远程 GitHub 仓库"
    run: exec --shell "git -C {{config.workspace_dir}} push {{config.git_remote}} {{config.git_branch}}"
    condition: "$git_commit.success == true"
    timeoutMs: 60000
    on_error:
      - run: notify-user --message "❌ Git Push 失败，请检查网络连接和 SSH 密钥"
      - exit: 1

  # ============================================
  # 步骤 7: 更新游标状态
  # ============================================
  - name: update_cursor
    description: "记录本次同步状态，防止重复处理"
    run: exec --shell "echo '{\"last_sync\": \"$(date -Iseconds)\", \"commit\": \"$(git -C {{config.workspace_dir}} rev-parse HEAD)\"}' > ~/.lobster/state/git-sync.cursor.json"
    condition: "$git_push.success == true"

  # ============================================
  # 步骤 8: 通知用户同步完成
  # ============================================
  - name: notify_complete
    description: "向用户发送同步完成通知"
    run: notify-user --message "✅ Workspace 同步完成！\n\n提交信息：{{summarize_changes.text}}\nCommit: $(git -C {{config.workspace_dir}} rev-parse --short HEAD)"
    condition: "$update_cursor.success == true"

# ============================================
# 错误处理：无变更时的处理
# ============================================
- name: no_changes
  description: "如果没有变更，跳过同步"
  run: notify-user --message "✅ Workspace 配置已是最新，无需同步"
  condition: "$check_git_status.stdout == ''"
