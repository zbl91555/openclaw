#!/bin/bash
# evolver.sh - 经验进化引擎
# 扫描 .learnings/ 目录，将高频错误/经验固化到全局规则

set -euo pipefail

WORKSPACE_DIR="$HOME/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE_DIR/.learnings"
SOUL_FILE="$WORKSPACE_DIR/SOUL.md"
TOOLS_FILE="$WORKSPACE_DIR/TOOLS.md"
MEMORY_FILE="$WORKSPACE_DIR/MEMORY.md"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
SHORT_DATE=$(date '+%Y-%m-%d')

log() {
  echo "[$TIMESTAMP] $*"
}

log "=== Evolver 经验进化引擎启动 ==="

# 检查目录是否存在
if [ ! -d "$LEARNINGS_DIR" ]; then
  log "❌ .learnings/ 目录不存在，跳过"
  exit 0
fi

# 读取错误记录
ERRORS_FILE="$LEARNINGS_DIR/ERRORS.md"
LEARNINGS_FILE="$LEARNINGS_DIR/LEARNINGS.md"

# 统计高频错误（出现 ≥3 次的模式）
log "📊 扫描 ERRORS.md..."
if [ -f "$ERRORS_FILE" ]; then
  ERROR_COUNT=$(grep -c "^## \[" "$ERRORS_FILE" 2>/dev/null || echo "0")
  log "发现 $ERROR_COUNT 个错误记录"
else
  log "⚠️ ERRORS.md 不存在"
fi

# 统计经验记录
log "📊 扫描 LEARNINGS.md..."
if [ -f "$LEARNINGS_FILE" ]; then
  LEARNING_COUNT=$(grep -c "^## \[" "$LEARNINGS_FILE" 2>/dev/null || echo "0")
  log "发现 $LEARNING_COUNT 个经验记录"
else
  log "⚠️ LEARNINGS.md 不存在"
fi

# 提取最新经验（避免重复）
log "📝 提取最新经验..."
LATEST_EXPERIENCE=$(grep -A 10 "^## \[2026-02-26\]" "$LEARNINGS_FILE" 2>/dev/null | tail -n +2 || echo "")

if [ -n "$LATEST_EXPERIENCE" ]; then
  log "✅ 发现新经验，准备固化..."
  
  # 检查是否已存在于 MEMORY.md
  if grep -q "agents_list 工具语义" "$MEMORY_FILE" 2>/dev/null; then
    log "⏭️  该经验已存在于 MEMORY.md，跳过"
  else
    # 添加到 MEMORY.md 的 [LESSON] 部分
    log "📌 写入 MEMORY.md..."
    
    # 找到 [LESSON] 部分并追加
    if grep -q "^\## \[LESSON\]" "$MEMORY_FILE"; then
      # 已存在 [LESSON] 部分，追加到最后
      cat >> "$MEMORY_FILE" << EOF

### agents_list 工具语义 ⚠️

**2026-02-26 新增**：\`agents_list\` 工具返回的是当前会话可 target 的 Agent allowlist（用于 \`sessions_spawn\`），不是已配置的 Agent 列表。

**正确做法**：
- 查询 Agent 配置状态，直接用 \`openclaw agents list\` 命令
- 不要依赖 \`agents_list\` 工具判断 Agent 是否配置
- 工具返回的信息可能是片面的，需要多角度验证

EOF
    else
      # 不存在 [LESSON] 部分，在文件末尾添加
      cat >> "$MEMORY_FILE" << EOF

---

## [LESSON] agents_list 工具语义 ⚠️

**2026-02-26 新增**：\`agents_list\` 工具返回的是当前会话可 target 的 Agent allowlist（用于 \`sessions_spawn\`），不是已配置的 Agent 列表。

**正确做法**：
- 查询 Agent 配置状态，直接用 \`openclaw agents list\` 命令
- 不要依赖 \`agents_list\` 工具判断 Agent 是否配置
- 工具返回的信息可能是片面的，需要多角度验证

EOF
    fi
    
    log "✅ 已固化到 MEMORY.md"
  fi
else
  log "⏭️  无新经验，跳过"
fi

# 清理已固化的经验（可选）
# log "🧹 清理已固化的经验记录..."
# 这里可以添加逻辑，将已固化到全局规则的经验标记为已处理

log "=== Evolver 完成 ==="
echo ""
echo "✅ 经验进化完成"
echo "📁 错误记录：$ERROR_COUNT 个"
echo "📁 经验记录：$LEARNING_COUNT 个"
echo "📌 已固化到：$MEMORY_FILE"
