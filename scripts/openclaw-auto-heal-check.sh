#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="$HOME/.openclaw/workspace/.runtime"
LOG_FILE="$RUNTIME_DIR/auto-heal.log"
LOCK_DIR="$RUNTIME_DIR/auto-heal.lock"
LAST_RUN_FILE="$RUNTIME_DIR/auto-heal.last"
HEAL_SCRIPT="$HOME/.openclaw/workspace/scripts/openclaw-restart-heal.sh"
COOLDOWN_SECONDS=90
export PATH="/Users/mudandan/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"

mkdir -p "$RUNTIME_DIR"

log() {
  printf '%s %s\n' "[$(date '+%Y-%m-%d %H:%M:%S')]" "$*" >> "$LOG_FILE"
}

now_ts() {
  date +%s
}

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

now="$(now_ts)"
if [[ -f "$LAST_RUN_FILE" ]]; then
  last="$(cat "$LAST_RUN_FILE" 2>/dev/null || echo 0)"
  delta=$((now - last))
  if (( delta < COOLDOWN_SECONDS )); then
    exit 0
  fi
fi

if [[ -z "$OPENCLAW_BIN" ]]; then
  log "openclaw command not found; skip auto-heal cycle"
  exit 0
fi

if "$OPENCLAW_BIN" gateway health >/dev/null 2>&1; then
  exit 0
fi

echo "$now" > "$LAST_RUN_FILE"
log "gateway unhealthy -> trigger auto-heal"
"$HEAL_SCRIPT" >> "$LOG_FILE" 2>&1 || log "auto-heal failed"
