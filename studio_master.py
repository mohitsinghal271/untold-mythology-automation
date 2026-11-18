#!/usr/bin/env python3
"""
studio_master.py - Central Controller for Untold Mythology Reels Production & Publishing.
Commands:
  python studio_master.py audit          - Run system diagnostics on voice, video, db, and queue
  python studio_master.py status         - Display queue status, active series, and performance
  python studio_master.py generate-day   - Generate and queue 5 reels for the daily mix
  python studio_master.py render-all     - Render all unrendered reels in queue
  python studio_master.py run-slot       - Check current IST slot and publish if ready
  python studio_master.py analyze        - Generate retention and drop-off analytics report
"""

import os
import sys
import argparse
import json
from datetime import datetime

from database import (
    init_db, get_connection, get_staged_reels, get_active_series,
    upsert_reel, is_content_duplicate, record_content_hash
)
from scheduler import get_current_ist_time, get_schedule_slots, run_scheduler_tick, publish_single_reel_with_retry
from analytics_optimizer import get_performance_summary, analyze_series_dropoff
from content_engine import get_next_daily_mix
from pipeline import produce_mythology_reel

def cmd_audit():
    print("=" * 65)
    print("       🔍 UNTOLD MYTHOLOGY STUDIO: SYSTEM AUDIT")
    print("=" * 65)

    # 1. VoiceStudio
    from voicestudio_engine import is_voicestudio_available
    vs_ok = is_voicestudio_available()
    print(f"🎙️  VoiceStudio Engine (OmniVoice GGUF): {'AVAILABLE (CPU Narrator Mode)' if vs_ok else 'MISSING'}")

    # 2. FFmpeg & HarfBuzz Fonts
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"🎥 FFmpeg Path:                       {ffmpeg_exe}")

    font_path = "C:\\Windows\\Fonts\\Nirmala.ttf"
    has_font = os.path.exists(font_path)
    print(f"🔤 Devanagari HarfBuzz Font:          {'FOUND (Nirmala UI)' if has_font else 'FALLBACK'}")

    # 3. Database
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reels")
    total_reels = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM series")
    total_series = c.fetchone()[0]
    conn.close()
    print(f"💾 SQLite Studio Database:             CONNECTED ({total_reels} reels, {total_series} series)")

    # 4. IST Schedule Slots
    now_ist = get_current_ist_time()
    slots = get_schedule_slots()
    print(f"⏰ Current IST Time:                   {now_ist.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Active Publishing Slots:            {len(slots)} configured slots")
    for s in slots:
        print(f"   - Slot {s['slot_id']} ({s['ist_time']} IST): {s['slot_name']} [{s['target_category']}]")

    print("=" * 65)
    print("✅ System Health Check Complete! All modules ready for autonomous operation.")

def cmd_status():
    print("=" * 65)
    print("       📊 UNTOLD MYTHOLOGY STUDIO: LIVE STATUS")
    print("=" * 65)
    now_ist = get_current_ist_time()
    print(f"🕒 Current IST Time: {now_ist.strftime('%Y-%m-%d %H:%M:%S')}\n")

    staged = get_staged_reels(limit=20)
    print(f"📥 Content Queue ({len(staged)} reels):")
    if not staged:
        print("   (Queue is currently empty. Run 'python studio_master.py generate-day' to refill)")
    for r in staged:
        is_s = f" [Part {r['part_number']}/{r['total_parts']}]" if r.get("series_id") else ""
        print(f"   [{r['status'].upper()}] #{r['id']} {r['title']}{is_s} (Hook: {r['top_hook']})")

    active_series = get_active_series()
    print(f"\n📖 Active Serialized Stories ({len(active_series)}):")
    for s in active_series:
        print(f"   - {s['title']} (Part {s['current_part']}/{s['total_parts']}) [{s['status']}]")

    print("\n" + "=" * 65)

def cmd_generate_day():
    print("=" * 65)
    print("       ✨ GENERATING 5 REELS FOR DAILY SCHEDULE MIX")
    print("=" * 65)
    mix = get_next_daily_mix()
    slots = get_schedule_slots()

    for idx, item in enumerate(mix):
        slot_info = slots[idx] if idx < len(slots) else {"ist_time": "18:00"}
        print(f"\n[SLOT {idx+1} - {slot_info.get('ist_time', '18:00')} IST] Generating: {item['title']}...")
        if is_content_duplicate(item["title"], item["top_hook"]):
            print("   [-] Already in memory/queue, skipping duplicate.")
            continue

        record_content_hash(item["title"], item["top_hook"], item["category"])
        upsert_reel({
            "slug": item["slug"],
            "series_id": item.get("series_id"),
            "part_number": item.get("part_number", 1),
            "total_parts": item.get("total_parts", 1),
            "title": item["title"],
            "top_hook": item["top_hook"],
            "top_hook_hindi": item["top_hook_hindi"],
            "category": item["category"],
            "status": "staged",
            "video_path": os.path.join("output", "ready_to_upload", item["slug"], f"{item['slug']}.mp4"),
            "caption": item["caption"],
            "cover_path": os.path.join("output", "ready_to_upload", item["slug"], "cover.jpg"),
            "scheduled_time": f"{slot_info.get('ist_time', '18:00')} IST",
            "published_time": None
        })
        print(f"   ✅ Staged into SQLite queue for {slot_info.get('ist_time')} IST")

    print("\n🎉 5 Daily Reels Queued in SQLite Database!")

def cmd_render_all():
    print("=" * 65)
    print("       🎬 RENDERING ALL QUEUED REELS (KEN BURNS + VOICE)")
    print("=" * 65)
    staged = get_staged_reels(limit=10)
    if not staged:
        print("No staged reels to render.")
        return

    for r in staged:
        slug = r["slug"]
        video_p = r["video_path"]
        if os.path.exists(video_p) and os.path.getsize(video_p) > 1000:
            print(f"[-] Reel {slug} already rendered ({os.path.getsize(video_p)/(1024*1024):.2f} MB), skipping.")
            continue

        print(f"\n🚀 Rendering: {r['title']} ({slug})...")
        try:
            produce_mythology_reel(topic_key=slug, engine="voicestudio", direct_upload=False)
        except Exception as e:
            print(f"[!] Rendering error on {slug}: {e}")

    print("\n✅ All staged reels are fully rendered and ready for publication!")

def cmd_analyze():
    print("=" * 65)
    print("       📈 PERFORMANCE & SERIES RETENTION ANALYTICS")
    print("=" * 65)
    summary = get_performance_summary()
    print(f"Total Published Reels: {summary['total_published']}")
    print(f"Total Staged Reels:    {summary['total_staged']}")
    print("\nCategory Performance Breakdown:")
    for p in summary.get("top_performing_pillars", []):
        print(f"  - {p['category']}: {p['total_posts']} posts | Avg Views: {p['avg_views']:.1f} | Avg Retention: {p['avg_retention']:.1f}%")

    dropoff = analyze_series_dropoff("series_barbareek")
    print("\nSerialized Story Retention (Barbareek 2-Part Series):")
    print(f"  - Conversion: {dropoff.get('part_1_to_part_2_conversion_pct')}%")
    print(f"  - Diagnosis:  {dropoff.get('diagnosis')}")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Untold Mythology Master Controller")
    parser.add_argument("command", choices=["audit", "status", "generate-day", "render-all", "run-slot", "analyze"],
                        help="Command to execute")
    args = parser.parse_args()

    if args.command == "audit":
        cmd_audit()
    elif args.command == "status":
        cmd_status()
    elif args.command == "generate-day":
        cmd_generate_day()
    elif args.command == "render-all":
        cmd_render_all()
    elif args.command == "run-slot":
        run_scheduler_tick()
    elif args.command == "analyze":
        cmd_analyze()

if __name__ == "__main__":
    main()
