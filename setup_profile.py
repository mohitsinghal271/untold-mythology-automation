#!/usr/bin/env python3
"""
setup_profile.py - Configures the Instagram account profile for Untold Mythology.
Updates:
  1. Profile Picture (Golden Sudarshana Chakra Emblem)
  2. Full Name / Display Name ("Untold Mythology | Legends")
  3. Biography (High-converting, viral storytelling bio adhering to ig-profile rubric)
  4. Generates high-res mobile Wallpapers for followers/stories.
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path
from instagrapi import Client

BASE_DIR = Path(__file__).resolve().parent
CREDS_FILE = BASE_DIR / "instagram_credentials.json"
SESSION_CACHE = BASE_DIR / "ig_session.json"
PFP_PATH = BASE_DIR / "assets" / "profile_pic.jpg"

NAME_FIELD = "Untold Mythology | Legends"
BIO_TEXT = (
    "Deep secrets of Indian Mythology & Mahabharat 🏹\n"
    "Cinematic untold stories & ancient legends.\n"
    "Daily Hindi deep-dives.\n"
    "👇 Tap Follow for daily wisdom"
)

def update_instagram_profile():
    if not CREDS_FILE.exists():
        print("[!] instagram_credentials.json not found!")
        return False

    with open(CREDS_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)

    session_id = creds.get("sessionid")
    if not session_id:
        print("[!] No sessionid found in credentials!")
        return False

    session_id = urllib.parse.unquote(str(session_id))
    username = creds.get("username", "untold_mythology_legends")

    cl = Client()
    cl.delay_range = [2, 4]

    print(f"[AUTH] Connecting to Instagram as @{username} via session ID...")
    if SESSION_CACHE.exists():
        try:
            cl.load_settings(SESSION_CACHE)
        except Exception:
            pass

    try:
        cl.login_by_sessionid(session_id)
        cl.dump_settings(SESSION_CACHE)
        print(f"[AUTH] Authenticated successfully as User ID: {cl.user_id}")
    except Exception as e:
        print(f"[!] Authentication failed: {e}")
        return False

    # 1. Update Profile Picture
    if PFP_PATH.exists():
        print(f"\n[1/3] Uploading profile picture from {PFP_PATH.name}...")
        try:
            cl.account_change_picture(PFP_PATH)
            print("[SUCCESS] Profile picture updated successfully!")
        except Exception as e:
            print(f"[!] Could not update profile picture: {e}")
    else:
        print(f"[!] Profile picture file not found at: {PFP_PATH}")

    # 2. Update Biography
    print("\n[2/3] Setting Biography...")
    print(f"Bio Content:\n{BIO_TEXT}")
    try:
        cl.account_set_biography(BIO_TEXT)
        print("[SUCCESS] Biography set successfully!")
    except Exception as e:
        print(f"[!] Could not set biography via account_set_biography: {e}")

    # 3. Update Name
    print(f"\n[3/3] Setting Name field to '{NAME_FIELD}'...")
    try:
        cl.account_edit(full_name=NAME_FIELD)
        print("[SUCCESS] Name updated successfully!")
    except Exception as e:
        print(f"[!] Could not update name via account_edit: {e}")

    # Verify updated info
    print("\n" + "=" * 50)
    print("VERIFYING LIVE INSTAGRAM PROFILE:")
    try:
        user_info = cl.user_info(int(cl.user_id))
        print(f"  - Username: @{user_info.username}")
        print(f"  - Full Name: {user_info.full_name}")
        print(f"  - Biography:\n{user_info.biography}")
        print(f"  - Profile Picture URL: {user_info.profile_pic_url[:60]}...")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"[!] Could not fetch updated user info: {e}")
        return False

if __name__ == "__main__":
    update_instagram_profile()
