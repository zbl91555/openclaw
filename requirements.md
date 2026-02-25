# 重新建设 opneClaw 架构

## 备份
现将现有的 .openclaw 目录备份到桌面 openclaw_backup.zip 文件中，如果后续升级失败我需要你去回滚

## 新架构思路
1. 需要是多 agent 协作的架构，我对多个 agent 的设想
    - 第一个 agent（main） 是负责协调调度和统一指挥的。相当于是一个总指挥，负责把任务分配给其他的 agent，并且收集他们的结果，最后整合成一个完整的解决方案。可以理解为是一个项目经理的角色，另外我有一些自己的想法，就是这个 agent 最好是能够支持多模态的输入和输出，因为我希望能够通过语音和它进行交互，并且它能够理解我的意图，然后输出语音和文字的回复。其他的 agent 每天需要向这个 agent 汇报工作，并且接受它的任务分配，当然我也可以独立的向其他的 agent 分配工作。
    - 第二个 agent 是擅长做 research 的工作，拥有众多 research skills，可以利用各种工具进行 research，例如 google search、github search、arxiv search、notebooklm 等等，并且能够将 research 的结果整合成一个完整的解决方案。
    - 第三个 agent 是擅长做 coding 的工作，拥有众多 coding skills，可以利用各种工具进行 coding，例如 git、docker 等等，并且能够将 coding 的结果整合成一个完整的解决方案。可以将我的一些想法变成现实，coding agent 也可以派发子 agent 去完成一些具体的 coding 任务，最后统一把关去 review，确保代码质量
    - 第四个 agent 是擅长做 idea 的工作，拥有众多 idea skills，可以从 github trending/reddit/google/openai blog/anthropic blog/linux.do 等等网站或论坛上定期自动抓取一些最新的资讯（当然我可以主动触发他），然后对这些资讯进行分析和总结，提取其中的热点和创意，然后反馈给我，我确认之后可以协调 research agent 做一些 research 工作，涉及到 coding 的话可以协调 coding agent 做一些 coding 工作做前期的验证。另外我给他抛出一个主题也可以帮我分析，也可以做一些头脑风暴，帮我拆解任务，输出一个详细的计划
    - 第五个 agent 是擅长做 writing 的工作，拥有众多 writing skills，可以利用各种工具进行 writing，例如 google notebooklm 等等，并且能够将 writing 的结果整合成一个完整的解决方案。可以帮我写一些文档、推文等。目前我的需求
2. 所有的 agent 都有单独的 bot，我可以直接管理，另外我也会把这些 bot 拉入群聊，可以自动向 main agent 汇报工作，并且接受它的任务分配，当然我的优先级更高可以随时打断他们。所有 agent 执行的任务项我需要有查看进度的能力，并且可以随时打断他们。
3. bot 机器人我希望使用飞书去做