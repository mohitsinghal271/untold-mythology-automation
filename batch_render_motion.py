#!/usr/bin/env python3
"""
batch_render_motion.py - Quickly assembles the remaining 4 reels with smooth Ken Burns motion clips.
Since all VoiceStudio audio beats are already cached in temp, this only renders the video and stages packages.
"""

from pipeline import produce_mythology_reel

stories = [
    "abhimanyu_chakravyuh",
    "krishna_vow",
    "ashwatthama_curse",
    "eklavya_thumb"
]

for s in stories:
    print(f"\n==================== RENDERING KEN BURNS: {s.upper()} ====================")
    produce_mythology_reel(topic_key=s, engine="voicestudio", direct_upload=False)
    print(f"==================== FINISHED: {s.upper()} ====================\n")

print("ALL 4 REELS ASSEMBLED WITH SMOOTH KEN BURNS MOTION!")
