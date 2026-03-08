#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

WEEKLY_SCRIPT="${WORKSPACE}/scripts/oneclick-weekly-industry-report.sh"
COMPETITOR_SCRIPT="${WORKSPACE}/scripts/oneclick-competitor-tracker.sh"
BOSS_SCRIPT="${WORKSPACE}/scripts/oneclick-nightly-boss-brief.sh"
HEAL_SCRIPT="${WORKSPACE}/scripts/openclaw-restart-heal.sh"
PROGRESS_SCRIPT="${WORKSPACE}/scripts/query-task-progress.py"
CANCEL_SCRIPT="${WORKSPACE}/scripts/cancel-task.py"

ACTION="list"
MENU_ID=""
REQ=""
TOPIC="AI Agent 行业"
WINDOW="最近7天"
DATE="$(date +%F)"
TIMEOUT=1800
TASK_ID=""
LATEST=3
DRY_RUN=0
CANCEL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --list) ACTION="list"; shift ;;
    --run) ACTION="run"; MENU_ID="${2:-}"; shift 2 ;;
    --req) REQ="${2:-}"; shift 2 ;;
    --topic) TOPIC="${2:-$TOPIC}"; shift 2 ;;
    --window) WINDOW="${2:-$WINDOW}"; shift 2 ;;
    --date) DATE="${2:-$DATE}"; shift 2 ;;
    --task-id) TASK_ID="${2:-}"; shift 2 ;;
    --latest) LATEST="${2:-$LATEST}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-$TIMEOUT}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --cancel) CANCEL=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

print_menu() {
  cat <<EOT
【SKR 高度定制化技能菜单 v2】
回复编号即可执行：
1. Coding 冲刺（Linus 执行 + Codex Review 门禁）
2. 老板汇报（进度/风险/明日计划/待决策）
3. 专业写作（先脑暴确认，再执行；Writer 一轮迭代）
4. 竞品追踪（固定节奏采集/对比/策略建议）
5. OpenClaw 配置体检与自动修复（网关异常兜底）
6. 任务进度查询/取消（按 task_id 或最近任务）

可附参数：
- 3 可带 topic；首次会返回脑暴卡片正文，需“确认脑暴”后继续
- 4 可带 topic/window（如“AI 编程助手/最近14天”）
- 2 可带 date（如 2026-02-26）
- 6 查询：--task-id <id> 或 --latest 3
- 6 取消：--cancel --task-id <id>
EOT
}

run_cmd() {
  local cmd="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] ${cmd}"
    return 0
  fi
  eval "$cmd"
}

if [[ "$ACTION" == "list" ]]; then
  print_menu
  exit 0
fi

if [[ -z "$MENU_ID" ]]; then
  echo "--run requires menu id" >&2
  exit 2
fi

if [[ -z "$OPENCLAW_BIN" ]]; then
  echo "openclaw command not found" >&2
  exit 127
fi

case "$MENU_ID" in
  1)
    TASKX="COD-$(date +%Y%m%d-%H%M%S)"
    if [[ -z "$REQ" ]]; then
      REQ="请描述 coding 目标与验收标准"
    fi
    MSG="[task_id:${TASKX}] 请按 Coding 冲刺模式执行：\n- 由 main 派发给 swe\n- swe 可先 subagent 并行实现\n- 复杂/高风险改动必须 codex review 才可交付\n需求：${REQ}\n输出：状态/产出/风险/ETA + 交付链接"
    run_cmd "\"${OPENCLAW_BIN}\" agent --agent main --message \"${MSG}\" --timeout \"${TIMEOUT}\""
    ;;
  2)
    run_cmd "\"${BOSS_SCRIPT}\" --date \"${DATE}\" --timeout \"${TIMEOUT}\""
    ;;
  3)
    CMD="\"${WEEKLY_SCRIPT}\" --topic \"${TOPIC}\" --timeout \"${TIMEOUT}\""
    if echo "${REQ}" | grep -Eqi '确认脑暴|confirm'; then
      CMD="${CMD} --confirm-brainstorm"
    fi
    if [[ -n "${TASK_ID}" ]]; then
      CMD="${CMD} --task-id \"${TASK_ID}\""
    fi
    run_cmd "${CMD}"
    ;;
  4)
    run_cmd "\"${COMPETITOR_SCRIPT}\" --topic \"${TOPIC}\" --window \"${WINDOW}\" --timeout \"${TIMEOUT}\""
    ;;
  5)
    run_cmd "\"${HEAL_SCRIPT}\""
    ;;
  6)
    if [[ "$CANCEL" -eq 1 ]]; then
      if [[ -z "$TASK_ID" ]]; then
        echo "--cancel requires --task-id" >&2
        exit 2
      fi
      run_cmd "python3 \"${CANCEL_SCRIPT}\" --task-id \"${TASK_ID}\" --reason \"用户通过 SKR 取消\""
    else
      if [[ -n "$TASK_ID" ]]; then
        run_cmd "python3 \"${PROGRESS_SCRIPT}\" --task-id \"${TASK_ID}\""
      else
        run_cmd "python3 \"${PROGRESS_SCRIPT}\" --latest \"${LATEST}\""
      fi
    fi
    ;;
  *)
    echo "Unsupported menu id: ${MENU_ID}" >&2
    exit 2
    ;;
esac
