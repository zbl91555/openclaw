# Gemini CLI Skill for OpenClaw

Quick integration of Google's Gemini CLI for non-interactive AI queries.

## Installation

1. **Install Gemini CLI:**
   ```bash
   brew install gemini-cli
   ```

2. **Authenticate (first time only):**
   ```bash
   gemini
   # Follow browser login flow
   ```

3. **Install this skill:**
   - Already in workspace: `~/.openclaw/workspace/skills/gemini-cli/`
   - Or via ClawHub: `openclaw skills install gemini-cli`

## Usage Examples

```
gemini "用 Python 写个快速排序"
gemini "解释一下量子纠缠"
gemini --json "返回用户信息示例"
gemini -m gemini-3-pro-preview "复杂问题"
```

## Features

- ✅ Non-interactive mode (perfect for scripts)
- ✅ Auto model selection (gemini-3-pro-preview default)
- ✅ JSON output support
- ✅ Error handling with fallback models
- ✅ Free tier: 60 req/min, 1k req/day

## Requirements

- Node.js 22+
- Google account (free)
- `/usr/sbin` in PATH (for `sysctl`)

## Troubleshooting

**429 Error:** Switch to `gemini-2.5-flash`  
**404 Error:** Use `-preview` models  
**Auth Error:** Run `gemini` interactively first

---

**Source:** https://github.com/google-gemini/gemini-cli  
**Docs:** https://geminicli.com/docs/
