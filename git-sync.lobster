#!/usr/bin/env lobster
# Workspace Git Backup & Sync
# 用法：lobster run git-sync.lobster

name: workspace-git-sync
description: 安全地将 OpenClaw Workspace 配置变更备份到 GitHub

# Lobster 工作流格式说明：
# https://github.com/openclaw/lobster
# 
# 由于 Lobster 还在早期开发中，YAML 格式支持有限
# 推荐使用命令行方式运行 Lobster 管道

# 等效的命令行：
# lobster 'git -C ~/.openclaw/workspace status --porcelain | json | where "length > 0" | git -C ~/.openclaw/workspace add . && git -C ~/.openclaw/workspace commit -m "Lobster sync" && git -C ~/.openclaw/workspace push origin main'
