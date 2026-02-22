#!/bin/bash
# Backup workspace script

BACKUP_DIR=".backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/workspace_backup_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "正在打包当前工作区 (排除 .git, node_modules, .backups)..."
tar -czvf "$BACKUP_FILE" --exclude='.git' --exclude='node_modules' --exclude='.backups' --exclude='.tmp' . > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ 备份成功！文件已存至: $BACKUP_FILE"
else
    echo "❌ 备份过程中发生错误。"
    exit 1
fi
