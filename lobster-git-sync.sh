#!/bin/bash
# Lobster Git Sync - 命令行版本
# 使用 Lobster 引擎实现 Workspace 自动同步

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
CURSOR_FILE="$HOME/.lobster/state/git-sync.cursor.json"

echo "🦞 Lobster Git Sync 启动"
echo "========================"
echo ""

# 创建 Lobster 状态目录
mkdir -p ~/.lobster/state

# 初始化游标
if [ ! -f "$CURSOR_FILE" ]; then
    echo '{"status":"initialized"}' > "$CURSOR_FILE"
fi

cd "$WORKSPACE_DIR"

# ============================================
# Lobster 命令行工作流
# ============================================

# 步骤 1-3: 检查状态 + 过滤变更
echo "📋 步骤 1-3: 检查 Git 状态..."
CHANGES=$(lobster 'exec "git status --porcelain" | json | where "length > 0"' 2>&1)

if [ -z "$CHANGES" ] || echo "$CHANGES" | grep -q "^\[\]$"; then
    echo "✅ Workspace 配置已是最新，无需同步"
    exit 0
fi

echo "发现变更："
echo "$CHANGES" | jq -r '.[]' 2>/dev/null || echo "$CHANGES"
echo ""

# 步骤 4: 人工审批
echo "📋 步骤 4: 人工审批"
echo ""
read -p "确认提交到 Git？(y/N): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ 用户取消提交"
    exit 0
fi

echo ""

# 步骤 5-7: Git Commit + Push + 通知
echo "📋 步骤 5-7: 执行同步..."
lobster '
  exec "git add ." &&
  exec "git commit -m \"Lobster sync: $(date +%Y-%m-%d %H:%M)\"" &&
  exec "git push origin main" &&
  exec "echo \"✅ Workspace 同步完成！\""
' 2>&1

# 步骤 8: 更新游标
echo ""
echo "📋 步骤 8: 更新游标状态..."
COMMIT_HASH=$(git rev-parse HEAD)
cat > "$CURSOR_FILE" << EOF
{
  "workflow": "lobster-git-sync",
  "last_sync": "$(date -Iseconds)",
  "last_commit": "$COMMIT_HASH",
  "status": "completed"
}
EOF
echo "✅ 游标已更新"
echo ""

# 完成通知
echo "========================"
echo "✅ Lobster Git Sync 完成！"
echo "========================"
echo ""
echo "Commit: $(git rev-parse --short HEAD)"
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""
