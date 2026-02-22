#!/bin/bash
# Restore workspace to a specific git commit

COMMIT="$1"

if [ -z "$COMMIT" ]; then
    echo "❌ 错误：请提供要还原的 Commit ID。"
    echo "   使用方式: restore.sh <commit_id>"
    echo "   例如:     restore.sh abc1234"
    echo ""
    echo "💡 使用 list.sh 查看所有可用历史快照及其 Commit ID。"
    exit 1
fi

# Validate commit exists
if ! git cat-file -t "$COMMIT" > /dev/null 2>&1; then
    echo "❌ 错误：在仓库中找不到 Commit ID '$COMMIT'，请确认拼写是否正确。"
    echo "💡 使用 list.sh 查看所有有效的备份历史。"
    exit 1
fi

# Get commit message for semantic display
COMMIT_MSG=$(git log --format="%s" -n 1 "$COMMIT")
COMMIT_DATE=$(git log --format="%ad" --date=format:"%Y-%m-%d %H:%M" -n 1 "$COMMIT")
COMMIT_FULL=$(git rev-parse "$COMMIT")

echo ""
echo "⚠️  警告：即将将工作区还原至以下历史状态："
echo "   🔖 Commit: $COMMIT"
echo "   📝 备注:   $COMMIT_MSG"
echo "   🕒 时间:   $COMMIT_DATE"
echo ""
echo "🔄 正在暂存当前未提交的变更（如有）..."

# Stash any current uncommitted changes to avoid data loss
git stash push -m "restore-stash-before-$COMMIT" --include-untracked > /dev/null 2>&1
STASHED=$?

echo "⏪ 正在切换至目标快照..."

# Use checkout to restore working tree to target commit state
git checkout "$COMMIT_FULL" -- .

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================================="
    echo "✅ 还原成功！工作区已恢复至："
    echo "   👉 『 $COMMIT_MSG 』"
    echo "   🕒 时间: $COMMIT_DATE"
    echo "=========================================================="
    echo ""
    echo "📋 当前 HEAD 仍指向最新 commit，文件内容已还原为 $COMMIT 时的状态。"
    echo "   如需永久回滚并推送到 GitHub，请执行："
    echo "   git revert <中间所有commit> 或 git reset --hard $COMMIT && git push --force"
    echo ""
    if [ "$STASHED" -eq 0 ]; then
        echo "💾 您之前未提交的变更已被暂存（git stash）。"
        echo "   如需恢复，请执行: git stash pop"
    fi
else
    echo "❌ 还原过程中发生错误！"
    # Restore stash if we stashed
    if [ "$STASHED" -eq 0 ]; then
        git stash pop > /dev/null 2>&1
        echo "♻️  已自动恢复您之前未提交的变更。"
    fi
    exit 1
fi
