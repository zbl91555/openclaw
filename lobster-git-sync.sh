#!/bin/bash
# Lobster Git Sync - 混合版本
# 使用 Lobster 检查状态 + Shell 执行同步

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
CURSOR_FILE="$HOME/.lobster/state/git-sync.cursor.json"

echo ""
echo "🦞 Lobster Git Sync"
echo "===================="
echo ""

mkdir -p ~/.lobster/state
cd "$WORKSPACE_DIR"

# ============================================
# 步骤 1: 检查 Git 状态（使用 Lobster）
# ============================================
echo "📋 步骤 1: 检查 Git 状态（Lobster）..."
CHANGES=$(lobster 'exec "git status --porcelain"' 2>&1)

if [ -z "$CHANGES" ] || echo "$CHANGES" | grep -q "^\[\]$"; then
    echo "✅ Workspace 配置已是最新，无需同步"
    exit 0
fi

echo ""
echo "发现以下变更："
echo "--------------"
echo "$CHANGES" | jq -r '.[]' 2>/dev/null || echo "$CHANGES"
echo "--------------"
echo ""

# ============================================
# 步骤 2: ⏸️ 人工审批
# ============================================
echo "⏸️  人工审批"
echo "============"
echo ""
read -p "确认提交到 GitHub？(y/N): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo ""
    echo "❌ 用户取消提交"
    exit 0
fi

echo ""
echo "✅ 用户已批准，继续执行..."
echo ""

# ============================================
# 步骤 3: 执行 Git 同步（Shell 命令）
# ============================================
echo "📋 步骤 3: 执行 Git 同步..."
echo ""

git add .
git commit -m "Lobster sync: $(date +%Y-%m-%d %H:%M)"
git push origin main

echo ""

# ============================================
# 步骤 4: 更新游标状态
# ============================================
echo "📋 步骤 4: 更新游标状态..."
COMMIT_HASH=$(git rev-parse HEAD)
cat > "$CURSOR_FILE" << EOF
{
  "workflow": "lobster-git-sync",
  "last_sync": "$(date -Iseconds)",
  "last_commit": "$COMMIT_HASH",
  "status": "completed",
  "approved_by": "user"
}
EOF
echo "✅ 游标已更新"

# ============================================
# 完成通知
# ============================================
echo ""
echo "===================="
echo "✅ Lobster Git Sync 完成！"
echo "===================="
echo ""
echo "提交信息：Lobster sync: $(date +%Y-%m-%d %H:%M)"
echo "Commit: $(git rev-parse --short HEAD)"
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""
