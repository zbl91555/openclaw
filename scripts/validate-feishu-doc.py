#!/usr/bin/env python3
import argparse
import json
import re
import urllib.error
import urllib.request

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


def parse_doc_id(link: str):
    m = re.search(r'/docx/([A-Za-z0-9]+)', link)
    return m.group(1) if m else ''


def block_text(blk):
    for key in ('text', 'heading1', 'heading2', 'heading3'):
        obj = blk.get(key, {})
        elems = obj.get('elements', [])
        if elems:
            return ''.join((x.get('text_run') or {}).get('content', '') for x in elems).strip()
    return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--link', required=True)
    ap.add_argument('--min-chars', type=int, default=120)
    args = ap.parse_args()

    doc_id = parse_doc_id(args.link)
    if not doc_id:
        print(json.dumps({'ok': False, 'reason': 'invalid_doc_link', 'doc_id': ''}, ensure_ascii=False))
        raise SystemExit(2)

    token = get_token()
    meta = call(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}', token=token)
    if meta.get('code') != 0:
        print(json.dumps({'ok': False, 'reason': 'doc_not_found', 'doc_id': doc_id, 'meta_code': meta.get('code')}, ensure_ascii=False))
        raise SystemExit(2)

    blocks = call(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks?page_size=200', token=token)
    items = blocks.get('data', {}).get('items', [])

    non_title_blocks = max(0, len(items) - 1)
    text_chars = 0
    non_empty_lines = 0
    skipped_blocks = 0

    if items:
        root = items[0]
        for child_id in root.get('children', []):
            try:
                d = call(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{child_id}', token=token)
            except urllib.error.HTTPError:
                skipped_blocks += 1
                continue
            blk = d.get('data', {}).get('block', {})
            line = block_text(blk)
            if line:
                non_empty_lines += 1
                text_chars += len(line)

    ok = non_title_blocks > 0 and text_chars >= max(1, args.min_chars)
    reason = ''
    if non_title_blocks <= 0:
        reason = 'empty_doc_body'
    elif text_chars < max(1, args.min_chars):
        reason = 'doc_body_too_short'

    out = {
        'ok': ok,
        'doc_id': doc_id,
        'title': meta.get('data', {}).get('document', {}).get('title', ''),
        'block_count': len(items),
        'non_title_blocks': non_title_blocks,
        'non_empty_lines': non_empty_lines,
        'text_chars': text_chars,
        'min_chars': args.min_chars,
        'skipped_blocks': skipped_blocks,
        'reason': '' if ok else reason,
    }
    print(json.dumps(out, ensure_ascii=False))
    raise SystemExit(0 if ok else 2)


if __name__ == '__main__':
    main()
