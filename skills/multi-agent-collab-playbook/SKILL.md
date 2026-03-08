---
name: multi-agent-collab-playbook
description: 统一三个 agent 的角色定位、路由边界、协作门禁与交付规范。用于当前 3-agent 架构的协同治理。
---

# Multi-Agent Collaboration Playbook

## 目标

- 保持角色边界清晰
- 把协作复杂度压到最低
- 让交付可验收、可追踪、可复盘

## 角色定位

- `main`：默认入口、任务分流、跨 agent 协调、结果汇总
- `swe`：工程实现、调试、测试、重构、代码评审
- `research-writer`：信息搜集、技术分析、技术文章撰写

## 基本规则

1. 用户可以直接找 `main`、`swe`、`research-writer`。
2. 用户直接找 `swe` 或 `research-writer` 时，`main` 默认抄收并跟踪。
3. 只有 `main` 可以发起跨 agent 协调。
4. `swe` 与 `research-writer` 禁止直接通信。
5. 跨域任务必须回到 `main` 重新拆分。

## 协作链路

1. 用户发起任务。
2. `main` 判断是否需要分流。
3. 单域任务直接由对应 agent 执行。
4. 跨域任务由 `main` 拆分并汇总。
5. 最终只向用户输出一个统一结果。

## 交付规范

- 执行 agent 回执：`状态 / 产出 / 阻塞 / ETA`
- `main` 汇总：`总状态 / 已完成 / 进行中 / 风险与下一步`
- `swe` 交付必须附验证方式
- `research-writer` 交付必须附来源或依据

## 门禁

- `swe`：
  - 复杂或高风险任务未附 review 结论，不得交付
  - 未说明验证方式，不得视为完成

- `research-writer`：
  - 关键结论无来源支撑，不得交付
  - 时效信息未核验，不得交付

- `main`：
  - 未完成汇总前，不得对用户宣告“已完成”
  - 不得绕过边界强行让 `swe` 与 `research-writer` 直接互聊

## 适用场景

- 编码与调试
- 科技信息搜集
- 技术分析
- 技术文章撰写
- 需要轻量协同但不需要复杂多智能体编排的任务
