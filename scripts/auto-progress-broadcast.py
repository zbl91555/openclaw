#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import time
import urllib.request

CONFIG_PATH = '/Users/mudandan/.openclaw/openclaw.json'
APP_TOKEN = 'It3vblOqwa1Exqsy2bKchI2wnUe'
TABLE_ID = 'tblEnjzZm9KN0kOm'
STATE_DIR = pathlib.Path('/Users/mudandan/.openclaw/workspace/.runtime/progress-broadcast')
LOCK_DIR = STATE_DIR / '.lock'

PROCESS_FIELDS = ['需求澄清', '编码实现', '风险审查', '结果汇总', '知识沉淀']
IGNORE_PREFIX = ('DEMO-', 'TEST-', 'MIGRATE-')


def call(url, method='GET', token=None, body=None):
    headers = {}
    data = None
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if body is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get_token():
    cfg = json.loads(pathlib.Path(CONFIG_PATH).read_text())
    app_id = cfg['channels']['feishu']['accounts']['main']['appId']
    app_secret = cfg['channels']['feishu']['accounts']['main']['appSecret']
    r = call(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        method='POST',
        body={'app_id': app_id, 'app_secret': app_secret},
    )
    return r['tenant_access_token']


def fetch_records(token):
    all_items = []
    page_token = None
    while True:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=500'
        if page_token:
            url += f'&page_token={page_token}'
        r = call(url, token=token)
        data = r.get('data', {})
        all_items.extend(data.get('items', []))
        if not data.get('has_more'):
            break
        page_token = data.get('page_token')
        if not page_token:
            break
    return all_items


def parse_time(text: str):
    if not text:
        return None
    try:
        return dt.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return None


def pick_latest_per_task(items):
    by_tid = {}
    for it in items:
        f = it.get('fields', {})
        tid = str(f.get('task_id') or '').strip()
        if not tid:
            continue
        prev = by_tid.get(tid)
        if not prev:
            by_tid[tid] = it
            continue
        t1 = parse_time(prev.get('fields', {}).get('最近更新时间') or '') or dt.datetime.min
        t2 = parse_time(f.get('最近更新时间') or '') or dt.datetime.min
        if t2 >= t1:
            by_tid[tid] = it
    return list(by_tid.values())


def build_snapshot(items, stale_minutes, max_tasks):
    now = dt.datetime.now()
    kept = []
    for it in items:
        f = it.get('fields', {})
        tid = str(f.get('task_id') or '').strip()
        if not tid:
            continue
        if tid.startswith(IGNORE_PREFIX):
            continue
        if str(f.get('交付状态') or '').strip() != '进行中':
            continue

        updated_txt = str(f.get('最近更新时间') or '').strip()
        updated = parse_time(updated_txt)
        if stale_minutes > 0 and updated and (now - updated).total_seconds() > stale_minutes * 60:
            continue

        phases = {k: str(f.get(k) or '') for k in PROCESS_FIELDS if f.get(k)}
        entry = {
            'task_id': tid,
            'title': str(f.get('任务标题') or f.get('文本') or '-').strip(),
            'status': str(f.get('交付状态') or '-').strip(),
            'stage': str(f.get('当前阶段') or '-').strip(),
            'owner': str(f.get('责任人') or '-').strip(),
            'updated_at': updated_txt or '-',
            'acceptance': str(f.get('验收结果') or '').strip(),
            'link': str(f.get('最终产物链接') or '').strip(),
            'phases': phases,
        }
        kept.append(entry)

    kept.sort(key=lambda x: x.get('updated_at') or '', reverse=True)
    if max_tasks > 0:
        kept = kept[:max_tasks]
    return kept


def state_file_for_target(target):
    key = hashlib.sha1(target.encode()).hexdigest()[:16]
    return STATE_DIR / f'{key}.state.json'


def snapshot_digest(snapshot):
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()


def should_send(target: str, snapshot, min_interval_seconds: int, force: bool):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    fp = state_file_for_target(target)
    now = int(time.time())
    digest = snapshot_digest(snapshot)

    if force:
        fp.write_text(json.dumps({'last_digest': digest, 'last_sent_at': now}, ensure_ascii=False))
        return True, 'force'

    last_digest = ''
    last_sent_at = 0
    if fp.exists():
        try:
            s = json.loads(fp.read_text())
            last_digest = str(s.get('last_digest') or '')
            last_sent_at = int(s.get('last_sent_at') or 0)
        except Exception:
            pass

    if digest == last_digest:
        return False, 'same_snapshot'

    if min_interval_seconds > 0 and (now - last_sent_at) < min_interval_seconds:
        return False, 'min_interval_not_reached'

    fp.write_text(json.dumps({'last_digest': digest, 'last_sent_at': now}, ensure_ascii=False))
    return True, 'changed'


def format_message(snapshot):
    lines = ['【自动进度播报】进行中任务']
    for idx, e in enumerate(snapshot, 1):
        lines.append(f"{idx}. {e['task_id']} | {e['status']} | {e['stage']} | {e['owner']} | {e['updated_at']}")
        lines.append(f"   {e['title']}")
        if e['link']:
            lines.append(f"   链接: {e['link']}")
    lines.append('回复 `skr 6` 可查详细进度。')
    return '\n'.join(lines)


def send_msg(channel: str, account: str, target: str, text: str, dry_run: bool):
    # 使用 nvm 下的 openclaw 完整路径
    openclaw_path = '/Users/mudandan/.nvm/versions/node/v22.22.0/bin/openclaw'
    cmd = [
        openclaw_path, 'message', 'send',
        '--channel', channel,
        '--account', account,
        '--target', target,
        '--message', text,
    ]
    if dry_run:
        print('DRY-RUN:', ' '.join(cmd))
        print(text)
        return
    try:
        os.execvp(cmd[0], cmd)
    except FileNotFoundError:
        # 边界 case: openclaw 命令不存在，静默退出
        print('SKIP: openclaw command not found')
        return


def acquire_lock(lock_ttl_seconds: int):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_DIR.exists():
        try:
            mtime = LOCK_DIR.stat().st_mtime
            if time.time() - mtime > lock_ttl_seconds:
                for child in LOCK_DIR.iterdir():
                    child.unlink(missing_ok=True)
                LOCK_DIR.rmdir()
        except Exception:
            pass
    try:
        LOCK_DIR.mkdir()
        (LOCK_DIR / 'pid').write_text(str(os.getpid()))
        return True
    except Exception:
        return False


def release_lock():
    try:
        for child in LOCK_DIR.iterdir():
            child.unlink(missing_ok=True)
        LOCK_DIR.rmdir()
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--channel', default='feishu')
    ap.add_argument('--account', default='main')
    ap.add_argument('--target', default='oc_f47b52a7056d01d66c9bcfda6a076a6b')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--max-tasks', type=int, default=8)
    ap.add_argument('--stale-minutes', type=int, default=180)
    ap.add_argument('--min-interval-seconds', type=int, default=240)
    ap.add_argument('--lock-ttl-seconds', type=int, default=600)
    args = ap.parse_args()

    if not acquire_lock(args.lock_ttl_seconds):
        print('SKIP: lock exists')
        return

    try:
        token = get_token()
        items = pick_latest_per_task(fetch_records(token))
        snapshot = build_snapshot(items, args.stale_minutes, args.max_tasks)
        if not snapshot:
            print('SKIP: no in-progress tasks')
            return

        ok, reason = should_send(args.target, snapshot, args.min_interval_seconds, args.force)
        if not ok:
            print(f'SKIP: {reason}')
            return

        text = format_message(snapshot)
        send_msg(args.channel, args.account, args.target, text, args.dry_run)
    finally:
        release_lock()


if __name__ == '__main__':
    main()
