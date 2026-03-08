#!/usr/bin/env python3
import argparse
import json
import random
import re
import time
import urllib.error
import urllib.request
from datetime import datetime

CONFIG_PATH = '/Users/mudandan/.openclaw/openclaw.json'

DROP_PATTERNS = [
    r'^【修复说明】',
    r'^二、协作建议：采用\s*skr\s*菜单入口',
    r'^三、下一步：每周固定进行竞品追踪',
]


def call(url, method='GET', token=None, body=None, retries=6):
    headers = {}
    data = None
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if body is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')

    for i in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep((1.35 ** i) + random.random() * 0.2)
                continue
            body_text = e.read().decode('utf-8', errors='ignore')
            raise RuntimeError(f'HTTP {e.code}: {body_text[:300]}')


def get_token():
    cfg = json.loads(open(CONFIG_PATH, 'r', encoding='utf-8').read())
    app_id = cfg['channels']['feishu']['accounts']['main']['appId']
    app_secret = cfg['channels']['feishu']['accounts']['main']['appSecret']
    r = call(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        method='POST',
        body={'app_id': app_id, 'app_secret': app_secret},
    )
    return r['tenant_access_token']


def parse_doc_id(link):
    m = re.search(r'/docx/([A-Za-z0-9]+)', link or '')
    return m.group(1) if m else ''


def block_text(blk):
    for key in ('text', 'heading1', 'heading2', 'heading3'):
        obj = blk.get(key, {})
        elems = obj.get('elements', [])
        if elems:
            return ''.join((x.get('text_run') or {}).get('content', '') for x in elems).strip()
    return ''


def get_doc_stats(token, doc_id):
    meta = call(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}', token=token)
    if meta.get('code') != 0:
        return {'ok': False, 'reason': 'doc_not_found', 'text_chars': 0, 'non_empty_lines': 0}

    blocks = call(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks?page_size=200', token=token)
    items = blocks.get('data', {}).get('items', [])
    non_title_blocks = max(0, len(items) - 1)
    text_chars = 0
    non_empty_lines = 0

    if items:
        for child_id in items[0].get('children', []):
            try:
                d = call(
                    f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{child_id}',
                    token=token,
                    retries=3,
                )
            except Exception:
                continue
            blk = d.get('data', {}).get('block', {})
            line = block_text(blk)
            if line:
                non_empty_lines += 1
                text_chars += len(line)

    return {
        'ok': True,
        'title': meta.get('data', {}).get('document', {}).get('title', ''),
        'non_title_blocks': non_title_blocks,
        'text_chars': text_chars,
        'non_empty_lines': non_empty_lines,
    }


def should_drop_line(line):
    if not line:
        return True
    if re.match(r'^https?://[^\s]+$', line):
        return True
    if re.match(r'^[-]{3,}$', line):
        return True
    if 'feishu.cn/docx/' in line or 'larksuite.com/docx/' in line:
        return True
    for p in DROP_PATTERNS:
        if re.search(p, line):
            return True
    return False


def normalize_text(line):
    s = line.strip()
    s = re.sub(r'\[(.*?)\]\((https?://[^)]+)\)', r'\1（\2）', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def inline_elements(s):
    s = normalize_text(s)
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s.startswith('**', i):
            j = s.find('**', i + 2)
            if j != -1 and j > i + 2:
                t = s[i + 2:j]
                out.append({'text_run': {'content': t, 'text_element_style': {'bold': True}}})
                i = j + 2
                continue
        if s[i] == '`':
            j = s.find('`', i + 1)
            if j != -1 and j > i + 1:
                t = s[i + 1:j]
                out.append({'text_run': {'content': t, 'text_element_style': {'inline_code': True}}})
                i = j + 1
                continue
        j = i
        while j < n and not s.startswith('**', j) and s[j] != '`':
            j += 1
        t = s[i:j]
        if t:
            out.append({'text_run': {'content': t}})
        i = j

    cleaned = []
    for e in out:
        c = (e.get('text_run') or {}).get('content', '')
        if c:
            cleaned.append(e)
    if not cleaned:
        cleaned = [{'text_run': {'content': s}}]
    return cleaned


def markdown_to_blocks(text):
    blocks = []
    prev_plain = None
    for raw in text.splitlines():
        line = raw.rstrip('\n')
        plain = normalize_text(line)
        if should_drop_line(plain):
            continue

        m = re.match(r'^\s{0,3}(#{1,3})\s+(.*)$', line)
        if m:
            lvl = len(m.group(1))
            content = normalize_text(m.group(2))
            if not content:
                continue
            if content == prev_plain:
                continue
            elems = inline_elements(content)
            key = 'heading1' if lvl == 1 else ('heading2' if lvl == 2 else 'heading3')
            bt = 3 if lvl == 1 else (4 if lvl == 2 else 5)
            blocks.append({'block_type': bt, key: {'elements': elems}})
            prev_plain = content
            continue

        um = re.match(r'^\s*[-*+]\s+(.*)$', line)
        if um:
            content = normalize_text(um.group(1))
            if not content:
                continue
            content = f'• {content}'
            if content == prev_plain:
                continue
            blocks.append({'block_type': 2, 'text': {'elements': inline_elements(content)}})
            prev_plain = content
            continue

        om = re.match(r'^\s*(\d+)[\.)]\s+(.*)$', line)
        if om:
            num = om.group(1)
            content = normalize_text(om.group(2))
            if not content:
                continue
            content = f'{num}. {content}'
            if content == prev_plain:
                continue
            blocks.append({'block_type': 2, 'text': {'elements': inline_elements(content)}})
            prev_plain = content
            continue

        content = normalize_text(line)
        if not content:
            continue
        if content == prev_plain:
            continue
        blocks.append({'block_type': 2, 'text': {'elements': inline_elements(content)}})
        prev_plain = content

    return blocks


def create_doc_with_blocks(token, title, blocks):
    created = call(
        'https://open.feishu.cn/open-apis/docx/v1/documents',
        method='POST',
        token=token,
        body={'title': title},
    )
    doc_id = created.get('data', {}).get('document', {}).get('document_id', '')
    if not doc_id:
        raise RuntimeError('create_document_failed')

    for i in range(0, len(blocks), 10):
        chunk = blocks[i:i + 10]
        call(
            f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
            method='POST',
            token=token,
            body={'children': chunk},
            retries=10,
        )
        time.sleep(0.2)

    return doc_id


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--task-title', required=True)
    p.add_argument('--text-file', required=True)
    p.add_argument('--link', default='')
    p.add_argument('--min-chars', type=int, default=300)
    p.add_argument('--force-rebuild', action='store_true')
    args = p.parse_args()

    result = {
        'ok': False,
        'fixed': False,
        'final_link': args.link,
        'reason': '',
        'source_text_chars': 0,
        'doc_text_chars': 0,
    }

    try:
        token = get_token()
    except Exception as e:
        result['reason'] = f'get_token_failed:{e}'
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(2)

    if not args.force_rebuild:
        doc_id = parse_doc_id(args.link)
        if doc_id:
            try:
                st = get_doc_stats(token, doc_id)
                result['doc_text_chars'] = st.get('text_chars', 0)
                if st.get('ok') and st.get('text_chars', 0) >= max(1, args.min_chars):
                    result['ok'] = True
                    result['reason'] = 'existing_doc_valid'
                    print(json.dumps(result, ensure_ascii=False))
                    raise SystemExit(0)
            except Exception:
                pass

    try:
        text = open(args.text_file, 'r', encoding='utf-8').read()
    except Exception as e:
        result['reason'] = f'read_text_failed:{e}'
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(2)

    blocks = markdown_to_blocks(text)
    source_text = '\n'.join(block_text({'text': b.get('text', {}), 'heading1': b.get('heading1', {}), 'heading2': b.get('heading2', {}), 'heading3': b.get('heading3', {})}) for b in blocks)
    result['source_text_chars'] = len(source_text)
    if len(source_text) < max(60, args.min_chars):
        result['reason'] = 'source_text_too_short_for_repair'
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(2)

    stamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    title = f"{args.task_title}（自动修复 {stamp}）"

    try:
        new_doc_id = create_doc_with_blocks(token, title, blocks)
        new_link = f'https://feishu.cn/docx/{new_doc_id}'
        st = get_doc_stats(token, new_doc_id)
        result['doc_text_chars'] = st.get('text_chars', 0)
        if st.get('text_chars', 0) < max(1, args.min_chars):
            result['reason'] = 'repaired_doc_still_too_short'
            result['final_link'] = new_link
            print(json.dumps(result, ensure_ascii=False))
            raise SystemExit(2)

        result['ok'] = True
        result['fixed'] = True
        result['final_link'] = new_link
        result['reason'] = 'repaired_with_new_doc'
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(0)
    except Exception as e:
        result['reason'] = f'repair_failed:{e}'
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(2)


if __name__ == '__main__':
    main()
