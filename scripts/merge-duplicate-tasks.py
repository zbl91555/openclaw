#!/usr/bin/env python3
import argparse
import datetime
import json
import re
import urllib.parse
import urllib.request
from collections import defaultdict

CONFIG_PATH = '/Users/mudandan/.openclaw/openclaw.json'
APP_TOKEN = 'It3vblOqwa1Exqsy2bKchI2wnUe'
TABLE_ID = 'tblEnjzZm9KN0kOm'

PROCESS_FIELDS = ['需求澄清', '编码实现', '风险审查', '结果汇总', '知识沉淀']


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
    cfg = json.loads(open(CONFIG_PATH, 'r').read())
    app_id = cfg['channels']['feishu']['accounts']['main']['appId']
    app_secret = cfg['channels']['feishu']['accounts']['main']['appSecret']
    r = call(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        method='POST',
        body={'app_id': app_id, 'app_secret': app_secret},
    )
    return r['tenant_access_token']


def list_records(token):
    all_items = []
    page_token = None
    while True:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=500'
        if page_token:
            url += f'&page_token={urllib.parse.quote(page_token)}'
        r = call(url, token=token)
        data = r.get('data', {})
        all_items.extend(data.get('items', []))
        if not data.get('has_more'):
            break
        page_token = data.get('page_token')
        if not page_token:
            break
    return all_items


def normalize_title(title):
    if not title:
        return ''
    t = title.strip().lower()
    t = re.sub(r'^(周度行业研究[:：\-\s]*|专业写作[:：\-\s]*|竞品追踪[:：\-\s]*|老板汇报[:：\-\s]*)', '', t)
    t = re.sub(r'[-\s]*20\d{2}-w\d{2}$', '', t)
    t = re.sub(r'[^\w\u4e00-\u9fa5]+', '', t)
    return t


def status_weight(status):
    order = {'已完成': 3, '进行中': 2, '阻塞': 1, '已合并': 0}
    return order.get(str(status or '').strip(), 0)


def parse_dt(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return datetime.datetime.min


def row_score(fields):
    score = 0
    if fields.get('最终产物链接'):
        score += 10
    score += status_weight(fields.get('交付状态')) * 2
    score += sum(1 for f in PROCESS_FIELDS if fields.get(f))
    score += 1 if fields.get('验收结果') else 0
    return score, parse_dt(fields.get('最近更新时间') or '')


def pick_master(rows):
    scored = sorted(rows, key=lambda r: row_score(r['fields']), reverse=True)
    return scored[0]


def merge_into_master(master_fields, dup_fields):
    out = {}
    for k in ['最终产物链接', '验收结果', '责任人', '当前阶段']:
        if not master_fields.get(k) and dup_fields.get(k):
            out[k] = dup_fields.get(k)
    for k in PROCESS_FIELDS:
        if not master_fields.get(k) and dup_fields.get(k):
            out[k] = dup_fields.get(k)
    return out


def update_record(token, record_id, fields):
    return call(
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}',
        method='PUT',
        token=token,
        body={'fields': fields},
    )


def main():
    ap = argparse.ArgumentParser(description='Merge duplicated tasks in delivery board')
    ap.add_argument('--execute', action='store_true', help='apply updates (default: dry-run)')
    ap.add_argument('--limit-groups', type=int, default=20)
    args = ap.parse_args()

    token = get_token()
    items = list_records(token)

    groups = defaultdict(list)
    for it in items:
        f = it.get('fields', {})
        tid = f.get('task_id')
        if not tid:
            continue
        status = str(f.get('交付状态') or '').strip()
        if status == '已合并':
            continue
        title = f.get('任务标题') or f.get('文本') or ''
        key = normalize_title(title)
        if not key:
            continue
        groups[key].append(it)

    dup_groups = [g for g in groups.values() if len(g) > 1]
    dup_groups.sort(key=lambda g: len(g), reverse=True)
    dup_groups = dup_groups[: args.limit_groups]

    report = []
    for g in dup_groups:
        master = pick_master(g)
        master_id = master['record_id']
        master_tid = master.get('fields', {}).get('task_id')
        merged_from = []
        patch_master = {}

        for r in g:
            if r['record_id'] == master_id:
                continue
            merged_from.append(r.get('fields', {}).get('task_id'))
            patch_master.update(merge_into_master(master['fields'], r.get('fields', {})))

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if merged_from:
            note = f"MERGED_FROM: {','.join([x for x in merged_from if x])} @ {now}"
            acc = (master['fields'].get('验收结果') or '').strip()
            patch_master['验收结果'] = (acc + ' | ' + note).strip(' |')
            patch_master['最近更新时间'] = now

        report.append({
            'master_task_id': master_tid,
            'master_record_id': master_id,
            'merged_from': merged_from,
            'patch_master': patch_master,
        })

        if args.execute:
            if patch_master:
                update_record(token, master_id, patch_master)
            for r in g:
                if r['record_id'] == master_id:
                    continue
                dup_tid = r.get('fields', {}).get('task_id')
                dup_acc = (r.get('fields', {}).get('验收结果') or '').strip()
                dup_patch = {
                    '交付状态': '已合并',
                    '当前阶段': '结果汇总',
                    '验收结果': (dup_acc + f" | MERGED_TO: {master_tid}").strip(' |'),
                    '最近更新时间': now,
                }
                update_record(token, r['record_id'], dup_patch)

    print(json.dumps({'ok': True, 'execute': args.execute, 'duplicate_groups': len(dup_groups), 'report': report}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
