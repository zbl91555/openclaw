#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

REQUIRED_FILES = [
    '01_research_pack.md',
    '02_codex_decomposition.md',
    '03_draft_v1.md',
    '04_review_round1.md',
    '05_draft_v2.md',
    '06_review_round2.md',
    '07_final.md',
]

BLOCKS = {
    'missing_codex_decomposition': 'BLOCKED: missing codex decomposition',
    'missing_notebooklm_evidence': 'BLOCKED: missing notebooklm evidence',
    'review_rounds_lt_2': 'BLOCKED: review rounds < 2',
    'missing_writing_quality_check': 'BLOCKED: missing writing quality check',
}


def has_notebooklm_evidence(text: str) -> bool:
    keys = ['NotebookLM', 'notebooklm ask', '数据源', '来源', '引用']
    return any(k in text for k in keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workdir', required=True, help='写作任务目录')
    args = ap.parse_args()

    wd = Path(args.workdir).expanduser().resolve()
    missing = [f for f in REQUIRED_FILES if not (wd / f).exists()]

    if (wd / '02_codex_decomposition.md').exists():
        decomp = (wd / '02_codex_decomposition.md').read_text(encoding='utf-8', errors='ignore')
    else:
        decomp = ''

    evidence_text = ''
    for name in ['01_research_pack.md', '07_final.md']:
        fp = wd / name
        if fp.exists():
            evidence_text += '\n' + fp.read_text(encoding='utf-8', errors='ignore')

    review_count = 0
    for name in ['04_review_round1.md', '06_review_round2.md']:
        fp = wd / name
        if fp.exists() and fp.read_text(encoding='utf-8', errors='ignore').strip():
            review_count += 1

    quality_ok = all((wd / n).exists() for n in ['04_review_round1.md', '06_review_round2.md', '07_final.md'])

    blocks = []
    if missing:
        if '02_codex_decomposition.md' in missing or not decomp.strip():
            blocks.append(BLOCKS['missing_codex_decomposition'])
        if review_count < 2:
            blocks.append(BLOCKS['review_rounds_lt_2'])
        if not quality_ok:
            blocks.append(BLOCKS['missing_writing_quality_check'])

    if not has_notebooklm_evidence(evidence_text):
        blocks.append(BLOCKS['missing_notebooklm_evidence'])

    # de-dup
    blocks = list(dict.fromkeys(blocks))

    result = {
        'ok': len(blocks) == 0,
        'workdir': str(wd),
        'missing_files': missing,
        'review_rounds': review_count,
        'blocks': blocks,
    }
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['ok'] else 2)


if __name__ == '__main__':
    main()
