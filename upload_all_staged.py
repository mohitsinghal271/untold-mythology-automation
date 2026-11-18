#!/usr/bin/env python3
"""
upload_all_staged.py - Publishes all staged Mahabharat reels to Instagram.
Uses the verified browser session ID from instagram_credentials.json.
"""

import os
import sys
import json
import time

def upload_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    creds_file = os.path.join(base_dir, "instagram_credentials.json")
    if not os.path.exists(creds_file):
        print("[!] instagram_credentials.json not found!")
        return

    with open(creds_file, "r", encoding="utf-8") as f:
        creds = json.load(f)

    session_id = creds.get("sessionid")
    if not session_id:
        print("[!] No sessionid found in credentials!")
        return

    import urllib.parse
    session_id = urllib.parse.unquote(str(session_id))
    username = creds.get("username", "untold_mythology_legends")

    from instagrapi import Client
    cl = Client()
    cl.delay_range = [2, 5]

    session_cache = os.path.join(base_dir, "ig_session.json")
    print(f"[AUTH] Connecting to Instagram as @{username} via session ID...")
    if os.path.exists(session_cache):
        try:
            cl.load_settings(session_cache)
        except Exception:
            pass

    try:
        cl.login_by_sessionid(session_id)
    except Exception as e:
        print(f"[AUTH NOTE] login_by_sessionid check notice: {e}")
        user_id = session_id.split(":")[0]
        cl.set_cookie("sessionid", session_id)
        cl.set_cookie("ds_user_id", user_id)
        cl.user_id = user_id

    try:
        cl.dump_settings(session_cache)
    except Exception:
        pass
    print(f"[AUTH] Authenticated as @{username} (ID: {cl.user_id})!")

    staged_root = os.path.join(base_dir, "output", "ready_to_upload")
    if not os.path.exists(staged_root):
        print("[!] No staged reels directory found.")
        return

    story_keys = [
        "karna_secret",
        "abhimanyu_chakravyuh",
        "krishna_vow",
        "ashwatthama_curse",
        "eklavya_thumb"
    ]

    published = []
    for idx, key in enumerate(story_keys, 1):
        reel_dir = os.path.join(staged_root, key)
        video_path = os.path.join(reel_dir, f"{key}.mp4")
        caption_path = os.path.join(reel_dir, "caption.txt")
        cover_path = os.path.join(reel_dir, "cover.jpg")

        if not os.path.exists(video_path):
            print(f"[-] Reel {key} not yet rendered, skipping...")
            continue

        caption = ""
        if os.path.exists(caption_path):
            with open(caption_path, "r", encoding="utf-8") as f:
                caption = f.read()

        cover = cover_path if os.path.exists(cover_path) else None

        print(f"\n[UPLOAD {idx}/{len(story_keys)}] Uploading {key} ({os.path.getsize(video_path)/(1024*1024):.2f} MB)...")
        try:
            media = cl.clip_upload(
                video_path,
                caption=caption,
                thumbnail=cover
            )
            url = f"https://www.instagram.com/reel/{media.code}/" if hasattr(media, "code") else f"ID: {media.pk}"
            print(f"[SUCCESS] 🎉 Published {key} successfully!")
            print(f"🔗 Live Reel: {url}")
            published.append({"key": key, "url": url, "id": str(media.pk)})

            # Safe cooldown between Instagram uploads to protect account health
            if idx < len(story_keys):
                print("[COOLDOWN] Waiting 15s before next upload...")
                time.sleep(15)

        except Exception as e:
            print(f"[!] Failed to upload {key}: {e}")

    print("\n" + "=" * 60)
    print(f"🏆 UPLOAD SUMMARY: {len(published)} Reels Published Live!")
    for p in published:
        print(f"  - {p['key']}: {p['url']}")
    print("=" * 60)
    return published

if __name__ == "__main__":
    upload_all()
