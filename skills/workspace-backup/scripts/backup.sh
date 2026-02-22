#!/bin/bash
# Backup workspace by committing and pushing to GitHub

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    MESSAGE="系统自动触发的常规性工作区快照备份"
fi

echo "📦 正在将当前工作区变更提交到 GitHub..."

# Stage all changes
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
    echo "ℹ️  当前工作区没有任何变更，无需备份。"
    echo "💡 最新的 commit 即为您当前的工作区状态："
    git log --oneline -1
    exit 0
fi

# --- Build detailed commit message body ---

# Count staged changes by type
ADDED=$(git diff --cached --name-status | grep -c '^A')
MODIFIED=$(git diff --cached --name-status | grep -c '^M')
DELETED=$(git diff --cached --name-status | grep -c '^D')
RENAMED=$(git diff --cached --name-status | grep -c '^R')
TOTAL=$((ADDED + MODIFIED + DELETED + RENAMED))

# Get diff stats (insertions/deletions line count)
STAT=$(git diff --cached --stat | tail -1)

# Get list of changed files (max 20 to keep message readable)
CHANGED_FILES=$(git diff --cached --name-status | head -20 | awk '
    /^A/ { print "  + [新增] " $2 }
    /^M/ { print "  ~ [修改] " $2 }
    /^D/ { print "  - [删除] " $2 }
    /^R/ { print "  > [重命名] " $3 }
')
OVERFLOW=$(git diff --cached --name-status | wc -l | tr -d ' ')
if [ "$OVERFLOW" -gt 20 ]; then
    REMAINING=$((OVERFLOW - 20))
    CHANGED_FILES="$CHANGED_FILES
  ... 及其他 $REMAINING 个文件"
fi

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# Get timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

# Compose full commit message
COMMIT_MSG="${MESSAGE}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 变更摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕒 备份时间 : ${TIMESTAMP}
🌿 分支     : ${BRANCH}
📊 变更统计 : 共 ${TOTAL} 个文件（新增 ${ADDED} | 修改 ${MODIFIED} | 删除 ${DELETED} | 重命名 ${RENAMED}）
📈 行变更   : ${STAT}

📁 变更文件列表
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${CHANGED_FILES}"

# Commit with detailed message
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
    echo "❌ 提交失败，请检查 git 配置。"
    exit 1
fi

# Push to remote
echo "🚀 正在推送到 GitHub..."
git push

if [ $? -eq 0 ]; then
    COMMIT_HASH=$(git rev-parse --short HEAD)
    echo ""
    echo "✅ 备份成功！"
    echo "📝 语义化描述 : ${MESSAGE}"
    echo "🔖 Commit ID  : ${COMMIT_HASH}"
    echo "📊 变更统计   : ${TOTAL} 个文件，${STAT}"
    echo "🌐 已同步至 GitHub 远端仓库"
else
    echo "❌ 推送到 GitHub 失败，请检查网络连接或远端仓库权限。"
    echo "⚠️  本地 commit 已创建 ($(git rev-parse --short HEAD))，但未同步到远端。"
    exit 1
fi
