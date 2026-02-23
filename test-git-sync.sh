#!/bin/bash
# Lobster Git Sync 工作流 - Bash 测试版
# 用途：测试 Lobster 工作流的完整流程

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
CURSOR_FILE="$HOME/.lobster/state/git-sync.cursor.json"

echo "🦞 OpenClaw Workspace Git Sync 测试"
echo "===================================="
echo ""

# 创建 Lobster 状态目录
mkdir -p ~/.lobster/state

# 初始化游标文件（如果不存在）
if [ ! -f "$CURSOR_FILE" ]; then
    echo '{"status":"initialized","last_sync":null}' > "$CURSOR_FILE"
fi

cd "$WORKSPACE_DIR"

# ============================================
# 步骤 1: 检查 Git 状态
# ============================================
echo "📋 步骤 1: 检查 Git 状态..."
GIT_STATUS=$(git status --porcelain)

if [ -z "$GIT_STATUS" ]; then
    echo "✅ Workspace 配置已是最新，无需同步"
    exit 0
fi

echo "发现变更："
echo "$GIT_STATUS"
echo ""

# ============================================
# 步骤 2: 获取详细 diff
# ============================================
echo "📋 步骤 2: 获取详细变更..."
GIT_DIFF=$(git diff --stat)
echo "$GIT_DIFF"
echo ""

# ============================================
# 步骤 3: 生成 commit message（简单版）
# ============================================
echo "📋 步骤 3: 生成提交信息..."
COMMIT_MSG="Git sync: $(date '+%Y-%m-%d %H:%M') - 配置备份"
echo "提交信息：$COMMIT_MSG"
echo ""

# ============================================
# 步骤 4: 人工确认（简化版审批门）
# ============================================
echo "📋 步骤 4: 人工审批"
echo ""
echo "变更文件："
echo "$GIT_STATUS" | while read line; do echo "  $line"; done
echo ""
read -p "确认提交到 Git？(y/N): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ 用户取消提交"
    exit 0
fi

# ============================================
# 步骤 5: Git Commit
# ============================================
echo ""
echo "📋 步骤 5: Git Commit..."
git add .
git commit -m "$COMMIT_MSG"
echo "✅ Commit 成功"
echo ""

# ============================================
# 步骤 6: Git Push（如果有远程仓库）
# ============================================
echo "📋 步骤 6: Git Push..."
if git remote -v | grep -q origin; then
    git push origin main
    echo "✅ Push 成功"
else
    echo "⚠️  未配置远程仓库，跳过 Push"
fi
echo ""

# ============================================
# 步骤 7: 更新游标状态
# ============================================
echo "📋 步骤 7: 更新游标状态..."
COMMIT_HASH=$(git rev-parse HEAD)
cat > "$CURSOR_FILE" << EOF
{
  "workflow": "git-sync",
  "last_sync": "$(date -Iseconds)",
  "last_commit": "$COMMIT_HASH",
  "status": "completed"
}
EOF
echo "✅ 游标已更新"
echo ""

# ============================================
# 步骤 8: 完成通知
# ============================================
echo "===================================="
echo "✅ Workspace 同步完成！"
echo "===================================="
echo ""
echo "提交信息：$COMMIT_MSG"
echo "Commit: $(git rev-parse --short HEAD)"
echo ""
echo "游标状态："
cat "$CURSOR_FILE"
echo ""
