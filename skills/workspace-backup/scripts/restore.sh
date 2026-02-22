#!/bin/bash
# Restore workspace script

BACKUP_DIR=".backups"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 请提供要还原的备份文件名。 (例如: workspace_backup_20231010_120000.tar.gz)"
    exit 1
fi

FULL_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

if [ ! -f "$FULL_PATH" ]; then
    echo "❌ 找不到指定的备份文件: $FULL_PATH"
    exit 1
fi

echo "正在从 $FULL_PATH 恢复数据，这将会覆盖当前文件..."
tar -xzvf "$FULL_PATH" -C ./ > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ 工作区已成功恢复！"
else
    echo "❌ 恢复过程中发生错误。"
    exit 1
fi
