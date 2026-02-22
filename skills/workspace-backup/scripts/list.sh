#!/bin/bash
BACKUP_DIR=".backups"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "当前没有备份目录 ($BACKUP_DIR)。"
    exit 0
fi

echo "当前可用的备份文件列表："
ls -lh "$BACKUP_DIR" | awk '{print $5, $6, $7, $8, $9}'
