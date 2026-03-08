#!/usr/bin/env python3
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime

APP_TOKEN = 'It3vblOqwa1Exqsy2bKchI2wnUe'
TABLE_ID = 'tblEnjzZm9KN0kOm'
CONFIG_PATH = '/Users/mudandan/.openclaw/openclaw.json'


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


def list_recent(token, limit):
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=500'
    r = call(url, token=token)
    items = r.get('data', {}).get('items', [])
    def keyf(x):
        f=x.get('fields',{})
        return f.get('最近更新时间') or ''
    items.sort(key=keyf, reverse=True)
    return items[:limit]


def get_by_task_id(token, task_id):
    filt = urllib.parse.quote(f'CurrentValue.[task_id] = "{task_id}"')
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=5&filter={filt}'
    r = call(url, token=token)
    items = r.get('data', {}).get('items', [])
    return items[0] if items else None


def summarize(fields):
    phase_fields = ['需求澄清', '编码实现', '风险审查', '结果汇总', '知识沉淀']
    phases = []
    for p in phase_fields:
        v = fields.get(p)
        if v:
            phases.append(f'{p}:{v}')
    return {
        'task_id': fields.get('task_id') or '',
        'title': fields.get('任务标题') or fields.get('文本') or '',
        'status': fields.get('交付状态') or '',
        'stage': fields.get('当前阶段') or '',
        'owner': fields.get('责任人') or '',
        'updated_at': fields.get('最近更新时间') or '',
        'acceptance': fields.get('验收结果') or '',
        'link': fields.get('最终产物链接') or '',
        'phases': phases,
    }


def format_human(rec):
    if not rec:
        return '未找到对应任务。'
    p = summarize(rec['fields'])
    lines = [
        f"task_id: {p['task_id']}",
        f"标题: {p['title']}",
        f"状态: {p['status']}",
        f"阶段: {p['stage']}",
        f"责任人: {p['owner']}",
        f"最近更新时间: {p['updated_at']}",
        f"验收结果: {p['acceptance'][:180]}",
        f"链接: {p['link'] or 'N/A'}",
        f"过程: {' | '.join(p['phases']) if p['phases'] else 'N/A'}",
    ]
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task-id', default='')
    ap.add_argument('--latest', type=int, default=1)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    token = get_token()
    if args.task_id:
        rec = get_by_task_id(token, args.task_id)
        if args.json:
            print(json.dumps({'item': summarize(rec['fields']) if rec else None}, ensure_ascii=False))
        else:
            print(format_human(rec))
        return

    items = list_recent(token, max(1, min(args.latest, 20)))
    packed = [summarize(i['fields']) for i in items]
    if args.json:
        print(json.dumps({'items': packed}, ensure_ascii=False))
        return
    if not packed:
        print('暂无任务记录。')
        return
    for i, it in enumerate(packed, 1):
        print(f"[{i}] {it['task_id']} | {it['status']} | {it['stage']} | {it['owner']} | {it['updated_at']}")
        print(f"    标题: {it['title']}")
        print(f"    链接: {it['link'] or 'N/A'}")


if __name__ == '__main__':
    main()
