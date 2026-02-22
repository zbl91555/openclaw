#!/bin/bash
# Backup workspace script with semantic descriptions

BACKUP_DIR=".backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    MESSAGE="系统自动触发的常规性工作区快照备份"
fi

# Sanitize message to build a readable but filesystem-safe filename suffix
SAFE_MSG=$(echo "$MESSAGE" | sed -e 's/[^a-zA-Z0-9\u4e00-\u9fa5]/_/g' | cut -c1-30 | sed 's/_$//')
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}_${SAFE_MSG}.tar.gz"
META_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}_${SAFE_MSG}.meta"

mkdir -p "$BACKUP_DIR"

echo "正在打包当前工作区 (排除 .git, node_modules, .backups)..."
tar -czvf "$BACKUP_FILE" --exclude='.git' --exclude='node_modules' --exclude='.backups' --exclude='.tmp' . > /dev/null

if [ $? -eq 0 ]; then
    # Write semantic metadata
    echo "File: $(basename "$BACKUP_FILE")" > "$META_FILE"
    echo "Date: $(date +'%Y-%m-%d %H:%M:%S')" >> "$META_FILE"
    echo "Message: $MESSAGE" >> "$META_FILE"
    
    echo "✅ 备份成功！"
    echo "📦 备份包位置: $BACKUP_FILE"
    echo "📝 关联语义化纪要: $MESSAGE"
else
    echo "❌ 备份过程中发生致命错误。"
    exit 1
fi
