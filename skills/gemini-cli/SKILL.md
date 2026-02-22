---
name: gemini-cli
description: Google Gemini CLI integration for non-interactive AI queries.
when: "When user asks to use Gemini CLI for quick questions, code generation, or file operations."
examples:
  - "gemini 写个快速排序"
  - "gemini 分析这个文件"
  - "用 gemini 总结一下"
metadata:
  {
    "openclaw": {
      "emoji": "♊️",
      "requires": { "bins": ["gemini"] }
    }
  }
---

# Execution Guide

## 执行步骤

1. **检查 gemini 是否已安装**
   ```bash
   which gemini || brew install gemini-cli
   ```

2. **检查认证**
   ```bash
   ls ~/.gemini/settings.json || gemini  # 首次登录
   ```

3. **执行查询**
   ```bash
   source ~/.nvm/nvm.sh && nvm use 22
   PATH="/usr/sbin:$PATH" gemini -m gemini-3-pro-preview "<用户问题>"
   ```

4. **如果 429 错误，降级到 gemini-2.5-flash**
   ```bash
   gemini -m gemini-2.5-flash "<用户问题>"
   ```

## 模型优先级

1. `gemini-3-pro-preview` - 首选
2. `gemini-2.5-flash` - 备用（429 时）
3. `gemini-2.0-flash` - 快速任务

## 输出处理

- 直接返回 gemini 的输出
- 如果是代码，用代码块包裹
- 如果是长文本，分段显示
