#!/bin/bash
# openclaw-sync.sh — 将 .openclaw 配置同步到 GitHub
# 仅在 openclaw gateway 正常运行时执行
# 用于：每日定时同步 + 大管家手动触发
#
# 用法: bash ~/.openclaw/scripts/openclaw-sync.sh

set -euo pipefail

OPENCLAW_DIR="$HOME/.openclaw"
REPO_URL="https://github.com/zbl91555/openclaw"
LOG_FILE="/tmp/openclaw-sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
  echo "[$TIMESTAMP] $*" | tee -a "$LOG_FILE"
}

# ============================================
# 步骤 1: 健康检查 — 只在 gateway 运行时同步
# ============================================
GATEWAY_PID=$(pgrep -f "openclaw-gateway" 2>/dev/null | head -1 || true)
GATEWAY_PORT_OPEN=$(lsof -i :18789 -t 2>/dev/null || true)

if [ -z "$GATEWAY_PORT_OPEN" ]; then
  log "❌ openclaw gateway 未运行 (port 18789 无监听)，跳过同步"
  echo "⚠️ Gateway 未运行，本次同步已跳过"
  exit 0
fi

log "✅ Gateway 运行正常 (port 18789)"

# ============================================
# 步骤 2: 初始化 git (首次执行时)
# ============================================
cd "$OPENCLAW_DIR"

if [ ! -d ".git" ]; then
  log "🔧 初始化 git 仓库..."
  git init
  git remote add origin "$REPO_URL"
  git checkout -b config 2>/dev/null || git checkout config 2>/dev/null || true
  log "✅ git 初始化完成"
fi

# 确保在 config 分支 (与 workspace 的 main 分支隔离)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ "$CURRENT_BRANCH" != "config" ]; then
  git checkout -b config 2>/dev/null || git checkout config
fi

# ============================================
# 步骤 3: 检查变更
# ============================================
git add -A

CHANGED=$(git status --porcelain)
if [ -z "$CHANGED" ]; then
  log "✅ 无变更，跳过 commit"
  echo "✅ .openclaw 配置已是最新"
  exit 0
fi

CHANGED_COUNT=$(echo "$CHANGED" | wc -l | tr -d ' ')

# ============================================
# 步骤 4: Commit + Push
# ============================================
SHORT_DATE=$(date '+%Y-%m-%d %H:%M')
COMMIT_MSG="⚙️ 配置自动同步: $SHORT_DATE ($CHANGED_COUNT 个文件)"

git commit -m "$COMMIT_MSG"
git push origin config --force 2>&1 | tail -3

COMMIT_HASH=$(git rev-parse --short HEAD)

log "✅ 同步完成 — $COMMIT_HASH ($CHANGED_COUNT 个文件)"
echo ""
echo "✅ .openclaw 已同步到 GitHub"
echo "📦 Commit: $COMMIT_HASH"
echo "📁 变更: $CHANGED_COUNT 个文件"
echo "🔗 $REPO_URL/tree/config"
