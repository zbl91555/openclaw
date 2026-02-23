#!/bin/bash
# OpenClaw Workspace Git 初始化脚本
# 用途：将工作区初始化为 Git 仓库，关联远程备份

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
GIT_REMOTE=""

echo "🦞 OpenClaw Workspace Git 初始化"
echo "================================"
echo ""

# 询问远程仓库地址
read -p "请输入 GitHub 仓库地址（如 git@github.com:username/repo.git，留空则仅本地 Git）： " GIT_REMOTE

echo ""
echo "📁 工作区目录：$WORKSPACE_DIR"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 检查是否已初始化
if [ -d ".git" ]; then
    echo "⚠️  Git 仓库已存在"
    read -p "是否重新初始化？(y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "❌ 取消初始化"
        exit 1
    fi
fi

# 初始化 Git
echo "🔄 初始化 Git 仓库..."
git init

# 创建 .gitignore
echo "📝 创建 .gitignore..."
cat > .gitignore << 'EOF'
# ===========================
# 敏感信息（必须忽略）
# ===========================
.env
credentials/
auth-profiles.json
*.key
*.pem

# ===========================
# 会话日志（隐私数据）
# ===========================
sessions/*.jsonl
*.jsonl
logs/
.cache/

# ===========================
# 沙箱环境
# ===========================
.docker/
sandboxes/
tmp/
*.tmp

# ===========================
# 系统文件
# ===========================
.DS_Store
Thumbs.db
*.swp
*.swo
*~

# ===========================
# Lobster 状态（本地状态）
# ===========================
.lobster/state/

# ===========================
# 需要保留的文件（例外规则）
# ===========================
!MEMORY.md
!AGENTS.md
!TOOLS.md
!HEARTBEAT.md
!articles/*.md
EOF

# 创建 .gitattributes（用于加密敏感文件）
echo "📝 创建 .gitattributes..."
cat > .gitattributes << 'EOF'
# 如果需要加密敏感文件，取消以下注释
# .env filter=git-crypt diff=git-crypt
# credentials/* filter=git-crypt diff=git-crypt
EOF

# 首次提交
echo "📦 首次提交..."
git add .
git commit -m "Initial commit: OpenClaw workspace backup

- 配置 Git 备份工作流
- 添加 .gitignore 保护敏感信息
-  Lobster git-sync 工作流已配置

自动生成"

# 关联远程仓库（如果提供了地址）
if [ ! -z "$GIT_REMOTE" ]; then
    echo "🔗 关联远程仓库：$GIT_REMOTE"
    git remote add origin "$GIT_REMOTE"
    git branch -M main
    
    # 尝试推送
    echo "🚀 推送到远程仓库..."
    git push -u origin main
    echo ""
    echo "✅ 远程关联成功！"
else
    echo "⚠️  仅初始化本地 Git，未关联远程仓库"
    echo ""
    echo "如需关联远程仓库，执行："
    echo "  git remote add origin <your-repo-url>"
    echo "  git push -u origin main"
fi

# 创建 Lobster 状态目录
echo "📁 创建 Lobster 状态目录..."
mkdir -p ~/.lobster/state

# 初始化游标文件
cat > ~/.lobster/state/git-sync.cursor.json << EOF
{
  "workflow": "git-sync",
  "initialized_at": "$(date -Iseconds)",
  "last_sync": null,
  "last_commit": "$(git rev-parse HEAD)",
  "status": "initialized"
}
EOF

echo ""
echo "================================"
echo "✅ Git 初始化完成！"
echo "================================"
echo ""
echo "📋 下一步："
echo ""
echo "1. 测试 Lobster 工作流："
echo "   lobster run ~/.openclaw/workspace/git-sync.lobster"
echo ""
echo "2. 配置定时任务（每天凌晨 4:30 自动同步）："
echo "   openclaw cron add \"30 4 * * *\" \"lobster run ~/.openclaw/workspace/git-sync.lobster\""
echo ""
echo "3. 查看 Git 状态："
echo "   cd ~/.openclaw/workspace && git status"
echo ""
echo "4. 查看 Lobster 状态："
echo "   cat ~/.lobster/state/git-sync.cursor.json"
echo ""
