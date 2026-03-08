---
name: codex-review
description: 对复杂/高风险编码任务执行 Codex 代码审查；支持在 subagent 编码失败时接管修复。
---

# Codex Review & Rescue

## 何时使用
- 复杂改造（跨多文件、跨模块、重构）
- 高风险改动（配置、权限、核心流程）
- subagent 编码失败、反复报错、无法收敛

## 复杂/高风险判定（满足任一即触发强制）
- 变更 >= 3 个文件或跨 2 个以上模块
- 涉及配置/鉴权/路由/权限/数据删除
- 涉及发布前核心链路（启动、支付、消息分发、任务派发）
- subagent 连续两轮无法收敛

## 标准流程
1. 如果已有代码改动，先执行：
   - `codex exec review --uncommitted --skip-git-repo-check`
2. 若发现问题，修复后再次 review，直到可交付。
3. 若 subagent 搞不定，直接由 Codex 接管：
   - `codex exec --full-auto --skip-git-repo-check "<任务说明>"`
4. 最终输出：
   - 风险清单（若有）
   - 已修复项
   - 建议验证命令

## 硬门禁
- 命中“复杂/高风险”时，未执行 `codex exec review --uncommitted --skip-git-repo-check` 不得交付。
- 必须在回复中附 `codex review` 结论摘要；没有结论时统一回复：`BLOCKED: missing codex review`。
- 若 review 有高风险未处理，统一回复：`BLOCKED: unresolved review findings`。

## 约束
- 不使用破坏性命令（如 `git reset --hard`）。
- 尽量最小改动；必要时先备份关键配置。
