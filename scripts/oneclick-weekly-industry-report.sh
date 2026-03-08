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

TOPIC="AI Agent 行业"
WEEK_TAG="$(date +%G-W%V)"
TIMEOUT=2400
TASK_ID_OVERRIDE=""
CONFIRM_BRAINSTORM=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic) TOPIC="${2:-${TOPIC}}"; shift 2 ;;
    --week) WEEK_TAG="${2:-${WEEK_TAG}}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-${TIMEOUT}}"; shift 2 ;;
    --task-id) TASK_ID_OVERRIDE="${2:-}"; shift 2 ;;
    --confirm-brainstorm) CONFIRM_BRAINSTORM=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${OPENCLAW_BIN}" || -z "${PYTHON_BIN}" ]]; then
  echo "openclaw/python3 not found in PATH" >&2
  exit 127
fi

TASK_TITLE="周度行业研究-${TOPIC}-${WEEK_TAG}"
LOCK_KEY="$(printf '%s' "${TASK_TITLE}" | shasum | awk '{print $1}')"
LOCK_PATH="${LOCK_DIR}/${LOCK_KEY}.lock"

if ! mkdir "${LOCK_PATH}" 2>/dev/null; then
  echo "SKIP duplicate trigger: lock exists for ${TASK_TITLE}"
  exit 0
fi
trap 'rmdir "${LOCK_PATH}" 2>/dev/null || true' EXIT

find_existing_task_id() {
  "${PYTHON_BIN}" - <<'PY'
import json, urllib.request

cfg = json.load(open('/Users/mudandan/.openclaw/openclaw.json'))
app_id = cfg['channels']['feishu']['accounts']['main']['appId']
app_secret = cfg['channels']['feishu']['accounts']['main']['appSecret']

req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode(),
    headers={'Content-Type': 'application/json; charset=utf-8'},
    method='POST',
)
token = json.load(urllib.request.urlopen(req))['tenant_access_token']

title = open('/tmp/.oc_task_title', 'r', encoding='utf-8').read().strip()
url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/It3vblOqwa1Exqsy2bKchI2wnUe/tables/tblEnjzZm9KN0kOm/records?page_size=500'
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
res = json.load(urllib.request.urlopen(req))
items = res.get('data', {}).get('items', [])

candidates = []
for it in items:
    f = it.get('fields', {})
    if f.get('任务标题') == title and f.get('交付状态') == '进行中' and f.get('task_id'):
        candidates.append((f.get('最近更新时间') or '', f.get('task_id')))

candidates.sort(reverse=True)
print(candidates[0][1] if candidates else '')
PY
}

write_brainstorm_card() {
  local file="$1"
  cat >"${file}" <<EOT
# 脑暴卡片

- task_id: ${TASK_ID}
- 主题: ${TOPIC}
- 周次: ${WEEK_TAG}

## 目标
- 产出一篇可发布到飞书知识库的周报，包含 5 条关键结论 + 3 条策略建议。

## 受众
- 管理层（看结论和决策项）
- 执行层（看策略动作与落地节奏）

## 结构草案
1. 本周行业关键变化
2. 竞品动态与对标
3. 机会/风险判断
4. 策略建议（保守/进取/高风险）
5. 下周执行建议

## 风险
- 数据源不足或时效性不够
- 观点不聚焦，结论不可执行

## 验收标准
- 必须有飞书文档链接
- 正文通过最小字符数门禁
- 结论和策略可执行

## 确认口令
确认脑暴 task_id=${TASK_ID}
EOT
}

print_brainstorm_card() {
  local file="$1"
  echo "===== 脑暴卡片（请先确认） ====="
  cat "${file}"
  echo "===== 脑暴卡片结束 ====="
  echo "确认后执行：skr-dispatch.sh --run 3 --req \"确认脑暴\" --task-id \"${TASK_ID}\""
}

printf '%s' "${TASK_TITLE}" > /tmp/.oc_task_title
EXISTING_TASK_ID="$(find_existing_task_id || true)"
rm -f /tmp/.oc_task_title

if [[ -n "${TASK_ID_OVERRIDE}" ]]; then
  TASK_ID="${TASK_ID_OVERRIDE}"
elif [[ -n "${EXISTING_TASK_ID}" ]]; then
  TASK_ID="${EXISTING_TASK_ID}"
else
  TASK_ID="WR-${WEEK_TAG}-$(date +%m%d%H%M%S)"
fi

# 防止“未经过脑暴就确认执行”
if [[ "${CONFIRM_BRAINSTORM}" -eq 1 && -z "${TASK_ID_OVERRIDE}" && -z "${EXISTING_TASK_ID}" ]]; then
  echo "ERROR: 未找到待确认脑暴任务，请先执行 skr 3 生成脑暴卡片"
  exit 2
fi

OUT_DIR="${RUNTIME_DIR}/${TASK_ID}"
mkdir -p "${OUT_DIR}"
BRAINSTORM_FILE="${OUT_DIR}/brainstorm-card.md"

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

if [[ "${CONFIRM_BRAINSTORM}" -ne 1 ]]; then
  if [[ ! -f "${BRAINSTORM_FILE}" ]]; then
    write_brainstorm_card "${BRAINSTORM_FILE}"
  fi
  update_status "进行中" "main" "需求澄清" "" "脑暴卡片已生成，待你确认脑暴"
  echo "task_id=${TASK_ID}"
  echo "status=进行中"
  echo "reason=brainstorm_pending"
  echo "brainstorm=${BRAINSTORM_FILE}"
  print_brainstorm_card "${BRAINSTORM_FILE}"
  exit 0
fi

if [[ ! -f "${BRAINSTORM_FILE}" ]]; then
  echo "ERROR: 找不到脑暴卡片，请先执行 skr 3 生成脑暴卡片后再确认"
  exit 2
fi

PROMPT_FILE="${OUT_DIR}/prompt.txt"
cat >"${PROMPT_FILE}" <<EOT
[task_id:${TASK_ID}]
脑暴已确认。请执行“周度行业研究 -> 一键出文”完整链路，主题：${TOPIC}，周次：${WEEK_TAG}。

强约束：
1. 仅通过 main 统筹，研究与成稿由 research-writer 一体完成。
2. research-writer 先用 NotebookLM + research 产出研究包和可引用数据源。
3. 然后用 codex-review 输出结构拆解（受众/观点/大纲/风险）。
4. research-writer 基于研究包成文，并在必要时回核 NotebookLM 数据源。
5. 最终发布到飞书知识库，返回：
   - 文档链接（必须可访问）
   - 5 条关键结论
   - 3 条策略建议
6. 若任一步骤缺失，请返回 BLOCKED 原因，不得伪造完成。
EOT

update_status "进行中" "main" "需求澄清" "" "脑暴已确认，进入研究阶段"

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
  update_status "已完成" "research-writer" "知识沉淀" "${LINK}" "${ACCEPT:-已完成并发布}"
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
