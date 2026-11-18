#!/usr/bin/env python3
"""
instagram_uploader.py - Handles Instagram Reels Publishing.
Supports:
  1. Automated direct upload via instagrapi (when credentials provided)
  2. Staged publishing package export (video.mp4, caption.txt, cover.jpg)
"""

import os
import sys
import json
import shutil
import subprocess
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def extract_cover_frame(video_path: str, cover_path: str, timestamp_sec: float = 1.0):
    """Extracts a high quality cover frame from the video."""
    try:
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", video_path,
            "-ss", str(timestamp_sec),
            "-vframes", "1",
            "-q:v", "2",
            cover_path
        ]
        subprocess.run(cmd, capture_output=True)
    except Exception as e:
        print("[!] Cover frame extraction note:", e)

def stage_reel_for_upload(video_path: str, caption: str, slug: str, base_out_dir: str = "output/ready_to_upload") -> dict:
    """
    Saves video, caption, and cover thumbnail in output/ready_to_upload/<slug>/
    """
    package_dir = os.path.join(base_out_dir, slug)
    os.makedirs(package_dir, exist_ok=True)

    dest_video = os.path.join(package_dir, f"{slug}.mp4")
    shutil.copy2(video_path, dest_video)

    dest_caption = os.path.join(package_dir, "caption.txt")
    with open(dest_caption, "w", encoding="utf-8") as f:
        f.write(caption)

    dest_cover = os.path.join(package_dir, "cover.jpg")
    extract_cover_frame(dest_video, dest_cover, timestamp_sec=1.5)

    print(f"[PACKAGE] Staged complete Reel package at: {package_dir}")
    print(f"  - Video: {dest_video}")
    print(f"  - Caption: {dest_caption}")
    print(f"  - Cover: {dest_cover}")

    return {
        "package_dir": package_dir,
        "video_path": dest_video,
        "caption_path": dest_caption,
        "cover_path": dest_cover
    }

def try_direct_upload(video_path: str, caption: str, cover_path: str = None) -> bool:
    """Attempts direct upload to Instagram via instagrapi if installed and configured."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    creds_file = os.path.join(base_dir, "instagram_credentials.json")
    if not os.path.exists(creds_file):
        print("[INFO] No instagram_credentials.json found. Reel is staged for manual/app upload.")
        return False

    try:
        from instagrapi import Client
    except ImportError:
        print("[INFO] instagrapi library not installed. Install with 'pip install instagrapi' for direct API uploads.")
        return False

    try:
        with open(creds_file, "r", encoding="utf-8") as f:
            creds = json.load(f)

        username = creds.get("username")
        password = creds.get("password")
        session_id = creds.get("sessionid") or creds.get("session_id")
        if session_id:
            import urllib.parse
            session_id = urllib.parse.unquote(str(session_id))
        session_file = os.path.join(base_dir, "ig_session.json")

        cl = Client()
        cl.delay_range = [2, 5]
        print(f"[AUTH] Connecting to Instagram as @{username}...")

        logged_in = False
        if os.path.exists(session_file):
            try:
                cl.load_settings(session_file)
                if session_id:
                    cl.login_by_sessionid(session_id)
                else:
                    cl.login(username, password)
                logged_in = True
                print("[AUTH] Reused existing session successfully.")
            except Exception as e:
                print(f"[AUTH] Saved session expired: {e}")

        if not logged_in:
            if session_id:
                print("[AUTH] Logging in using browser session ID...")
                cl.login_by_sessionid(session_id)
                cl.dump_settings(session_file)
                print("[AUTH] Successfully authenticated via session ID!")
            else:
                try:
                    cl.login(username, password)
                    cl.dump_settings(session_file)
                    print("[AUTH] Successfully logged in and saved session.")
                except Exception as e:
                    if "out of date" in str(e).lower() or "challenge" in str(e).lower():
                        print("\n[!] Meta requires session cookie login to bypass the mobile app challenge.")
                        print("👉 To enable 1-click automatic uploads, add your 'sessionid' to instagram_credentials.json:")
                        print("   1. Open instagram.com in Chrome/Edge and log in.")
                        print("   2. Press F12 -> Application tab -> Cookies -> https://www.instagram.com")
                        print("   3. Copy the value of 'sessionid' and paste it into instagram_credentials.json as:")
                        print('      { "username": "...", "sessionid": "PASTE_HERE" }\n')
                    raise e

        print(f"[UPLOAD] Uploading Reel to Instagram ({video_path})...")
        media = cl.clip_upload(
            video_path,
            caption=caption,
            thumbnail=cover_path
        )
        print(f"[SUCCESS] 🎉 Reel published successfully! Media ID: {media.pk}")
        if hasattr(media, "code"):
            print(f"🔗 Instagram URL: https://www.instagram.com/reel/{media.code}/")
        return True
    except Exception as e:
        print(f"[!] Upload encountered an issue: {e}")
        print("💡 The video and caption are safely staged in ready_to_upload/ for 1-click mobile posting.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        v_path = sys.argv[1]
        c_text = "Check out this incredible untold story! #mythology"
        stage_reel_for_upload(v_path, c_text, "test_sample")
