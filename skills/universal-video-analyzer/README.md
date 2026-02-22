# Universal Video Analyzer for OpenClaw

A professional YouTube analysis tool integrated as an OpenClaw skill.

## Prerequisites
- `yt-dlp, ffmpeg`: Used for metadata and transcript extraction.
  Install via: `pip install yt-dlp, ffmpeg` or your package manager.
- `notebooklm-py`: Optional module, used for generating AI summaries and podcasts.
  Install via: `pip install notebooklm-py`

## File Structure
- `SKILL.md`: Skill definition and triggers.
- `scripts/analyzer.py`: Main execution script.

## Functionality
The script extracts the best available transcript and metadata, then presents it in a structured format suitable for further AI processing or direct user reading.
