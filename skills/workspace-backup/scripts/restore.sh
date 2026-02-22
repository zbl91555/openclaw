#!/bin/bash
# Restore workspace script exposing semantic info

BACKUP_DIR=".backups"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 错误: 请提供要还原的精准备份包名称。 (例如: backup_20231010_xxx.tar.gz)"
    exit 1
fi

FULL_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

if [ ! -f "$FULL_PATH" ]; then
    echo "❌ 错误: 找不到指定的实体备份包 - $FULL_PATH"
    exit 1
fi

# Determine corresponding meta file
META_FILE="${FULL_PATH%.tar.gz}.meta"

echo "🔄 正在从 $FULL_PATH 无痕覆盖恢复工作区中..."
tar -xzvf "$FULL_PATH" -C ./ > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ 工作区物理文件已成功强制恢复！"
    # Inform the semantic context of this restored state
    if [ -f "$META_FILE" ]; then
        MSG=$(grep "^Message: " "$META_FILE" | sed 's/^Message: //')
        echo "=========================================================="
        echo "🎉 还原里程碑：您已将时间线倒推并驻留在了"
        echo "👉 『 $MSG 』 的状态！"
        echo "=========================================================="
    else
        echo "⚠️ 警告：该备份为旧时代产物，缺失语义化描述元数据。"
    fi
else
    echo "❌ 恢复过程中底层遭遇异常错误！"
    exit 1
fi
