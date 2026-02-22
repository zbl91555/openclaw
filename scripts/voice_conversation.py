#!/usr/bin/env python3
"""
语音对话状态管理
"""

import json
import os
import sys

CONFIG_FILE = "/Users/mudandan/.openclaw/workspace/config/voice_settings.json"

def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"voiceConversation": {"enabled": False}}

def save_config(config):
    """保存配置"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def enable_voice_conversation():
    """开启语音对话模式"""
    config = load_config()
    config["voiceConversation"]["enabled"] = True
    config["voiceConversation"]["autoTTS"] = True
    save_config(config)
    return "语音对话模式已开启 ✅"

def disable_voice_conversation():
    """关闭语音对话模式"""
    config = load_config()
    config["voiceConversation"]["enabled"] = False
    config["voiceConversation"]["autoTTS"] = False
    save_config(config)
    return "语音对话模式已关闭"

def is_voice_conversation_enabled():
    """检查语音对话是否开启"""
    config = load_config()
    return config.get("voiceConversation", {}).get("enabled", False)

def get_voice_settings():
    """获取语音设置"""
    config = load_config()
    return config.get("voiceConversation", {})

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "enable":
            print(enable_voice_conversation())
        elif command == "disable":
            print(disable_voice_conversation())
        elif command == "status":
            print("enabled" if is_voice_conversation_enabled() else "disabled")
        elif command == "settings":
            print(json.dumps(get_voice_settings(), ensure_ascii=False))
        else:
            print("Unknown command")
    else:
        # 检查状态并输出
        if is_voice_conversation_enabled():
            print("VOICE_MODE_ENABLED")
        else:
            print("VOICE_MODE_DISABLED")
