#!/usr/bin/env python3
"""
video_compositor.py - "Mahabharat Style" HarfBuzz-Powered 1080x1920 Instagram Reel Compositor.
Features:
  1. Series Title Header at Top (Line 1: MAHABHARAT in gold, Line 2: Story name in cream)
  2. Glowing Golden Keyword (+ cream sublabel) appearing on key spoken ideas (P2_mahabharat.md)
  3. Bottom floating dark rounded subtitle pill with HarfBuzz-shaped Devanagari text
  4. Audio mixing: Narration + Atmospheric Tanpura Drone + Conch blast at start + Divine Boom on reveals
  5. Ultra-fast native FFmpeg assembly (3-5 seconds per Reel)
"""

import os
import sys
import subprocess
import imageio_ffmpeg
from sfx_generator import build_sfx_library

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

WIDTH = 1080
HEIGHT = 1920
FPS = 24

def format_ass_time(seconds: float) -> str:
    """Formats float seconds into ASS timestamp format: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass_subtitles(
    timed_beats: list,
    series_title: str,
    top_hook: str,
    top_hook_hindi: str,
    total_duration: float,
    out_ass_path: str
):
    """
    Generates a professional ASS subtitle script following P2_mahabharat.md:
      - Series Title: Pinned at top 15% (Gold all caps + Cream sub)
      - Glowing Keyword: Centered in mid-screen during key reveals
      - SubtitlePill: Floating dark pill at bottom with clean Devanagari text
    """
    series_header = series_title or "MAHABHARAT"
    tot_time_str = format_ass_time(total_duration)

    ass_template = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SeriesTitle,Georgia,44,&H004AB6E8,&H000000FF,&H0005080F,&H80000000,-1,0,0,0,100,100,2,0,1,3,2,8,60,60,110,1
Style: SeriesSub,Georgia,30,&H00CFE9F5,&H000000FF,&H0005080F,&H80000000,-1,0,0,0,100,100,1,0,1,2,1,8,60,60,165,1
Style: TopHookHindi,Nirmala UI,40,&H00FFFFFF,&H000000FF,&H001891BE,&HEB1891BE,-1,0,0,0,100,100,0,0,3,10,0,8,60,60,225,1
Style: KeyWord,Georgia,62,&H004AB6E8,&H000000FF,&H00080B1A,&H90080B1A,-1,0,0,0,100,100,2,0,1,4,3,2,60,60,450,1
Style: KeyWordSub,Nirmala UI,32,&H00CFE9F5,&H000000FF,&H0005080F,&H00000000,-1,0,0,0,100,100,1,0,1,2,1,2,60,60,405,1
Style: SubtitlePill,Nirmala UI,48,&H00FFFFFF,&H000000FF,&H005A453A,&HEB181412,-1,0,0,0,100,100,0,0,3,16,0,2,60,60,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    # 1. Pinned Series Title at Top
    events.append(f"Dialogue: 1,0:00:00.00,{tot_time_str},SeriesTitle,,0,0,0,,⚡ {series_header.upper()} ⚡")
    if top_hook:
        events.append(f"Dialogue: 1,0:00:00.00,{tot_time_str},SeriesSub,,0,0,0,,{top_hook.upper()}")
    if top_hook_hindi:
        events.append(f"Dialogue: 1,0:00:00.00,{tot_time_str},TopHookHindi,,0,0,0,,{top_hook_hindi}")

    # 2. Synchronized Beats (Keyword + Subtitle Pill)
    for beat in timed_beats:
        start_s = format_ass_time(beat["start_time"])
        end_s = format_ass_time(beat["end_time"])

        # Glowing Gold Keyword if present
        keyword = beat.get("keyword")
        sublabel = beat.get("sublabel")
        if keyword:
            events.append(f"Dialogue: 2,{start_s},{end_s},KeyWord,,0,0,0,,{keyword.upper()}")
        if sublabel:
            events.append(f"Dialogue: 2,{start_s},{end_s},KeyWordSub,,0,0,0,,{sublabel.upper()}")

        # Bottom Subtitle Pill in Devanagari
        text = beat.get("text_hindi") or beat["text"]
        words = text.split()
        if len(words) > 9:
            mid = len(words) // 2
            text = " ".join(words[:mid]) + "\\N" + " ".join(words[mid:])
        events.append(f"Dialogue: 0,{start_s},{end_s},SubtitlePill,,0,0,0,,{text}")

    full_ass = ass_template + "\n".join(events) + "\n"
    with open(out_ass_path, "w", encoding="utf-8") as f:
        f.write(full_ass)

    return out_ass_path

def build_mixed_soundtrack(narration_path: str, assets_dir: str, total_duration: float) -> str:
    """
    Mixes voiceover narration with procedural sound design:
      - Soft mystical tanpura drone bed (looping at low volume)
      - Conch shell horn at the opening hook (0.0s)
      - Divine reveal sub-bass boom at 7.0s
    """
    sfx_lib = build_sfx_library(assets_dir)
    conch = sfx_lib["conch"]
    boom = sfx_lib["boom"]
    drone = sfx_lib["drone"]
    mixed_audio = os.path.join(assets_dir, "soundtrack_master.mp3")

    # Complex audio filter to balance voice, ambient drone, and sfx
    # [0:a] Narration (full volume 1.1)
    # [1:a] Drone (volume 0.18)
    # [2:a] Conch blast (volume 0.35, delayed 0.1s)
    # [3:a] Divine boom (volume 0.45, delayed 6.5s)
    filter_complex = (
        "[0:a]volume=1.15[vo];"
        "[1:a]volume=0.18,atrim=0:{dur}[drone];"
        "[2:a]volume=0.35,adelay=100|100[conch];"
        "[3:a]volume=0.45,adelay=6500|6500[boom];"
        "[vo][drone][conch][boom]amix=inputs=4:duration=first:dropout_transition=2[aout]"
    ).format(dur=int(total_duration) + 1)

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", narration_path,
        "-i", drone,
        "-i", conch,
        "-i", boom,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        mixed_audio
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(mixed_audio) and os.path.getsize(mixed_audio) > 1000:
        return mixed_audio
    # Fallback to plain narration if complex mixing fails
    return narration_path

def render_reel_video(
    timed_beats: list,
    series_title: str,
    top_hook: str,
    audio_path: str,
    output_path: str,
    assets_dir: str,
    top_hook_hindi: str = None
):
    """
    Renders the complete 1080x1920 Instagram Reel with 2D scenes, sound design,
    and HarfBuzz-shaped Devanagari typography.
    """
    from scene_generator import get_scene_image

    print(f"[RENDER] Rendering {len(timed_beats)} smooth animated Ken Burns scenes...")
    clip_paths = []
    total_duration = 0.0

    for idx, beat in enumerate(timed_beats):
        duration = max(1.5, beat["duration"])
        scene_name = beat.get("scene", f"scene_{idx}")
        scene_img_path = get_scene_image(scene_name, assets_dir)
        total_duration += duration

        clip_path = os.path.join(assets_dir, f"motion_{idx:02d}.mp4")
        total_frames = int(duration * FPS) + 2

        # Rich cinematic camera moves from P2_mahabharat.md:
        # Alternating slow push-in, slow pull-out, tilt-up reveal, and sideways parallax drift
        motion_type = idx % 4
        if motion_type == 0:
            vf_pan = f"zoompan=z='min(zoom+0.0010,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        elif motion_type == 1:
            vf_pan = f"zoompan=z='if(lte(zoom,1.0),1.14,max(1.001,zoom-0.0010))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        elif motion_type == 2:
            vf_pan = f"zoompan=z='1.10':x='iw*0.06*(on/{total_frames})':y='ih/2-(ih/zoom/2)':d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        else:
            vf_pan = f"zoompan=z='1.10':x='iw/2-(iw/zoom/2)':y='ih*0.10*(1-on/{total_frames})':d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"

        clip_cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1",
            "-i", scene_img_path,
            "-vf", vf_pan,
            "-t", f"{duration:.2f}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            clip_path
        ]
        subprocess.run(clip_cmd, capture_output=True, check=True)
        escaped_clip = os.path.abspath(clip_path).replace(chr(92), "/")
        clip_paths.append(f"file '{escaped_clip}'")

    concat_txt_path = os.path.join(assets_dir, "concat_scenes.txt")
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(clip_paths))

    # Generate ASS subtitle file
    ass_file = os.path.join(assets_dir, "subtitles.ass")
    generate_ass_subtitles(
        timed_beats=timed_beats,
        series_title=series_title,
        top_hook=top_hook,
        top_hook_hindi=top_hook_hindi,
        total_duration=total_duration,
        out_ass_path=ass_file
    )

    # Build audio soundtrack with drone + conch + boom sound design
    final_audio = build_mixed_soundtrack(audio_path, assets_dir, total_duration)

    escaped_ass = ass_file.replace("\\", "/").replace(":", "\\:")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    print(f"[RENDER] Running native FFmpeg assemble -> {output_path}")
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt_path,
        "-i", final_audio,
        "-vf", f"fps={FPS},format=yuv420p,ass='{escaped_ass}'",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {res.stderr[-500:]}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[RENDER] Successfully created Reel: {output_path} ({size_mb:.2f} MB)")
    return output_path
