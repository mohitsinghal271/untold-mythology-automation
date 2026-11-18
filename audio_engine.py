#!/usr/bin/env python3
"""
audio_engine.py - Synthesizes expressive Hindi narration using VoiceStudio (OmniVoice GGUF)
with seamless Edge-TTS fallback and sentence-level timestamps.
"""

import os
import sys
import asyncio
import json
import subprocess
import shutil
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

try:
    from voicestudio_engine import synthesize_with_voicestudio, is_voicestudio_available
except ImportError:
    def is_voicestudio_available(): return False
    synthesize_with_voicestudio = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

async def synthesize_sentence_edgetts(text: str, output_path: str, voice: str = "hi-IN-MadhurNeural", rate: str = "-2%"):
    """Fallback synthesis with Edge-TTS."""
    comm = edge_tts.Communicate(text, voice=voice, rate=rate)
    await comm.save(output_path)

def get_audio_duration(file_path: str) -> float:
    """Returns duration in seconds using ffmpeg."""
    cmd = [FFMPEG_EXE, "-i", file_path]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", res.stderr)
    if m:
        h, mins, s = map(float, m.groups())
        return round(h * 3600 + mins * 60 + s, 2)
    return 3.0

def build_narration_track(
    beats: list,
    output_dir: str,
    engine: str = "voicestudio",
    voice: str = "hi-IN-MadhurNeural"
) -> tuple[str, list]:
    """
    Synthesizes each beat using VoiceStudio (or Edge-TTS fallback), calculates timestamps,
    and merges into master audio.
    """
    os.makedirs(output_dir, exist_ok=True)
    timed_beats = []
    current_time = 0.0
    concat_list = os.path.join(output_dir, "concat_audio.txt")
    file_entries = []

    use_vs = (engine == "voicestudio") and is_voicestudio_available()
    print(f"[AUDIO] Engine selected: {'VoiceStudio (OmniVoice GGUF)' if use_vs else 'Edge-TTS'}")

    for idx, beat in enumerate(beats):
        beat_audio_name = f"beat_{idx:02d}.mp3"
        beat_audio_path = os.path.join(output_dir, beat_audio_name)

        # Prioritize Hindi Devanagari text for natural pronunciation
        script_text = beat.get("text_hindi") or beat["text"]

        # Only synthesize if not already cached
        if not (os.path.exists(beat_audio_path) and os.path.getsize(beat_audio_path) > 1000):
            success = False
            if use_vs:
                try:
                    success = synthesize_with_voicestudio(
                        text=script_text,
                        output_path=beat_audio_path,
                        language="Hindi",
                        steps=5
                    )
                except Exception as e:
                    print(f"[!] VoiceStudio error on beat {idx}: {e}")
                    success = False

            if not success:
                print(f"[*] Falling back to Edge-TTS for beat {idx}...")
                asyncio.run(synthesize_sentence_edgetts(script_text, beat_audio_path, voice=voice))

        dur = get_audio_duration(beat_audio_path)
        start_t = current_time
        end_t = current_time + dur

        timed_beats.append({
            "id": idx,
            "text": script_text,
            "text_hindi": beat.get("text_hindi", script_text),
            "scene": beat.get("scene", f"scene_{idx}"),
            "keyword": beat.get("keyword"),
            "sublabel": beat.get("sublabel"),
            "start_time": round(start_t, 2),
            "end_time": round(end_t, 2),
            "duration": round(dur, 2),
            "audio_file": beat_audio_path
        })

        escaped_file = os.path.abspath(beat_audio_path).replace(chr(92), "/")
        file_entries.append(f"file '{escaped_file}'")
        current_time = end_t

    # Write concat list
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write("\n".join(file_entries))

    # Merge via ffmpeg
    master_audio = os.path.join(output_dir, "master_narration.mp3")
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        master_audio
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    return master_audio, timed_beats

if __name__ == "__main__":
    from mythology_scriptwriter import get_story
    story = get_story("ravan")
    test_dir = r"D:\instagram-automation\temp\vs_test"
    master, timed = build_narration_track(story["beats"][:2], test_dir, engine="voicestudio")
    print("Master audio created:", master)
