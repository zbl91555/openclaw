# TOOLS.md — 百晓生·工具路由规则

## 🔍 情报搜集工具链

| 工具 | 场景 | 优先级 |
|------|------|--------|
| `exa-web-search-free` | 语义搜索、技术文档、学术内容 | ⭐⭐⭐ 优先 |
| `web-search-pro` (Tavily) | 新闻模式、时间过滤、特定域名 | ⭐⭐ 备选 |
| `universal-video-analyzer` | YouTube/Bilibili 视频内容提取、字幕分析 | 视频场景必用 |
| `notebooklm` | 将研究结果沉淀为可查询知识库 | 长期项目 |
| `brainstorming` | 根据情报发散创意方向、产品思路 | 创意阶段 |

## 📤 输出规范

搜集完成后，将简报写入 `~/.openclaw/shared/brief.md`，格式：

```markdown
## 情报简报 · [日期 时间]

### 核心发现
- [关键发现 1]
- [关键发现 2]

### 趋势判断
[基于数据的趋势分析]

### 原始链接
- [标题](URL)
```

## 🌐 API Key

| 服务 | 配置位置 |
|------|---------|
| Tavily (web-search-pro) | `TAVILY_API_KEY` in `.env` |
| Exa (exa-web-search-free) | 免费，无需 Key |
