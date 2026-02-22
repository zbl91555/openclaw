#!/usr/bin/env python3
"""
TTS 文本预处理脚本 - 修复版
- 移除表情符号（仅 emoji）
- 保留中文和主要内容
"""

import re
import sys

def remove_emojis(text):
    """仅移除 emoji 表情符号，保留中文"""
    # 更精确的 emoji 范围
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons 😀-🙏
        "\U0001F300-\U0001F5FF"  # symbols 🌀-🗿
        "\U0001F680-\U0001F6FF"  # transport 🚀-🛿
        "\U0001F1E0-\U0001F1FF"  # flags 🇦-🇿
        "\U0001F900-\U0001F9FF"  # supplemental 🤠-🧿
        "\U0001FA00-\U0001FA6F"  # chess
        "\U0001FA70-\U0001FAFF"  # extended
        "\U00002600-\U000026FF"  # misc symbols ☀-⛿
        "\U00002700-\U000027BF"  # dingbats ✀-➿
        "\U0001F004\U0001F0CF"   # mahjong, cards
        "\U0001F18E"             # AB button
        "\U00003030\U0000303D"   # wavy dash
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def clean_markdown(text):
    """清理 markdown 但保留内容"""
    # 移除链接，保留链接文字
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 移除代码标记，保留代码内容
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # 移除粗体/斜体标记
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # 移除行首的列表标记
    text = re.sub(r'^[\s]*[-\*\+][\s]+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.[\s]+', '', text, flags=re.MULTILINE)
    
    return text

def humanize_text(text):
    """适度口语化 - 使用整词匹配避免部分替换"""
    import re
    # 使用正则表达式进行整词替换，避免部分匹配
    text = re.sub(r'\b配置\b', '设置', text)
    text = re.sub(r'\b已完成\b', '已经弄好了', text)
    text = re.sub(r'\b使用\b', '用', text)
    text = re.sub(r'\b包含\b', '有', text)
    return text

def process_for_tts(text):
    """处理文本用于 TTS"""
    text = remove_emojis(text)
    text = clean_markdown(text)
    text = humanize_text(text)
    
    # 清理多余空行和空格
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = sys.stdin.read()
    
    result = process_for_tts(text)
    print(result)
