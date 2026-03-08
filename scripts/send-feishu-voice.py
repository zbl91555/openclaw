#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile
import urllib.request
import uuid

CONFIG_PATH = '/Users/mudandan/.openclaw/openclaw.json'
WORKSPACE = '/Users/mudandan/.openclaw/workspace'


def call_json(url, method='GET', token=None, body=None):
    headers = {}
    data = None
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if body is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get_cfg():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_token(cfg, account):
    acc = cfg['channels']['feishu']['accounts'][account]
    r = call_json(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        method='POST',
        body={'app_id': acc['appId'], 'app_secret': acc['appSecret']},
    )
    return r['tenant_access_token']


def default_chat_id(cfg):
    groups = cfg.get('channels', {}).get('feishu', {}).get('groups', {})
    if groups:
        return list(groups.keys())[0]
    return ''


def preprocess_text(text):
    p = os.path.join(WORKSPACE, 'scripts', 'tts_preprocess.py')
    try:
        out = subprocess.check_output(['python3', p, text], text=True)
        return out.strip() if out.strip() else text
    except Exception:
        return text


def run(cmd):
    subprocess.check_call(cmd)


def make_opus(text, voice):
    tts_text = preprocess_text(text)
    if len(tts_text) > 800:
        tts_text = tts_text[:800]

    tmpdir = tempfile.mkdtemp(prefix='feishu_voice_')
    mp3 = os.path.join(tmpdir, 'out.mp3')
    opus = os.path.join(tmpdir, 'out.opus')

    run(['edge-tts', '--voice', voice, '--text', tts_text, '--write-media', mp3])

    run(['ffmpeg', '-y', '-i', mp3, '-c:a', 'libopus', '-b:a', '32k', '-vbr', 'on', '-compression_level', '10', opus])
    return opus, tmpdir


def upload_opus(token, opus_path):
    boundary = '----OpenClawBoundary' + uuid.uuid4().hex
    filename = os.path.basename(opus_path)
    with open(opus_path, 'rb') as f:
        content = f.read()

    parts = []
    parts.append(f'--{boundary}\r\n'.encode())
    parts.append(b'Content-Disposition: form-data; name="file_type"\r\n\r\n')
    parts.append(b'opus\r\n')

    parts.append(f'--{boundary}\r\n'.encode())
    parts.append(f'Content-Disposition: form-data; name="file_name"\r\n\r\n{filename}\r\n'.encode())

    parts.append(f'--{boundary}\r\n'.encode())
    parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    parts.append(b'Content-Type: application/octet-stream\r\n\r\n')
    parts.append(content)
    parts.append(b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())

    body = b''.join(parts)
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/im/v1/files',
        data=body,
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': f'multipart/form-data; boundary={boundary}',
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if res.get('code') != 0:
        raise RuntimeError(f'upload failed: {res}')
    return res['data']['file_key']


def send_audio(token, chat_id, file_key):
    content = json.dumps({'file_key': file_key}, ensure_ascii=False)
    r = call_json(
        f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        method='POST',
        token=token,
        body={
            'receive_id': chat_id,
            'msg_type': 'audio',
            'content': content,
        },
    )
    if r.get('code') != 0:
        raise RuntimeError(f'send message failed: {r}')
    return r.get('data', {}).get('message_id', '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--chat-id', default='')
    ap.add_argument('--account', default='main')
    ap.add_argument('--voice', default='zh-CN-XiaoxiaoNeural')
    args = ap.parse_args()

    cfg = get_cfg()
    chat_id = args.chat_id or default_chat_id(cfg)
    if not chat_id:
        raise SystemExit('no chat_id provided and no default feishu group found')

    token = get_token(cfg, args.account)
    opus_path, tmpdir = make_opus(args.text, args.voice)
    try:
        file_key = upload_opus(token, opus_path)
        message_id = send_audio(token, chat_id, file_key)
        print(json.dumps({'ok': True, 'chat_id': chat_id, 'file_key': file_key, 'message_id': message_id}, ensure_ascii=False))
    finally:
        try:
            for name in os.listdir(tmpdir):
                os.remove(os.path.join(tmpdir, name))
            os.rmdir(tmpdir)
        except Exception:
            pass


if __name__ == '__main__':
    main()
