#!/usr/bin/env python3
import argparse
import json
import os
import signal
import subprocess
from pathlib import Path

WORKSPACE = '/Users/mudandan/.openclaw/workspace'
UPDATER = f'{WORKSPACE}/scripts/bitable-update-collab-status.py'
QUERY = f'{WORKSPACE}/scripts/query-task-progress.py'


def sh(cmd):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True)


def list_matching_pids(task_id: str):
    # 仅杀执行类进程，避免误杀查询/取消自身
    out = sh("ps -axo pid=,command=").stdout.splitlines()
    pids = []
    for line in out:
        line = line.strip()
        if not line:
            continue
        try:
            pid_s, cmd = line.split(' ', 1)
            pid = int(pid_s)
        except Exception:
            continue
        if pid == os.getpid():
            continue
        if task_id not in cmd:
            continue
        if 'cancel-task.py' in cmd or 'query-task-progress.py' in cmd:
            continue
        if ('openclaw agent' in cmd) or ('oneclick-' in cmd):
            pids.append((pid, cmd))
    return pids


def kill_pids(pairs):
    killed = []
    for pid, cmd in pairs:
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append({'pid': pid, 'signal': 'TERM', 'cmd': cmd[:200]})
        except ProcessLookupError:
            continue
        except PermissionError:
            continue
    return killed


def write_cancel_marker(task_id: str, reason: str):
    d = Path(WORKSPACE) / '.runtime' / 'pipelines' / task_id
    if not d.exists():
        return ''
    marker = d / 'CANCELED'
    marker.write_text(reason + '\n', encoding='utf-8')
    return str(marker)


def update_board(task_id: str, reason: str):
    if not Path(UPDATER).exists():
        return {'ok': False, 'reason': 'updater_missing'}
    # 使用“已取消”状态；若表单枚举限制，后端会拒绝，兜底改为阻塞
    cmd = (
        f"python3 '{UPDATER}' --task-id '{task_id}' --title '任务取消' "
        f"--status 已取消 --owner main --module 风险审查 --acceptance '{reason}' --upsert"
    )
    r = sh(cmd)
    txt = (r.stdout or '').strip() or (r.stderr or '').strip()
    if r.returncode == 0:
        try:
            return json.loads(txt)
        except Exception:
            return {'ok': True, 'raw': txt}

    fallback = (
        f"python3 '{UPDATER}' --task-id '{task_id}' --title '任务取消' "
        f"--status 阻塞 --owner main --module 风险审查 --acceptance '已取消: {reason}' --upsert"
    )
    r2 = sh(fallback)
    txt2 = (r2.stdout or '').strip() or (r2.stderr or '').strip()
    try:
        return json.loads(txt2)
    except Exception:
        return {'ok': r2.returncode == 0, 'raw': txt2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task-id', required=True)
    ap.add_argument('--reason', default='用户手动取消')
    args = ap.parse_args()

    pairs = list_matching_pids(args.task_id)
    killed = kill_pids(pairs)
    marker = write_cancel_marker(args.task_id, args.reason)
    board = update_board(args.task_id, args.reason)

    print(json.dumps({
        'ok': True,
        'task_id': args.task_id,
        'killed': killed,
        'marker': marker,
        'board': board,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
