#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
CONFIG_PATH="$STATE_DIR/openclaw.json"
LOG_DIR="$STATE_DIR/logs"
GATEWAY_LOG="$LOG_DIR/gateway.log"
GATEWAY_ERR_LOG="$LOG_DIR/gateway.err.log"
WORKDIR="${OPENCLAW_GUARD_WORKDIR:-$HOME/Documents/New project}"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUNTIME_DIR="${TMPDIR:-/tmp}/openclaw-guard"
mkdir -p "$RUNTIME_DIR"

INFO_LOG="$RUNTIME_DIR/restart-heal-$STAMP.log"
CONTEXT_FILE="$RUNTIME_DIR/restart-heal-context-$STAMP.txt"
export PATH="/Users/mudandan/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"
CODEX_BIN="${CODEX_BIN:-$(command -v codex || true)}"

log() {
  printf '%s %s\n' "[$(date '+%Y-%m-%d %H:%M:%S')]" "$*" | tee -a "$INFO_LOG"
}

health_ok() {
  "$OPENCLAW_BIN" gateway health >/dev/null 2>&1
}

restart_and_check() {
  log "Restarting gateway..."
  if ! "$OPENCLAW_BIN" gateway restart >>"$INFO_LOG" 2>&1; then
    log "restart command returned non-zero"
    return 1
  fi
  sleep 2
  if health_ok; then
    log "Gateway health check passed"
    return 0
  fi
  log "Gateway health check failed"
  return 1
}

collect_context() {
  {
    echo "=== openclaw gateway status ==="
    "$OPENCLAW_BIN" gateway status || true
    echo
    echo "=== openclaw gateway health ==="
    "$OPENCLAW_BIN" gateway health || true
    echo
    echo "=== tail gateway.err.log ==="
    tail -n 200 "$GATEWAY_ERR_LOG" 2>/dev/null || true
    echo
    echo "=== tail gateway.log ==="
    tail -n 200 "$GATEWAY_LOG" 2>/dev/null || true
  } >"$CONTEXT_FILE"
}

run_codex_repair() {
  log "Invoking codex auto-repair..."
  "$CODEX_BIN" exec \
    --skip-git-repo-check \
    --full-auto \
    --cd "$WORKDIR" \
    --add-dir "$STATE_DIR" \
    --output-last-message "$RUNTIME_DIR/codex-repair-$STAMP.txt" \
    "OpenClaw gateway restart failed. Read $CONTEXT_FILE and repair only $CONFIG_PATH so gateway can start.\
Rules:\
1) Only edit files under $STATE_DIR.\
2) Fix the minimal root cause from logs (schema/JSON/channel config).\
3) Keep current Feishu routing intent for main/swe/research-writer bindings.\
4) After edit, run: openclaw gateway restart && openclaw gateway health.\
5) If first fix fails, do one more minimal fix and re-check health.\
6) At the end, print a concise summary of changed keys." \
    >>"$INFO_LOG" 2>&1
}

restore_backup() {
  local latest_backup
  latest_backup=""
  while IFS= read -r candidate; do
    if jq -e '[.bindings[]?.match? | has("conversationId")] | any' "$candidate" >/dev/null 2>&1; then
      continue
    fi
    latest_backup="$candidate"
    break
  done < <(ls -1t "$CONFIG_PATH".guard.bak.* 2>/dev/null || true)

  if [[ -z "$latest_backup" ]]; then
    log "No valid guard backup found"
    return 0
  fi

  log "Restoring backup: $latest_backup"
  cp "$latest_backup" "$CONFIG_PATH"
  "$OPENCLAW_BIN" gateway restart >>"$INFO_LOG" 2>&1 || true
}

main() {
  if [[ -z "$OPENCLAW_BIN" ]]; then
    echo "openclaw command not found in PATH" >&2
    exit 127
  fi
  if [[ -z "$CODEX_BIN" ]]; then
    echo "codex command not found in PATH" >&2
    exit 127
  fi
  if [[ ! -f "$CONFIG_PATH" ]]; then
    echo "Config not found: $CONFIG_PATH" >&2
    exit 2
  fi

  cp "$CONFIG_PATH" "$CONFIG_PATH.guard.bak.$STAMP"
  log "Saved backup: $CONFIG_PATH.guard.bak.$STAMP"

  if restart_and_check; then
    log "No repair needed"
    exit 0
  fi

  collect_context
  if run_codex_repair; then
    log "Codex repair command finished"
  else
    log "Codex repair command failed"
  fi

  if health_ok; then
    log "Gateway recovered after codex repair"
    exit 0
  fi

  log "Trying doctor --fix fallback"
  "$OPENCLAW_BIN" doctor --fix >>"$INFO_LOG" 2>&1 || true
  "$OPENCLAW_BIN" gateway restart >>"$INFO_LOG" 2>&1 || true
  if health_ok; then
    log "Gateway recovered via doctor fallback"
    exit 0
  fi

  log "Gateway still unhealthy after codex repair; applying backup fallback"
  restore_backup

  if health_ok; then
    log "Gateway recovered via backup fallback"
    exit 0
  fi

  log "Gateway recovery failed. Inspect: $INFO_LOG"
  exit 1
}

main "$@"
