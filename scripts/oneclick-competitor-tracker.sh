#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
BITABLE_UPDATER="${WORKSPACE}/scripts/bitable-update-collab-status.py"
OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || true)}"
VOICE_SENDER="${WORKSPACE}/scripts/send-feishu-voice.py"
VOICE_SETTINGS="${WORKSPACE}/config/voice_settings.json"
RUNTIME_DIR="${WORKSPACE}/.runtime/pipelines"
mkdir -p "${RUNTIME_DIR}"

TRACK_TOPIC="AI Agent 平台"
TIME_WINDOW="最近7天"
TIMEOUT=2000

while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic) TRACK_TOPIC="${2:-${TRACK_TOPIC}}"; shift 2 ;;
    --window) TIME_WINDOW="${2:-${TIME_WINDOW}}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-${TIMEOUT}}"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${OPENCLAW_BIN}" || -z "${PYTHON_BIN}" ]]; then
  echo "openclaw/python3 not found in PATH" >&2
  exit 127
fi

TASK_ID="CT-$(date +%Y%m%d-%H%M%S)"
TASK_TITLE="竞品追踪-${TRACK_TOPIC}-${TIME_WINDOW}"
OUT_DIR="${RUNTIME_DIR}/${TASK_ID}"
mkdir -p "${OUT_DIR}"

send_voice_if_enabled() {
  local msg="$1"
  if [[ ! -f "${VOICE_SENDER}" ]]; then
    return 0
  fi
  local enabled
  enabled="$(${PYTHON_BIN} - <<'PY'
import json, os
p=os.path.expanduser("${VOICE_SETTINGS}")
if not os.path.exists(p):
    print("0")
else:
    try:
        c=json.load(open(p,'r',encoding='utf-8'))
        print("1" if c.get('voiceConversation',{}).get('enabled') else "0")
    except Exception:
        print("0")
PY
)"
  if [[ "${enabled}" != "1" ]]; then
    return 0
  fi
  "${PYTHON_BIN}" "${VOICE_SENDER}" --text "${msg}" >/dev/null 2>&1 || true
}

update_status() {
  local status="$1"; local owner="$2"; local module="$3"; local link="${4:-}"; local acceptance="${5:-}"
  if [[ -f "${BITABLE_UPDATER}" ]]; then
    "${PYTHON_BIN}" "${BITABLE_UPDATER}" \
      --task-id "${TASK_ID}" \
      --title "${TASK_TITLE}" \
      --status "${status}" \
      --owner "${owner}" \
      --module "${module}" \
      --link "${link}" \
      --acceptance "${acceptance}" \
      --upsert >/dev/null 2>&1 || true
  fi
}

PROMPT_FILE="${OUT_DIR}/prompt.txt"
cat >"${PROMPT_FILE}" <<EOT
[task_id:${TASK_ID}]
请执行“竞品追踪”单次周期任务：主题=${TRACK_TOPIC}，时间窗=${TIME_WINDOW}。

目标：固定节奏采集、横向对比、输出策略建议，并更新到飞书表格。

执行要求：
1. main 统筹，research-writer 负责采集、对比、结构化输出。
2. 至少覆盖 3 个竞品：定位、核心能力、价格/商业模式、近期动态。
3. 输出策略建议：保守/进取/高风险 三档各 1 条。
4. 在飞书产出可追踪文档，并回写飞书链接。
5. 若数据不足，明确标记 BLOCKED 与补数建议。
EOT

update_status "进行中" "main" "需求澄清" "" "任务已创建，进入采集阶段"

JSON_FILE="${OUT_DIR}/result.json"
TEXT_FILE="${OUT_DIR}/result.txt"

if ! "${OPENCLAW_BIN}" agent --agent main --message "$(cat "${PROMPT_FILE}")" --json --timeout "${TIMEOUT}" >"${JSON_FILE}" 2>"${OUT_DIR}/error.log"; then
  update_status "阻塞" "main" "风险审查" "" "openclaw 调用失败"
  echo "FAILED task_id=${TASK_ID} (openclaw call failed)"
  exit 1
fi

jq -r '.result.payloads[0].text // empty' "${JSON_FILE}" >"${TEXT_FILE}"
LINK="$(grep -Eo 'https://[^ )"]*(feishu|larksuite)[^ )"]*' "${TEXT_FILE}" | head -n 1 || true)"
ACCEPT="$(head -n 2 "${TEXT_FILE}" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | cut -c1-180)"

FIX_JSON="$(${PYTHON_BIN} "${WORKSPACE}/scripts/ensure-feishu-doc-body.py" \
  --task-title "${TASK_TITLE}" \
  --text-file "${TEXT_FILE}" \
  --link "${LINK}" \
  --min-chars 300 2>/dev/null || true)"

DOC_OK=0
if [[ -n "${FIX_JSON}" ]] && echo "${FIX_JSON}" | jq -e '.ok == true' >/dev/null 2>&1; then
  DOC_OK=1
  LINK="$(echo "${FIX_JSON}" | jq -r '.final_link // empty')"
  if echo "${FIX_JSON}" | jq -e '.fixed == true' >/dev/null 2>&1; then
    ACCEPT="AUTOFIX: 文档正文自动修复并回填链接"
  fi
else
  ACCEPT="BLOCKED: doc validation/repair failed"
fi

if [[ -n "${LINK}" && "${DOC_OK}" -eq 1 ]]; then
  update_status "已完成" "research-writer" "结果汇总" "${LINK}" "${ACCEPT:-已完成并回写}"
elif [[ -n "${LINK}" && "${DOC_OK}" -eq 0 ]]; then
  update_status "阻塞" "main" "风险审查" "${LINK}" "${ACCEPT}"
elif grep -Eqi '(BLOCKED|阻塞|失败|error)' "${TEXT_FILE}"; then
  update_status "阻塞" "main" "风险审查" "" "${ACCEPT:-存在阻塞}"
else
  update_status "进行中" "main" "编码实现" "" "${ACCEPT:-流程进行中}"
fi

echo "task_id=${TASK_ID}"
echo "out_dir=${OUT_DIR}"
echo "link=${LINK:-N/A}"
VOICE_BRIEF="任务 ${TASK_ID} 已处理。状态：$( [[ "${DOC_OK}" -eq 1 ]] && echo 已完成 || echo 进行中 )。${ACCEPT}。${LINK:+文档链接已生成。}"
send_voice_if_enabled "${VOICE_BRIEF}"

echo "result:"
cat "${TEXT_FILE}"
