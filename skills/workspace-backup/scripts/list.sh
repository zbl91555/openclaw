#!/bin/bash
# List workspace backup history via git log

echo "================ 📜 工作区 GitHub 备份历史 ================"
echo ""

# Check if we're in a git repo
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ 当前目录不是 Git 仓库，无法查看备份历史。"
    exit 1
fi

# Show commit history with index
git log --oneline --format="%C(yellow)%h%Creset  %C(cyan)%ad%Creset  %s" --date=format:"%Y-%m-%d %H:%M" | head -20 | nl -w2 -s". "

echo ""
TOTAL=$(git rev-list --count HEAD 2>/dev/null || echo "?")
echo "📊 历史快照总数: $TOTAL 条"
echo "🌐 远端仓库: $(git remote get-url origin 2>/dev/null || echo '未配置')"
echo ""
echo "💡 提示：使用 Commit ID（前7位）即可还原至对应状态。"
echo "   例如: restore.sh abc1234"
