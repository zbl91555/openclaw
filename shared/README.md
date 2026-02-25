# Shared Handoff Directory

两个 Agent 之间的"中间站"，用于传递研究简报和代码输出。

## 目录结构

```
shared/
├── README.md       ← 本文件
├── brief.md        ← 主 Agent 输出的 Research 简报（Coding Bot 消费）
└── output/         ← Coding Bot 输出的代码文件（主 Agent 归纳）
```

## 工作流

```
您 → 主 Agent：「研究 xxx，结果写到 ~/.openclaw/shared/brief.md」
     ↓
您 → Coding Bot：「读取 ~/.openclaw/shared/brief.md，帮我实现」
     ↓
Coding Bot 输出代码 → ~/.openclaw/shared/output/xxx.py
```
