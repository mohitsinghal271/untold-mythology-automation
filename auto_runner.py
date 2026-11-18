#!/usr/bin/env python3
"""
auto_runner.py - 24/7 Autonomous Scheduler & Reel Publisher for GitHub Actions.
Operates fully unattended in cloud runners:
  1. Reads Instagram credentials from GitHub Secrets (env vars) or local file.
  2. Tracks publication state in posted_history.json so stories are never duplicated.
  3. Uses Edge-TTS (hi-IN-MadhurNeural) for zero-dependency cloud voiceover synthesis.
  4. Generates high-impact 1080x1920 2D vector Mahabharat scenes with sound design.
  5. Publishes directly to Instagram via instagrapi (or stages if direct upload disabled).
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "posted_history.json"
CREDS_FILE = BASE_DIR / "instagram_credentials.json"

def ensure_credentials_from_env():
    """Builds instagram_credentials.json from environment variables if present (GitHub Secrets)."""
    env_username = os.environ.get("IG_USERNAME")
    env_sessionid = os.environ.get("IG_SESSIONID")
    env_password = os.environ.get("IG_PASSWORD")

    if env_username and env_sessionid:
        print("[SETUP] Injecting Instagram credentials from GitHub Secrets...")
        creds = {
            "username": env_username.strip(),
            "sessionid": env_sessionid.strip()
        }
        if env_password:
            creds["password"] = env_password.strip()

        with open(CREDS_FILE, "w", encoding="utf-8") as f:
            json.dump(creds, f, indent=2)
        print(f"[SETUP] Successfully configured credentials for @{env_username}")
    elif not CREDS_FILE.exists():
        print("[WARN] Neither GitHub Secrets nor instagram_credentials.json found!")

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posted_topics": [], "history": [], "total_posted": 0}

def save_history(history: dict):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def pick_next_topic(history: dict, requested_topic: str = None) -> str:
    from mythology_scriptwriter import list_all_keys
    all_keys = list_all_keys()
    posted = history.get("posted_topics", [])

    if requested_topic and requested_topic != "auto":
        for k in all_keys:
            if requested_topic.lower() in k.lower():
                return k
        return requested_topic

    # Pick next unposted topic
    for key in all_keys:
        if key not in posted:
            return key

    # If all have been posted, cycle through starting from the oldest
    print("[INFO] All catalog topics have been published once. Cycling through catalog...")
    cycle_index = len(posted) % len(all_keys)
    return all_keys[cycle_index]

def run_autonomous_cycle(requested_topic: str = "auto", direct_upload: bool = True):
    print("=" * 70)
    print("🤖 UNTOLD MYTHOLOGY 24/7 AUTONOMOUS REEL ENGINE")
    print(f"⏰ Execution Time: {datetime.now(timezone.utc).isoformat()} UTC")
    print("=" * 70)

    # 1. Environment & Credentials
    ensure_credentials_from_env()

    # 2. Pick Topic
    history = load_history()
    topic_key = pick_next_topic(history, requested_topic)
    print(f"[TARGET] Selected Topic: '{topic_key}'")

    # 3. Produce Reel via Pipeline
    from pipeline import produce_mythology_reel
    # On GitHub Actions runners, engine='edge_tts' is completely headless & fast
    result = produce_mythology_reel(
        topic_key=topic_key,
        engine="edge_tts",
        direct_upload=direct_upload
    )

    # 4. Update History
    posted_topics = history.get("posted_topics", [])
    if topic_key not in posted_topics:
        posted_topics.append(topic_key)
    history["posted_topics"] = posted_topics

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": topic_key,
        "video": result.get("video"),
        "cover": result.get("cover"),
        "uploaded": result.get("uploaded", direct_upload),
        "direct_upload_success": result.get("uploaded", False)
    }
    history.setdefault("history", []).append(entry)
    history["total_posted"] = len(history["history"])
    history["last_run"] = datetime.now(timezone.utc).isoformat()
    save_history(history)

    print("\n" + "=" * 70)
    print("✅ AUTONOMOUS CYCLE FINISHED SUCCESSFULLY!")
    print(f"📦 Staged Video: {result.get('video')}")
    print(f"🖼️ Cover: {result.get('cover')}")
    print(f"📊 Total Lifetime Reels: {history['total_posted']}")
    print("=" * 70)

    # Set GitHub Actions output environment variable if running in CI
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"video={result.get('video')}\n")
            f.write(f"topic_key={topic_key}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="24/7 Autonomous Reels Runner")
    parser.add_argument("--topic", default="auto", help="Topic key or 'auto'")
    parser.add_argument("--no-upload", action="store_true", help="Stage only, do not upload")
    args = parser.parse_args()

    run_autonomous_cycle(requested_topic=args.topic, direct_upload=not args.no_upload)
