#!/usr/bin/env python3
"""
pipeline.py - Master Autonomous "Mahabharat Style" Instagram Reel Production & Publishing Engine.
Features:
  - 5 High-Impact Curated Stories following P2_mahabharat.md
  - VoiceStudio (OmniVoice GGUF) / Edge-TTS Voiceover
  - Procedural Sound Design: Conch horn, Tanpura drone, Divine reveal boom
  - Authentic Hindi Devanagari (देवनागरी) HarfBuzz Typography
  - Automated 1-Click Publishing to Instagram via verified Session ID
"""

import os
import sys
import json
import argparse
import time

from mythology_scriptwriter import get_story, list_all_keys
from audio_engine import build_narration_track
from video_compositor import render_reel_video
from instagram_uploader import stage_reel_for_upload, try_direct_upload

def produce_mythology_reel(topic_key: str = "karna_secret", engine: str = "voicestudio", direct_upload: bool = False):
    print("=" * 70)
    print(f"    🎬 MAHABHARAT REEL GENERATOR: {topic_key.upper()}")
    print("=" * 70)

    start_time = time.time()
    story = get_story(topic_key)
    print(f"[STEP 1] Topic Selected: {story['topic']}")
    print(f"         Series Title:   {story.get('series_title', 'MAHABHARAT')}")
    print(f"         Top Hook:       {story['top_hook']} | {story.get('top_hook_hindi', '')}")
    print(f"         Total Beats:    {len(story['beats'])}")

    # Work paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, "config.json")
    cfg = {}
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)

    temp_base = cfg.get("temp_dir", "output/temp")
    out_base = cfg.get("output_dir", "output/ready_to_upload")
    if not os.path.isabs(temp_base):
        temp_base = os.path.join(base_dir, temp_base)
    if not os.path.isabs(out_base):
        out_base = os.path.join(base_dir, out_base)
    temp_dir = os.path.join(temp_base, topic_key)
    output_dir = out_base
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Step 2: Voiceover Narration
    print(f"\n[STEP 2] Synthesizing Voiceover via {engine}...")
    master_audio, timed_beats = build_narration_track(
        story["beats"],
        temp_dir,
        engine=engine
    )
    total_audio_duration = sum(b["duration"] for b in timed_beats)
    print(f"         Audio complete: {total_audio_duration:.1f}s across {len(timed_beats)} beats")

    # Step 3: Video Compositing with Sound Design & Devanagari Typography
    print("\n[STEP 3] Rendering 1080x1920 9:16 Video (Mahabharat Style + Sound Design)...")
    temp_video = os.path.join(temp_dir, f"{topic_key}_raw.mp4")
    render_reel_video(
        timed_beats=timed_beats,
        series_title=story.get("series_title", "MAHABHARAT"),
        top_hook=story["top_hook"],
        top_hook_hindi=story.get("top_hook_hindi"),
        audio_path=master_audio,
        output_path=temp_video,
        assets_dir=temp_dir
    )

    # Step 4: Staging
    print("\n[STEP 4] Staging Publishing Package (MP4 + Caption + Cover Thumbnail)...")
    package = stage_reel_for_upload(
        video_path=temp_video,
        caption=story["caption"],
        slug=topic_key,
        base_out_dir=output_dir
    )

    # Step 5: Direct Instagram Publishing
    uploaded = False
    if direct_upload:
        print("\n[STEP 5] 🚀 Uploading Reel directly to Instagram via Session ID...")
        uploaded = try_direct_upload(package["video_path"], story["caption"], package["cover_path"])

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"🎉 REEL [{topic_key}] COMPLETE in {elapsed:.1f}s! (Published: {uploaded})")
    print(f"📁 Video Location:   {package['video_path']}")
    print(f"📝 Caption File:     {package['caption_path']}")
    print(f"🖼️ Cover Thumbnail:  {package['cover_path']}")
    print("=" * 70)

    return {
        "key": topic_key,
        "topic": story["topic"],
        "video": package["video_path"],
        "cover": package["cover_path"],
        "uploaded": uploaded
    }

def publish_all_five_reels(engine: str = "voicestudio", direct_upload: bool = True):
    all_keys = list_all_keys()
    results = []
    print("\n" + "#" * 70)
    print(f"🚀 BATCH LAUNCH: PRODUCING & PUBLISHING {len(all_keys)} MAHABHARAT REELS")
    print("#" * 70 + "\n")

    for i, key in enumerate(all_keys, 1):
        print(f"\n>>> PROCESSING REEL {i}/{len(all_keys)}: {key.upper()} <<<\n")
        try:
            res = produce_mythology_reel(topic_key=key, engine=engine, direct_upload=direct_upload)
            results.append(res)
            # Gentle pacing between Instagram uploads
            if direct_upload and i < len(all_keys):
                print("\n[COOLDOWN] Waiting 12 seconds before next Instagram upload...")
                time.sleep(12)
        except Exception as e:
            print(f"[!] Error on {key}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "#" * 70)
    print("🏆 ALL 5 REELS COMPLETED!")
    for r in results:
        status_icon = "✅ PUBLISHED" if r.get("uploaded") else "📁 STAGED"
        print(f"  - {status_icon}: {r['key']} -> {r['video']}")
    print("#" * 70)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce Mahabharat Cartoon Reel")
    parser.add_argument("--topic", type=str, default="karna_secret", help="Topic key or 'all'")
    parser.add_argument("--engine", type=str, default="voicestudio", choices=["voicestudio", "edgetts"], help="TTS engine")
    parser.add_argument("--upload", action="store_true", help="Attempt direct Instagram upload")
    args = parser.parse_args()

    if args.topic.lower() == "all":
        publish_all_five_reels(engine=args.engine, direct_upload=args.upload)
    else:
        produce_mythology_reel(topic_key=args.topic, engine=args.engine, direct_upload=args.upload)
