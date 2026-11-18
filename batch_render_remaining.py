#!/usr/bin/env python3
"""
batch_render_remaining.py - Produces all 4 remaining Mahabharat reels:
  - abhimanyu_chakravyuh
  - krishna_vow
  - ashwatthama_curse
  - eklavya_thumb
"""

import sys
import os

from pipeline import produce_mythology_reel

stories = [
    "abhimanyu_chakravyuh",
    "krishna_vow",
    "ashwatthama_curse",
    "eklavya_thumb"
]

for s in stories:
    print(f"\n==================== STARTING: {s.upper()} ====================")
    try:
        produce_mythology_reel(topic_key=s, engine="voicestudio", direct_upload=False)
        print(f"==================== FINISHED: {s.upper()} ====================\n")
    except Exception as e:
        print(f"[!] Error producing {s}: {e}")
        import traceback
        traceback.print_exc()

print("ALL REMAINING REELS RENDERED!")
