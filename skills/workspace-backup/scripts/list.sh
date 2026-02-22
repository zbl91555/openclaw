#!/bin/bash
# List available workspace backups with their semantic context

BACKUP_DIR=".backups"

# Check if backup files exist securely
if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/*.meta 2>/dev/null)" ]; then
    echo "📂 当前没有任何附带语义化描述的工作区备份历史。"
    exit 0
fi

echo "================ 当前可用的时光机历史记录 ================"

# Parse and print each metadata file cleanly
for meta in "$BACKUP_DIR"/*.meta; do
    if [ -f "$meta" ]; then
        FILE=$(grep "^File: " "$meta" | sed 's/^File: //')
        MSG=$(grep "^Message: " "$meta" | sed 's/^Message: //')
        DATE=$(grep "^Date: " "$meta" | sed 's/^Date: //')
        
        # Verify the actual archive exists
        if [ -f "$BACKUP_DIR/$FILE" ]; then
            SIZE=$(ls -lh "$BACKUP_DIR/$FILE" | awk '{print $5}')
            echo "📝 场景状态 :【 $MSG 】"
            echo "🕒 封存时间 : $DATE"
            echo "💾 物理体积 : $SIZE"
            echo "📦 精确文件 : $FILE"
            echo "--------------------------------------------------------"
        fi
    fi
done

echo "💡 提示：您可以使用 restore 脚本配合精确文件(如: backup_xxx.tar.gz) 进行还原。"
