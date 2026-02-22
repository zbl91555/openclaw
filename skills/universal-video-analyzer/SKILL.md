---
name: universal-video-analyzer
description: Advanced Multi-platform (Bilibili/YouTube) content extraction and AI analysis. Fetches metadata, transcripts, and generates structured summaries.
when: "When user sends a YouTube or Bilibili URL, says 'analyze this video', 'summarize this collection', or 'extract key points from video'."
metadata:
  openclaw:
     requires: { "bins": ["yt-dlp", "python3", "ffmpeg"], "anyBins": ["python3", "python"] }
     emoji: "📺"
---

# Universal Video Analyzer Skill

Advanced multi-platform content extraction and AI-driven structured analysis. Supports Bilibili, YouTube, and more.

## Content & Features
- **Transcript Extraction**: Automatically fetches manual or auto-generated subtitles using `yt-dlp`.
- **Metadata Insight**: Retrieves title, channel, view count, and description.
- **Smart Summarization**: Formats video content for AI analysis.
- **Transcript Translation**: Automatically translates extracted transcripts into any target language (e.g., zh-CN for Chinese) using built-in programmatic translation API.
- **Audio Extraction**: "Podcast mode" converts video audio into `.mp3` format for offline playback.
- **Thumbnail Fetching**: Secures the highest resolution cover image of the video.
- **Community Sentiment**: Extracts top audience comments (`--comments`) for sentiment analysis.
- **Intelligent Chapters**: Formats and parses video chapter timelines (`--chapters`) for quick navigation.
- **Playlist & Anthology Analysis**: Batch analyzes YouTube playlists, channels, and Bilibili video anthologies (`--playlist`).
- **Bilibili Support**: Extracts VIP/regional restricted content via local browser cookies (`--cookies-from-browser`).
- **NotebookLM AI Integration**: Automatically creates notebooks with a `[TMP]` tag, generates AI summaries (`--summary`), and creates AI podcasts (`--podcast`).
- **Organized Storage**: All downloaded assets (audio, transcripts, thumbnails) are neatly sorted into respective `.tmp/<video_id>/` folders.

## Usage Commands
- "Analyze this Bilibili video and give me a summary"
- "获取视频的中文字幕并生成大纲: https://..."
- "分析这个 Bilibili 视频的大纲和核心看点"
- "下载这期视频的封面和音频作为播客资料"
- "Analyze this youtube playlist to give me the big picture"
- "帮我提取这个视频的音频，并用 NotebookLM 制作成一期播客"
- "一键提炼这个 B 站视频选集/合集中所有视频的核心知识点"
- "分析这个播放列表的内容并生成一份深度研究报告"
- "Extract and summarize all episodes in this anthology: https://www.bilibili.com/video/..."

## Script Commands
```bash
# Standard analysis
python3 scripts/analyzer.py "<youtube_url>"

# Extract translation, audio, and thumbnail
python3 scripts/analyzer.py "<youtube_url>" --translate zh-CN --audio --thumbnail

# Analyze community comments and chapters
python3 scripts/analyzer.py "<youtube_url>" --comments --chapters

# Analyze entire playlist/channel fast (summary only)
python3 scripts/analyzer.py "<playlist_url>" --playlist

# Batch process Bilibili anthology: Extract all P's, upload to NotebookLM, and get AI summary
python3 scripts/analyzer.py "<bilibili_playlist_url>" --cookies-from-browser chrome --playlist --summary

# Full automated pipeline for collections (Summaries + Podcast)
python3 scripts/analyzer.py "<url>" --playlist --summary --podcast --cookies-from-browser chrome

# Bilibili support via local browser cookies + NotebookLM AI Summary and Podcast
python3 scripts/analyzer.py "<bilibili_url>" --cookies-from-browser chrome --summary --podcast
```

## Troubleshooting & Known Issues
- **Bilibili Playlist/Anthology Outputs "Unknown" Titles & Missing Subtitles**: 
  - **Issue**: `yt-dlp`'s flat-playlist extraction often fails to obtain Bilibili subtitle data or specific part titles without login credentials.
  - **Resolution**: Always pass the `--cookies-from-browser chrome` (or edge/safari) flag when downloading Bilibili content. The analyzer will now intelligently parse the `p=N` fallback parameters in the URL to correctly tag videos (e.g., `Part 1`, `Part 2`) and prevent transcript file overlap (e.g., `transcript_p1.txt`) even when `yt-dlp` returns `unknown` IDs.
- **Unclear/Messy Output Folder Names**: 
  - **Resolution**: All generated directories in `.tmp/` are now appropriately sanitized and formatted to include the full, human-readable video/playlist title along with the video ID (e.g., `.tmp/Video_Title_BV.../`).
