#!/usr/bin/env python3
import json
import subprocess
import sys
import os
import re
import tempfile
import shutil
import urllib.request
import urllib.parse
import time
import argparse
from typing import Optional, Dict, Any

def sanitize_filename(name: str) -> str:
    # Remove characters that are unsafe for filenames
    safe_name = re.sub(r'[\\/*?:"<>|]', "", name)
    return safe_name.strip()

def run_command(command: list) -> tuple[int, str, str]:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def get_metadata(url: str, fetch_comments: bool = False, is_playlist: bool = False, cookies_from_browser: Optional[str] = None) -> Optional[Dict[str, Any]]:
    print(f"[*] Fetching metadata for: {url}")
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        "--no-warnings"
    ]
    if fetch_comments:
        cmd.append("--write-comments")
    if is_playlist:
        cmd.append("--flat-playlist")
    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])
    cmd.append(url)
    rc, stdout, stderr = run_command(cmd)
    if rc != 0:
        print(f"[!] Error fetching metadata: {stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None

def extract_transcript(url: str, video_id: str, cookies_from_browser: Optional[str] = None) -> str:
    print("[*] Attempting to extract transcript...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Try to download subtitles
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-auto-subs",
            "--write-subs",
            "--sub-langs", "en.*,zh.*,ja.*,ai-zh,ai-en,ai-.*",
            "--sub-format", "vtt/srt/best",
            "-o", os.path.join(tmpdir, "sub"),
        ]
        if cookies_from_browser:
            cmd.extend(["--cookies-from-browser", cookies_from_browser])
        cmd.append(url)
        rc, _, stderr = run_command(cmd)
        
        # Look for sub files
        sub_files = [f for f in os.listdir(tmpdir) if f.startswith("sub.")]
        if not sub_files:
            return "No transcript available (subtitles not found)."

        # Prefer manual subs over auto-subs, and prioritize zh/en languages
        def sub_priority(filename):
            fn = filename.lower()
            if "zh" in fn and not "ai" in fn: return 0
            if "en" in fn and not "ai" in fn: return 1
            if "ai-zh" in fn: return 2
            if "ai-en" in fn: return 3
            if "zh" in fn: return 4
            if "en" in fn: return 5
            return 99
            
        sub_files.sort(key=sub_priority)
        sub_path = os.path.join(tmpdir, sub_files[0])
        
        try:
            with open(sub_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple VTT/SRT cleaning (removes timestamps and tags)
            lines = content.splitlines()
            cleaned = []
            for line in lines:
                if not line.strip(): continue
                if "-->" in line: continue
                if line.isdigit(): continue
                if line.startswith("WEBVTT"): continue
                if line.startswith("Kind:"): continue
                if line.startswith("Language:"): continue
                
                # Remove HTML tags
                line = re.sub(r'<[^>]+>', '', line)
                clean_line = line.strip()
                
                if clean_line:
                    if not cleaned:
                        cleaned.append(clean_line)
                    elif cleaned[-1] == clean_line:
                        continue
                    elif clean_line.startswith(cleaned[-1].replace('-', '').strip()):
                        # Youtube auto-subs often have rolling text. Replace previous incomplete line.
                        cleaned[-1] = clean_line
                    else:
                        cleaned.append(clean_line)
            
            # Reconstruct into sentences and paragraphs
            final_text = ""
            for c in cleaned:
                if not final_text:
                    final_text = c
                else:
                    # Smart joining
                    if final_text[-1] in ".!?":
                        final_text += " " + c
                    elif final_text.endswith("-"):
                        final_text = final_text[:-1] + c
                    else:
                        final_text += " " + c
            
            # Group into readable paragraphs (approx 5-7 sentences per paragraph)
            # If no punctuation, we just wrap it arbitrarily to avoid huge blocks.
            sentences = re.split(r'(?<=[.!?]) +', final_text)
            paragraphs = []
            curr_para = []
            word_count = 0
            
            for s in sentences:
                curr_para.append(s)
                word_count += len(s.split())
                # Break paragraph if it has 5 sentences or over 60 words
                if len(curr_para) >= 5 or word_count > 60:
                    paragraphs.append(" ".join(curr_para))
                    curr_para = []
                    word_count = 0
                    
            if curr_para:
                paragraphs.append(" ".join(curr_para))
                
            return "\n\n".join(paragraphs) if paragraphs else final_text
        except Exception as e:
            return f"Error reading transcript: {str(e)}"

def translate_text(text: str, target_lang='zh-CN', chunk_size=4000) -> str:
    print(f"[*] Translating transcript to {target_lang}...")
    def translate_chunk(chunk):
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(chunk)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))
            return ''.join([sentence[0] for sentence in result[0] if sentence and len(sentence) > 0 and sentence[0]])
        except Exception as e:
            return f"\n[Translation error: {e}]\n"

    chunks = []
    current_chunk = []
    current_length = 0
    for line in text.splitlines():
        if current_length + len(line) > chunk_size:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = len(line)
        else:
            current_chunk.append(line)
            current_length += len(line) + 1
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    translated_text = ""
    for i, chunk in enumerate(chunks):
        translated_text += translate_chunk(chunk) + "\n"
        time.sleep(0.5)
    return translated_text

def main():
    parser = argparse.ArgumentParser(description="Universal Video Analyzer")
    parser.add_argument("url", help="YouTube URL to analyze")
    parser.add_argument("--translate", "-t", help="Translate transcript to specified language code (e.g. zh-CN)", default=None)
    parser.add_argument("--audio", "-a", action="store_true", help="Download video as an audio/podcast file (mp3)")
    parser.add_argument("--thumbnail", "-i", action="store_true", help="Download the highest quality thumbnail image")
    parser.add_argument("--playlist", "-p", action="store_true", help="Analyze as a playlist/channel instead of a single video")
    parser.add_argument("--comments", "-c", action="store_true", help="Extract top comments for community sentiment")
    parser.add_argument("--chapters", action="store_true", help="Extract intelligent video chapters/timestamps")
    parser.add_argument("--cookies-from-browser", help="Extract cookies from the specified browser (e.g. chrome, edge, safari). Essential for downloading premium or region-locked Bilibili subtitles and content.", default=None)
    parser.add_argument("--summary", action="store_true", help="Use NotebookLM to generate an AI chapter structure and summary (requires notebooklm-py)")
    parser.add_argument("--podcast", action="store_true", help="Use NotebookLM to generate an AI audio podcast based on the video (requires notebooklm-py)")
    args = parser.parse_args()

    url = args.url
    
    # 1. Get Metadata
    metadata = get_metadata(url, fetch_comments=args.comments, is_playlist=args.playlist, cookies_from_browser=args.cookies_from_browser)
    if not metadata:
        sys.exit(1)

    is_playlist_obj = metadata.get('_type') in ('playlist', 'multi_video')
    
    if args.playlist and is_playlist_obj:
        title = metadata.get('title', 'Unknown Playlist')
        uploader = metadata.get('uploader', 'Unknown Channel')
        entries = metadata.get('entries', [])
        
        print("\n" + "="*60)
        print("【PLAYLIST/ANTHOLOGY DETECTED】")
        print("="*60)
        print(f"**Title**: {title}")
        print(f"**Channel**: {uploader}")
        print(f"**Total Videos**: {len(entries)}")
        
        if not (args.summary or args.podcast):
            total_duration = sum([e.get('duration', 0) or 0 for e in entries])
            hours = total_duration // 3600
            minutes = (total_duration % 3600) // 60
            print(f"**Total Duration**: {hours} hours, {minutes} minutes")
            
            print("\n--- **First 15 Videos Snapshot** ---")
            for i, entry in enumerate(entries[:15]):
                vid_title = entry.get('title', 'Unknown')
                if vid_title == 'Unknown':
                    vid_title = f"Part {i+1}"
                dur = entry.get('duration', 0) or 0
                dur_str = f"{int(dur)//60}:{int(dur)%60:02d}"
                print(f"{i+1}. {vid_title} ({dur_str})")
                
            print("\n[!] To analyze all videos in this collection, add --summary or --podcast to your command.")
            print("="*60)
            sys.exit(0)
        else:
            print(f"[*] Batch processing {len(entries)} videos for AI analysis...")
            video_list = []
            for entry in entries:
                # Some extractors return 'url' or 'id'
                v_url = entry.get('url') or entry.get('webpage_url')
                if not v_url and entry.get('id'):
                    # Fallback for youtube if it's just an id
                    if "youtube.com" in url:
                        v_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    elif "bilibili.com" in url:
                        v_url = f"https://www.bilibili.com/video/{entry['id']}"
                
                if v_url:
                    video_list.append({
                        'url': v_url,
                        'title': entry.get('title', 'Unknown'),
                        'id': entry.get('id', 'unknown')
                    })
            
            if not video_list:
                print("[!] Could not extract individual video URLs from playlist.", file=sys.stderr)
                sys.exit(1)
            
            # Process sub-videos
            all_transcript_files = []
            playlist_id = metadata.get('id', 'playlist_' + str(int(time.time())))
            safe_title = sanitize_filename(title)
            dir_name = f"{safe_title}_{playlist_id}" if safe_title else playlist_id
            playlist_output_dir = os.path.join(".tmp", dir_name)
            os.makedirs(playlist_output_dir, exist_ok=True)

            for i, vid in enumerate(video_list):
                print(f"[*] [{i+1}/{len(video_list)}] Processing: {vid['title']}")
                # Improve ID extraction for filenames
                safe_id = vid['id']
                if safe_id == 'unknown':
                    # Try to extract 'p=N' from Bilibili URL
                    p_match = re.search(r'p=(\d+)', vid['url'])
                    if p_match:
                        safe_id = f"p{p_match.group(1)}"
                    else:
                        safe_id = f"v{i+1}"
                
                v_transcript = extract_transcript(vid['url'], vid['id'] if vid['id'] != 'unknown' else safe_id, cookies_from_browser=args.cookies_from_browser)
                v_file = os.path.join(playlist_output_dir, f"transcript_{safe_id}.txt")
                vid_display_title = vid['title'] if vid['title'] != 'Unknown' else f"Part {i+1}"
                with open(v_file, "w", encoding="utf-8") as f:
                    f.write(f"TITLE: {vid_display_title}\nURL: {vid['url']}\n\n{v_transcript}")
                all_transcript_files.append(v_file)

            # Proceed to NotebookLM with all files
            process_notebooklm_batch(title, all_transcript_files, args, playlist_id)
            sys.exit(0)

    video_id = metadata.get('id', 'unknown')
    title = metadata.get('title', 'Unknown Title')
    uploader = metadata.get('uploader', 'Unknown Channel')
    duration_str = metadata.get('duration_string', 'Unknown')
    view_count = metadata.get('view_count', 0)
    description = metadata.get('description', '')

    # 2. Extract Transcript
    transcript = extract_transcript(url, video_id, cookies_from_browser=args.cookies_from_browser)

    # Establish tmp directory for grouping files
    safe_title = sanitize_filename(title)
    dir_name = f"{safe_title}_{video_id}" if safe_title else video_id
    output_dir = os.path.join(".tmp", dir_name)
    os.makedirs(output_dir, exist_ok=True)

    # Save full transcript to file
    transcript_file = os.path.join(output_dir, f"transcript_{video_id}.txt")
    try:
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        transcript_msg = f"Full transcript thoughtfully saved to {os.path.abspath(transcript_file)}"
    except Exception as e:
        transcript_msg = f"Could not save full transcript to file: {e}"

    if args.translate:
        transcript = translate_text(transcript, target_lang=args.translate)
        translated_file = os.path.join(output_dir, f"transcript_{args.translate}_{video_id}.txt")
        try:
            with open(translated_file, "w", encoding="utf-8") as f:
                f.write(transcript)
            transcript_msg += f"\n**Translated Transcript**: {os.path.abspath(translated_file)}"
        except Exception as e:
            transcript_msg += f"\n[!] Could not save translated transcript: {e}"

    # 3. Output Structured Results
    print("\n" + "="*60)
    print("【UNIVERSAL VIDEO ANALYSIS RESULT】")
    print("="*60)
    print(f"**Title**: {title}")
    print(f"**Channel**: {uploader}")
    print(f"**Duration**: {duration_str}")
    print(f"**Views**: {view_count:,}")
    print(f"**URL**: {url}")
    print(f"**Transcript File**: {transcript_msg}")

    # Custom Extractions
    if args.chapters and 'chapters' in metadata and metadata['chapters']:
        print("\n--- **Intelligent Chapters** ---")
        for ch in metadata['chapters']:
            st = ch.get('start_time', 0)
            m, s = divmod(int(st), 60)
            h, m = divmod(m, 60)
            ts = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
            print(f"[{ts}] {ch.get('title', '...')}")
            
    if args.comments and 'comments' in metadata and metadata['comments']:
        print("\n--- **Top Community Comments (Sentiment Base)** ---")
        sorted_comments = sorted(metadata['comments'], key=lambda x: x.get('like_count', 0), reverse=True)
        for i, c in enumerate(sorted_comments[:10]):
            author = c.get('author', 'Anonymous')
            likes = c.get('like_count', 0)
            text = c.get('text', '').replace('\n', ' ')
            trunc_text = text[:150] + ("..." if len(text) > 150 else "")
            print(f"❤️ {likes} | @{author}: {trunc_text}")

    print("\n--- **Description Snippet** ---")
    print(description[:500] + ("..." if len(description) > 500 else ""))
    
    print("\n--- **Transcript / Content Preview** ---")
    print(transcript[:2000] + ("\n...(truncated for display, see file for full transcript)..." if len(transcript) > 2000 else ""))
    print("="*60)

    # 4. Extra Actions
    if args.audio:
        print(f"\n[*] Downloading audio/podcast version...")
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", os.path.join(output_dir, f"audio_{video_id}.%(ext)s")
        ]
        if args.cookies_from_browser:
            cmd.extend(["--cookies-from-browser", args.cookies_from_browser])
        cmd.append(url)
        rc, _, stderr = run_command(cmd)
        if rc == 0:
            print(f"[✔] Audio downloaded successfully to {os.path.abspath(os.path.join(output_dir, f'audio_{video_id}.mp3'))}")
        else:
            print(f"[!] Audio download error: {stderr}", file=sys.stderr)

    if args.thumbnail:
        thumbnail_url = metadata.get('thumbnail')
        if thumbnail_url:
            print(f"\n[*] Downloading thumbnail from URL: {thumbnail_url}")
            try:
                thumb_file = os.path.join(output_dir, f"thumbnail_{video_id}.jpg")
                urllib.request.urlretrieve(thumbnail_url, thumb_file)
                print(f"[✔] Thumbnail downloaded successfully to {os.path.abspath(thumb_file)}")
            except Exception as e:
                print(f"[!] Thumbnail download error: {e}")

    # 5. NotebookLM Integration
    if getattr(args, 'summary', False) or getattr(args, 'podcast', False):
        print(f"\n[*] Initializing NotebookLM AI Analysis...")
        # Check if notebooklm is installed
        rc, _, _ = run_command(["notebooklm", "--version"])
        if rc != 0:
            print("[!] NotebookLM CLI not found. Please install it with: pip install notebooklm-py", file=sys.stderr)
        else:
            try:
                # Create Notebook
                nb_title = f"[TMP] YT: {title[:30]}"
                print(f"[*] Creating Notebook: {nb_title} (Marked as temporary for easy cleanup)")
                rc, out, err = run_command(["notebooklm", "create", nb_title, "--json"])
                if rc == 0:
                    nb_data = json.loads(out)
                    nb_id = nb_data.get("notebook", {}).get("id") or nb_data.get("id")
                    if nb_id:
                        print(f"[✔] Notebook created: {nb_id}")
                        
                        # Add Source
                        print(f"[*] Uploading transcript to NotebookLM...")
                        rc, out, err = run_command(["notebooklm", "source", "add", transcript_file, "-n", nb_id, "--json"])
                        if rc == 0:
                            src_data = json.loads(out)
                            src_id = src_data.get("source", {}).get("id") or src_data.get("source_id")
                            if src_id:
                                print(f"[✔] Source uploaded: {src_id}. Waiting for processing...")
                                run_command(["notebooklm", "source", "wait", src_id, "-n", nb_id])
                                
                                # Summary
                                if getattr(args, 'summary', False):
                                    print("\n" + "="*60)
                                    print("【NOTEBOOKLM AI SUMMARY】")
                                    print("="*60)
                                    # Call interactively or just run blocking
                                    prompt = "根据刚刚上传的解说文案，帮我一键提炼出带有时间线顺序或逻辑顺序的具体智能章节大纲和核心观点。请以Markdown格式输出，标题和核心内容要清晰"
                                    process = subprocess.Popen(
                                        ["notebooklm", "ask", prompt, "-n", nb_id, "--new"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True
                                    )
                                    stdout, _ = process.communicate()
                                    # Try to filter out progress messages from NotebookLM
                                    for line in stdout.splitlines():
                                        if "Starting new conversation" not in line and "Answer:" not in line and "Conversation:" not in line:
                                            print(line)
                                    print("="*60)

                                # Podcast
                                if getattr(args, 'podcast', False):
                                    print(f"\n[*] Generating Deep-Dive Audio Podcast...")
                                    rc, out, err = run_command(["notebooklm", "generate", "audio", "深入聊一聊这篇稿件中的核心内容", "-n", nb_id, "--json"])
                                    if rc == 0:
                                        print(f"[✔] Podcast generation started! Once complete, you can download it using:")
                                        print(f"    notebooklm download audio {os.path.join(output_dir, f'podcast_{video_id}.mp3')} -n {nb_id}")
                                        print(f"    Use 'notebooklm artifact list -n {nb_id}' to check status.")
                                    else:
                                        print(f"[!] Podcast generation failed: {err}")
                            else:
                                print(f"[!] Failed to parse source ID: {out}")
                        else:
                            print(f"[!] Failed to upload source: {err}")
                            
                        print("\n" + "-"*60)
                        print(f"ℹ️ TIP: You can manually delete this temporary notebook later with:")
                        print(f"   notebooklm delete -n {nb_id} -y")
                        print("-" * 60)
                    else:
                        print(f"[!] Failed to parse notebook ID: {out}")
                else:
                    print(f"[!] Failed to create notebook: {err}")
            except Exception as e:
                print(f"[!] Error during NotebookLM integration: {e}")

def process_notebooklm_batch(title, file_paths, args, collection_id):
    print(f"\n[*] Initializing NotebookLM AI Analysis for the collection...")
    rc, _, _ = run_command(["notebooklm", "--version"])
    if rc != 0:
        print("[!] NotebookLM CLI not found. Please install it with: pip install notebooklm-py", file=sys.stderr)
        return

    try:
        nb_title = f"[TMP] Collection: {title[:30]}"
        print(f"[*] Creating Notebook: {nb_title}")
        rc, out, err = run_command(["notebooklm", "create", nb_title, "--json"])
        if rc != 0:
            print(f"[!] Failed to create notebook: {err}")
            return
            
        nb_data = json.loads(out)
        nb_id = nb_data.get("notebook", {}).get("id") or nb_data.get("id")
        print(f"[✔] Notebook created: {nb_id}")

        for f_path in file_paths:
            fname = os.path.basename(f_path)
            print(f"[*] Uploading {fname} to NotebookLM...")
            rc, out, err = run_command(["notebooklm", "source", "add", f_path, "-n", nb_id, "--json"])
            if rc != 0:
                print(f"[!] Failed to upload {fname}: {err}")
                continue
            src_data = json.loads(out)
            src_id = src_data.get("source", {}).get("id") or src_data.get("source_id")
            if src_id:
                print(f"    [✔] Uploaded. Waiting for processing...")
                run_command(["notebooklm", "source", "wait", src_id, "-n", nb_id])

        # Summary
        if getattr(args, 'summary', False):
            print("\n" + "="*60)
            print("【NOTEBOOKLM AI COLLECTION SUMMARY】")
            print("="*60)
            process = subprocess.Popen(
                ["notebooklm", "ask", "这是这个视频合集/选集的所有转录内容。请帮我进行深度分析，总结整个合集的核心内容、知识结构和逻辑脉络。并提炼出各章节的关键看点。请以Markdown格式输出。", "-n", nb_id, "--new"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, _ = process.communicate()
            for line in stdout.splitlines():
                if "Starting new conversation" not in line and "Answer:" not in line and "Conversation:" not in line:
                    print(line)
            print("="*60)

        # Podcast
        if getattr(args, 'podcast', False):
            print(f"\n[*] Generating Deep-Dive Audio Podcast for the collection...")
            rc, out, err = run_command(["notebooklm", "generate", "audio", "深入聊一聊这系列稿件中的核心逻辑和关键知识点", "-n", nb_id, "--json"])
            if rc == 0:
                print(f"[✔] Podcast generation started!")
                print(f"    Tip: notebooklm download audio ./.tmp/{collection_id}/collection_podcast.mp3 -n {nb_id}")
            else:
                print(f"[!] Podcast generation failed: {err}")

        print("\n" + "-"*60)
        print(f"ℹ️ TIP: You can manually delete this temporary notebook later with:")
        print(f"   notebooklm delete -n {nb_id} -y")
        print("-" * 60)

    except Exception as e:
        print(f"[!] Error during NotebookLM batch integration: {e}")

if __name__ == "__main__":
    main()
