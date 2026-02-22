#!/bin/bash
# Edge TTS wrapper with 1.2x speed by default

# Parse arguments
VOICE="zh-CN-XiaoxiaoNeural"
TEXT=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --voice)
      VOICE="$2"
      shift 2
      ;;
    --text)
      TEXT="$2"
      shift 2
      ;;
    --write-media)
      OUTPUT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Generate temp file
TEMP_FILE=$(mktemp /tmp/edge_tts_temp.XXXXXX.mp3)

# Run original edge-tts
edge-tts --voice "$VOICE" --text "$TEXT" --write-media "$TEMP_FILE"

# Apply 1.2x speed
ffmpeg -i "$TEMP_FILE" -filter:a "atempo=1.2" "$OUTPUT" -y

# Cleanup
rm -f "$TEMP_FILE"
