#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
BITABLE_UPDATER="${WORKSPACE}/scripts/bitable-update-collab-status.py"
OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || true)}"
VOICE_SENDER="${WORKSPACE}/scripts/send-feishu-voice.py"
VOICE_SETTINGS="${WORKSPACE}/config/voice_settings.json"
RUNTIME_DIR="${WORKSPACE}/.runtime/pipelines"
LOCK_DIR="${RUNTIME_DIR}/.locks"
mkdir -p "${RUNTIME_DIR}" "${LOCK_DIR}"

REPORT_DATE="$(date +%F)"
TIMEOUT=900
TASK_ID_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) REPORT_DATE="${2:-${REPORT_DATE}}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-${TIMEOUT}}"; shift 2 ;;
    --task-id) TASK_ID_OVERRIDE="${2:-}"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${OPENCLAW_BIN}" || -z "${PYTHON_BIN}" ]]; then
  echo "openclaw/python3 not found in PATH" >&2
  exit 127
fi

LOCK_KEY="NB-${REPORT_DATE}"
LOCK_PATH="${LOCK_DIR}/${LOCK_KEY}.lock"
if ! mkdir "${LOCK_PATH}" 2>/dev/null; then
  echo "SKIP duplicate trigger: lock exists for ${LOCK_KEY}"
  exit 0
fi
trap 'rmdir "${LOCK_PATH}" 2>/dev/null || true' EXIT

TASK_ID="${TASK_ID_OVERRIDE:-NB-${REPORT_DATE//-/}-$(date +%H%M%S)}"
TASK_TITLE="老板汇报-${REPORT_DATE}"
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
请执行“老板汇报模式”日报汇总，日期：${REPORT_DATE}。

输出结构必须为：
1) 今日进度（按任务列出完成/进行中）
2) 风险与阻塞（含影响和应对）
3) 明日计划（按 owner）
4) 需你决策事项（每项含建议选项）

要求：
- main 统一汇总，不要群聊刷屏。
- 产出发布到飞书文档，并返回链接。
- 若数据不足，明确写 BLOCKED 与缺失数据项。
EOT

update_status "进行中" "main" "结果汇总" "" "任务已创建，进入汇总阶段"

JSON_FILE="${OUT_DIR}/result.json"
TEXT_FILE="${OUT_DIR}/result.txt"
ERR_FILE="${OUT_DIR}/error.log"
: > "${ERR_FILE}"

# 外层硬超时 + 一次重试，规避 openclaw agent 无输出挂起
if ! "${PYTHON_BIN}" - "$OPENCLAW_BIN" "$PROMPT_FILE" "$JSON_FILE" "$ERR_FILE" "$TIMEOUT" <<'PY'
import os
import subprocess
import sys
import time

openclaw_bin = sys.argv[1]
prompt_file = sys.argv[2]
json_file = sys.argv[3]
err_file = sys.argv[4]
timeout = int(sys.argv[5])

with open(prompt_file, 'r', encoding='utf-8') as f:
    msg = f.read()

cmd = [openclaw_bin, 'agent', '--agent', 'main', '--message', msg, '--json', '--timeout', str(timeout)]
hard_timeout = max(45, min(timeout + 60, 600))

for attempt in (1, 2):
    with open(err_file, 'ab') as ef:
        ef.write(f"\n[attempt {attempt}] cmd={' '.join(cmd[:4])} ...\n".encode('utf-8'))
    with open(json_file, 'wb') as out, open(err_file, 'ab') as ef:
        p = subprocess.Popen(cmd, stdout=out, stderr=ef)
        try:
            rc = p.wait(timeout=hard_timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            with open(err_file, 'ab') as ef2:
                ef2.write(f"[hard-timeout] {hard_timeout}s\n".encode('utf-8'))
            rc = 124

    size = os.path.getsize(json_file) if os.path.exists(json_file) else 0
    if rc == 0 and size > 0:
        print('ok')
        sys.exit(0)

    with open(err_file, 'ab') as ef:
        ef.write(f"[attempt {attempt} failed] rc={rc}, json_size={size}\n".encode('utf-8'))
    time.sleep(2)

print('failed')
sys.exit(1)
PY
then
  update_status "阻塞" "main" "风险审查" "" "openclaw 调用失败或超时（已重试一次）"
  echo "FAILED task_id=${TASK_ID} (openclaw call failed/hung)"
  exit 1
fi

jq -r '.result.payloads[0].text // empty' "${JSON_FILE}" >"${TEXT_FILE}"
LINK="$(grep -Eo 'https://[^ )"]*(feishu|larksuite)[^ )"]*' "${TEXT_FILE}" | head -n 1 || true)"
ACCEPT="$(head -n 2 "${TEXT_FILE}" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | cut -c1-180)"

FIX_JSON="$(${PYTHON_BIN} "${WORKSPACE}/scripts/ensure-feishu-doc-body.py" \
  --task-title "${TASK_TITLE}" \
  --text-file "${TEXT_FILE}" \
  --link "${LINK}" \
  --min-chars 120 2>/dev/null || true)"

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
  update_status "已完成" "main" "结果汇总" "${LINK}" "${ACCEPT:-已完成并发布}"
elif [[ -n "${LINK}" && "${DOC_OK}" -eq 0 ]]; then
  update_status "阻塞" "main" "风险审查" "${LINK}" "${ACCEPT}"
elif grep -Eqi '(BLOCKED|阻塞|失败|error)' "${TEXT_FILE}"; then
  update_status "阻塞" "main" "风险审查" "" "${ACCEPT:-存在阻塞}"
else
  update_status "进行中" "main" "结果汇总" "" "${ACCEPT:-流程进行中}"
fi

echo "task_id=${TASK_ID}"
echo "out_dir=${OUT_DIR}"
echo "link=${LINK:-N/A}"
VOICE_BRIEF="任务 ${TASK_ID} 已处理。状态：$( [[ "${DOC_OK}" -eq 1 ]] && echo 已完成 || echo 进行中 )。${ACCEPT}。${LINK:+文档链接已生成。}"
send_voice_if_enabled "${VOICE_BRIEF}"

echo "result:"
cat "${TEXT_FILE}"
