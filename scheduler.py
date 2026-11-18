#!/usr/bin/env python3
"""
scheduler.py - 5-Slot Daily Instagram Publishing Scheduler (IST).
Implements Phase 2:
  - 5 Configurable Daily Publishing Slots in India Standard Time (IST)
  - Content Queue Management & Auto-Refill
  - Exponential Backoff & Retry Logic
  - Anti-Duplicate Protection
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from database import (
    get_connection, get_staged_reels, mark_reel_published,
    mark_reel_failed, upsert_reel, is_content_duplicate, record_content_hash
)

# India Standard Time (UTC + 5:30)
IST_OFFSET = timedelta(hours=5, minutes=30)

def get_current_ist_time() -> datetime:
    """Returns the current time in IST."""
    return datetime.now(timezone.utc) + IST_OFFSET

def get_schedule_slots() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM schedule_slots WHERE is_active = 1 ORDER BY ist_time ASC")
    slots = [dict(r) for r in c.fetchall()]
    conn.close()
    return slots

def find_current_or_next_slot() -> Optional[Dict[str, Any]]:
    now_ist = get_current_ist_time()
    now_str = now_ist.strftime("%H:%M")
    slots = get_schedule_slots()
    if not slots:
        return None

    for s in slots:
        if s["ist_time"] >= now_str:
            return s
    # If past the last slot, wrap to first slot tomorrow
    return slots[0]

def publish_single_reel_with_retry(reel: Dict[str, Any], max_retries: int = 3) -> bool:
    """
    Attempts to publish a staged reel to Instagram with exponential backoff.
    """
    slug = reel["slug"]
    video_path = reel["video_path"]
    caption = reel["caption"]
    cover_path = reel["cover_path"]

    if not (os.path.exists(video_path) and os.path.getsize(video_path) > 1000):
        print(f"[!] Reel {slug} video file missing or empty: {video_path}")
        mark_reel_failed(slug, "Video file missing or corrupt")
        return False

    # Check for credentials
    base_dir = os.path.dirname(os.path.abspath(__file__))
    creds_file = os.path.join(base_dir, "instagram_credentials.json")
    if not os.path.exists(creds_file):
        print(f"[STAGE ONLY] No credentials file found. Reel {slug} remains safely staged.")
        return False

    with open(creds_file, "r", encoding="utf-8") as f:
        creds = json.load(f)

    session_id = creds.get("sessionid")
    if not session_id:
        print(f"[STAGE ONLY] No active sessionid. Reel {slug} remains staged.")
        return False

    import urllib.parse
    session_id = urllib.parse.unquote(str(session_id))
    username = creds.get("username", "untold_mythology_legends")

    for attempt in range(1, max_retries + 1):
        print(f"\n[UPLOAD ATTEMPT {attempt}/{max_retries}] Publishing {slug} as @{username}...")
        try:
            from instagrapi import Client
            cl = Client()
            cl.delay_range = [2, 5]

            user_id = session_id.split(":")[0]
            cl.settings["cookies"] = {"sessionid": session_id, "ds_user_id": user_id}
            cl.init()
            cl.authorization_data = {
                "ds_user_id": user_id,
                "sessionid": session_id,
                "should_use_header_over_cookies": True
            }
            cl.private.cookies.set("ds_user_id", user_id)
            cl.private.cookies.set("sessionid", session_id)
            cl.private.headers.update(cl.base_headers)
            cl.private.headers.update({"Authorization": cl.authorization})

            media = cl.clip_upload(
                video_path,
                caption=caption,
                thumbnail=cover_path if (cover_path and os.path.exists(cover_path)) else None
            )

            url = f"https://www.instagram.com/reel/{media.code}/" if hasattr(media, "code") else f"ID: {media.pk}"
            print(f"[SUCCESS] 🎉 Published {slug} successfully!")
            print(f"🔗 Live Reel: {url}")
            mark_reel_published(slug, str(media.pk), url)
            return True

        except Exception as e:
            err_msg = str(e)
            print(f"[!] Upload attempt {attempt} failed: {err_msg}")
            if "login_required" in err_msg.lower() or "checkpoint" in err_msg.lower():
                print("[AUTH ERROR] Session expired or checkpoint triggered. Needs refreshed session ID.")
                mark_reel_failed(slug, f"Auth expired: {err_msg}")
                return False

            # Exponential backoff: 10s, 30s, 60s
            backoff_sec = 10 * (2 ** (attempt - 1))
            if attempt < max_retries:
                print(f"[RETRY] Waiting {backoff_sec}s before retry...")
                time.sleep(backoff_sec)
            else:
                mark_reel_failed(slug, f"Failed after {max_retries} attempts: {err_msg}")

    return False

def run_scheduler_tick():
    """
    Called periodically or as a daemon:
      1. Checks current IST time.
      2. If inside a publishing window and a scheduled reel is ready, publishes it.
      3. Refills queue if staged count < 5.
    """
    now_ist = get_current_ist_time()
    now_hm = now_ist.strftime("%H:%M")
    print(f"\n[SCHEDULER] Current IST Time: {now_ist.strftime('%Y-%m-%d %H:%M:%S')} (Slot check: {now_hm})")

    staged = get_staged_reels(limit=5)
    print(f"[QUEUE] Currently {len(staged)} reels staged in queue.")

    if not staged:
        print("[QUEUE] Queue is low! Auto-generating new content batch...")
        from content_engine import get_next_daily_mix
        from pipeline import produce_mythology_reel
        mix = get_next_daily_mix()
        for item in mix:
            if not is_content_duplicate(item["title"], item["top_hook"]):
                print(f"  + Queuing new reel: {item['title']}")
                record_content_hash(item["title"], item["top_hook"], item["category"])
                # Stage reel record in database
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
                    "scheduled_time": None,
                    "published_time": None
                })

    return get_staged_reels(limit=5)

if __name__ == "__main__":
    run_scheduler_tick()
