#!/bin/bash
# auto-git-sync.sh — 全自动 workspace 同步到 GitHub
# 用于 cron 定时任务和大管家手动触发
# 无需人工审批，自动 commit + push

set -euo pipefail

WORKSPACE_DIR="$HOME/.openclaw/workspace"
LOG_FILE="/tmp/openclaw-git-sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
SHORT_DATE=$(date '+%Y-%m-%d %H:%M')

log() {
  echo "[${TIMESTAMP}] $*" | tee -a "$LOG_FILE"
}

log "=== OpenClaw workspace 自动同步开始 ==="
cd "$WORKSPACE_DIR"

# 检查 git 状态
if git diff --quiet && git diff --staged --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  log "✅ 无变更，跳过同步"
  echo "✅ Workspace 已是最新，无需同步"
  exit 0
fi

CHANGED_COUNT=$(git status --porcelain | wc -l | tr -d ' ')
log "📝 发现 ${CHANGED_COUNT} 个文件变更"

# 自动 commit
git add .
COMMIT_MSG="🔄 自动同步: ${SHORT_DATE} (${CHANGED_COUNT} 个文件)"
git commit -m "$COMMIT_MSG"
log "✅ Commit: $COMMIT_MSG"

# Push 到远端
git push origin main
COMMIT_HASH=$(git rev-parse --short HEAD)

log "✅ 同步完成 — commit: ${COMMIT_HASH}"
log "=== 同步结束 ==="

echo ""
echo "✅ Workspace 已同步到 GitHub"
echo "📦 Commit: ${COMMIT_HASH}"
echo "📁 变更文件: ${CHANGED_COUNT} 个"
echo "🔗 https://github.com/zbl91555/openclaw"
