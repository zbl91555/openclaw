#!/usr/bin/env python3
import argparse
import datetime
import json
import sys
import urllib.parse
import urllib.request

APP_TOKEN_DEFAULT = 'It3vblOqwa1Exqsy2bKchI2wnUe'
TABLE_ID_DEFAULT = 'tblEnjzZm9KN0kOm'  # 任务看板（交付主表）
CONFIG_PATH = '/Users/mudandan/.openclaw/openclaw.json'

PROCESS_FIELDS = ['需求澄清', '编码实现', '风险审查', '结果汇总', '知识沉淀']
DELIVERY_FIELDS = [
    'task_id',
    '任务标题',
    '交付状态',
    '验收结果',
    '责任人',
    '截止时间',
    '最终产物链接',
    '最近更新时间',
    '当前阶段',
]
REQUIRED_FIELDS = DELIVERY_FIELDS + PROCESS_FIELDS

MODULE_ALIASES = {
    '需求澄清': {'需求澄清', '需求分析', '决策卡', '产品澄清'},
    '编码实现': {'编码实现', '开发实现', '工程实现', '代码开发'},
    '风险审查': {'风险审查', '代码审查', 'codex review', 'review'},
    '结果汇总': {'结果汇总', '汇总', '收敛', '状态汇总', '老板汇报', '周度行业研究', '竞品追踪'},
    '知识沉淀': {'知识沉淀', '知识库发布', '文档沉淀', '内容沉淀', '专业写作'},
}


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


def normalize_module(module):
    if not module:
        return ''
    raw = module.strip()
    for canonical, aliases in MODULE_ALIASES.items():
        if raw in aliases:
            return canonical
    return raw


def list_fields(token, app_token, table_id):
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields?page_size=500'
    r = call(url, token=token)
    return r.get('data', {}).get('items', [])


def ensure_fields(token, app_token, table_id):
    existing = {i['field_name'] for i in list_fields(token, app_token, table_id)}
    created = []
    for name in REQUIRED_FIELDS:
        if name in existing:
            continue
        body = {'field_name': name, 'type': 1}
        r = call(
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields',
            method='POST',
            token=token,
            body=body,
        )
        if r.get('code') == 0:
            created.append(name)
    return created


def find_record_by_task_id(token, app_token, table_id, task_id):
    filter_expr = f'CurrentValue.[task_id] = "{task_id}"'
    url = (
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records'
        f'?page_size=20&filter={urllib.parse.quote(filter_expr)}'
    )
    r = call(url, token=token)
    items = r.get('data', {}).get('items', [])
    return items[0] if items else None


def build_fields(args):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fields = {
        'task_id': args.task_id,
        '交付状态': args.status,
        '责任人': args.owner,
        '最近更新时间': now,
    }
    if args.title:
        fields['任务标题'] = args.title
    if args.acceptance:
        fields['验收结果'] = args.acceptance
    if args.deadline:
        fields['截止时间'] = args.deadline
    if args.link:
        fields['最终产物链接'] = args.link
    module = normalize_module(args.module)
    if module:
        fields['当前阶段'] = module
        if module in PROCESS_FIELDS:
            fields[module] = args.status
    return fields


def update_record(token, app_token, table_id, record_id, fields):
    body = {'fields': fields}
    return call(
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}',
        method='PUT',
        token=token,
        body=body,
    )


def create_record(token, app_token, table_id, fields, title=''):
    create_fields = dict(fields)
    create_fields['文本'] = f"{fields.get('task_id', '')} | {title or fields.get('任务标题', '')}".strip(' |')
    body = {'records': [{'fields': create_fields}]}
    return call(
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create',
        method='POST',
        token=token,
        body=body,
    )


def main():
    p = argparse.ArgumentParser(description='Update delivery board by task_id (single-table view)')
    p.add_argument('--task-id', required=True, help='任务唯一标识 task_id')
    p.add_argument('--title', default='', help='任务标题')
    p.add_argument('--status', required=True, help='交付状态，例如 进行中/阻塞/已完成')
    p.add_argument('--owner', required=True, help='责任人，例如 main/swe/research-writer')
    p.add_argument('--module', default='', help='过程字段（需求澄清/编码实现/风险审查/结果汇总/知识沉淀）')
    p.add_argument('--acceptance', default='', help='验收结果摘要')
    p.add_argument('--deadline', default='', help='截止时间文本，如 2026-02-27 18:00')
    p.add_argument('--link', default='', help='最终产物链接')
    p.add_argument('--app-token', default=APP_TOKEN_DEFAULT)
    p.add_argument('--table-id', default=TABLE_ID_DEFAULT)
    p.add_argument('--upsert', action='store_true', help='task_id 不存在时自动创建')
    p.add_argument('--ensure-only', action='store_true', help='仅补齐字段并退出')
    args = p.parse_args()

    token = get_token()
    created = ensure_fields(token, args.app_token, args.table_id)
    if args.ensure_only:
        print(json.dumps({'ok': True, 'action': 'ensure_only', 'created_fields': created}, ensure_ascii=False))
        return

    rec = find_record_by_task_id(token, args.app_token, args.table_id, args.task_id)
    fields = build_fields(args)

    if not rec:
        if not args.upsert:
            print(json.dumps({'ok': False, 'error': f'task_id 不存在: {args.task_id}', 'hint': 'use --upsert', 'created_fields': created}, ensure_ascii=False))
            sys.exit(2)
        r = create_record(token, args.app_token, args.table_id, fields, args.title)
        print(json.dumps({'ok': r.get('code') == 0, 'code': r.get('code'), 'msg': r.get('msg'), 'action': 'created', 'task_id': args.task_id, 'status': args.status, 'owner': args.owner, 'module': normalize_module(args.module), 'link': args.link, 'created_fields': created}, ensure_ascii=False))
        return

    r = update_record(token, args.app_token, args.table_id, rec['record_id'], fields)
    print(json.dumps({'ok': r.get('code') == 0, 'code': r.get('code'), 'msg': r.get('msg'), 'action': 'updated', 'task_id': args.task_id, 'status': args.status, 'owner': args.owner, 'module': normalize_module(args.module), 'link': args.link, 'created_fields': created}, ensure_ascii=False))


if __name__ == '__main__':
    main()
