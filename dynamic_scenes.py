#!/usr/bin/env python3
"""
dynamic_scenes.py - Procedural 2D Silhouette Scene Synthesizer.
Generates infinite unique Hindu mythology scenes based on directorial keywords:
  - Skies: Dusk, Night, Divine, Battle, Peace
  - Settings: Battlefield, Ocean, Kailash, Forest, Chariot, Temple, Cosmic
  - Silhouettes: Shiva, Krishna, Barbareek, Arjun, Karna, Hanuman, Sage, Sacred Om, Gita
  - Atmospherics: God rays, golden dust particles, glowing weapons, soft vignette
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH = 1080
HEIGHT = 1920

GOLD = (232, 182, 74)       # #E8B64A
GOLD_BRIGHT = (255, 230, 130)
GOLD_AURA = (255, 240, 180)
SILHOUETTE = (18, 14, 26)   # Deep rich shadow puppet silhouette
NEON_BLUE = (80, 180, 255)
BLOOD_RED = (200, 35, 30)

SKIES = {
    "dusk": [(42, 23, 71), (142, 58, 122), (240, 138, 60)],
    "night": [(14, 20, 48), (35, 43, 92), (18, 22, 50)],
    "divine": [(59, 42, 122), (110, 75, 175), (235, 195, 120)],
    "battle": [(90, 14, 18), (155, 30, 25), (196, 50, 28)],
    "peace": [(35, 45, 90), (120, 140, 195), (250, 215, 130)]
}

def draw_gradient_sky(sky_type="dusk"):
    colors = SKIES.get(sky_type.lower(), SKIES["dusk"])
    c1, c2, c3 = colors
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    h_half = HEIGHT // 2
    for y in range(HEIGHT):
        if y < h_half:
            r = y / h_half
            c = (int(c1[0]*(1-r) + c2[0]*r), int(c1[1]*(1-r) + c2[1]*r), int(c1[2]*(1-r) + c2[2]*r))
        else:
            r = (y - h_half) / h_half
            c = (int(c2[0]*(1-r) + c3[0]*r), int(c2[1]*(1-r) + c3[1]*r), int(c2[2]*(1-r) + c3[2]*r))
        draw.line([(0, y), (WIDTH, y)], fill=c)
    return img

def add_god_rays(draw, center=(WIDTH//2, 600), count=11, length=700, color=(255, 235, 160)):
    cx, cy = center
    for i in range(count):
        angle = -75 + i * (150 / max(1, count - 1))
        r1 = math.radians(angle)
        r2 = math.radians(angle + 4.0)
        p1 = (cx + int(length * math.sin(r1)), cy + int(length * math.cos(r1)))
        p2 = (cx + int(length * math.sin(r2)), cy + int(length * math.cos(r2)))
        draw.polygon([(cx, cy), p1, p2], fill=color)

def add_floating_dust(draw, count=50, seed=42):
    np.random.seed(seed)
    for _ in range(count):
        x = int(np.random.randint(30, WIDTH - 30))
        y = int(np.random.randint(100, HEIGHT - 200))
        rad = int(np.random.choice([2, 3, 4]))
        col = GOLD_BRIGHT if rad == 4 else GOLD
        draw.ellipse([(x - rad, y - rad), (x + rad, y + rad)], fill=col)

def draw_temple_shrine(draw, cx=WIDTH//2, ground_y=1600):
    # Sacred temple shikhar silhouette
    shikhar = [(cx, ground_y - 700), (cx - 160, ground_y - 250), (cx + 160, ground_y - 250)]
    draw.polygon(shikhar, fill=SILHOUETTE)
    draw.rectangle([(cx - 220, ground_y - 250), (cx + 220, ground_y)], fill=SILHOUETTE)
    # Kalash & flag on top
    draw.ellipse([(cx - 20, ground_y - 730), (cx + 20, ground_y - 690)], fill=GOLD)
    draw.polygon([(cx, ground_y - 730), (cx + 70, ground_y - 755), (cx, ground_y - 780)], fill=GOLD)

def draw_archer_silhouette(draw, cx=WIDTH//2, ground_y=1600, holding_bow=True):
    # Head & Mukut
    draw.ellipse([(cx - 45, ground_y - 620), (cx + 45, ground_y - 530)], fill=SILHOUETTE)
    # Golden Mukut
    draw.polygon([(cx - 35, ground_y - 610), (cx, ground_y - 670), (cx + 35, ground_y - 610)], fill=GOLD)
    # Torso
    draw.polygon([(cx - 70, ground_y - 530), (cx + 70, ground_y - 530),
                  (cx + 45, ground_y - 320), (cx - 45, ground_y - 320)], fill=SILHOUETTE)
    # Golden Kavach highlight
    draw.ellipse([(cx - 30, ground_y - 510), (cx + 30, ground_y - 450)], fill=GOLD)
    # Lower body / Dhoti
    draw.polygon([(cx - 65, ground_y - 320), (cx + 65, ground_y - 320),
                  (cx + 85, ground_y), (cx - 85, ground_y)], fill=SILHOUETTE)
    # Bow & Arrow
    if holding_bow:
        # Grand bow
        draw.arc([(cx + 40, ground_y - 680), (cx + 260, ground_y - 280)], start=270, end=90, fill=GOLD, width=7)
        # Aiming arrow
        draw.line([(cx - 60, ground_y - 480), (cx + 240, ground_y - 480)], fill=GOLD_BRIGHT, width=5)
        draw.polygon([(cx + 240, ground_y - 480), (cx + 215, ground_y - 495), (cx + 215, ground_y - 465)], fill=GOLD_BRIGHT)

def draw_shiva_silhouette(draw, cx=WIDTH//2, ground_y=1600):
    # Meditating Lord Shiva on Tiger Skin / Rock
    # Rock base
    draw.polygon([(cx - 350, ground_y), (cx - 280, ground_y - 180),
                  (cx + 280, ground_y - 180), (cx + 350, ground_y)], fill=SILHOUETTE)
    # Crossed legs
    draw.ellipse([(cx - 240, ground_y - 280), (cx + 240, ground_y - 140)], fill=SILHOUETTE)
    # Torso
    draw.polygon([(cx - 80, ground_y - 520), (cx + 80, ground_y - 520),
                  (cx + 60, ground_y - 260), (cx - 60, ground_y - 260)], fill=SILHOUETTE)
    # Head & Jata (matted hair)
    draw.ellipse([(cx - 50, ground_y - 620), (cx + 50, ground_y - 520)], fill=SILHOUETTE)
    draw.polygon([(cx - 45, ground_y - 610), (cx, ground_y - 700), (cx + 45, ground_y - 610)], fill=SILHOUETTE)
    # Crescent Moon & Ganga
    draw.arc([(cx + 25, ground_y - 690), (cx + 65, ground_y - 650)], start=200, end=40, fill=GOLD_AURA, width=5)
    # Blue throat glow (Neelkanth)
    draw.ellipse([(cx - 20, ground_y - 540), (cx + 20, ground_y - 500)], fill=NEON_BLUE)
    # Trishul standing tall on side
    tx = cx + 220
    draw.line([(tx, ground_y - 820), (tx, ground_y)], fill=GOLD, width=7)
    draw.arc([(tx - 60, ground_y - 860), (tx + 60, ground_y - 740)], start=0, end=180, fill=GOLD, width=6)
    draw.polygon([(tx, ground_y - 880), (tx - 15, ground_y - 820), (tx + 15, ground_y - 820)], fill=GOLD)
    # Damru
    draw.polygon([(tx - 35, ground_y - 700), (tx + 35, ground_y - 700),
                  (tx + 35, ground_y - 640), (tx - 35, ground_y - 640)], fill=GOLD)

def draw_chariot_scene(draw, cx=WIDTH//2, ground_y=1600):
    # Giant multi-spoke Chariot Wheel (Kurukshetra symbol)
    wx, wy, wr = cx - 180, ground_y - 220, 180
    draw.ellipse([(wx - wr, wy - wr), (wx + wr, wy + wr)], fill=SILHOUETTE, outline=GOLD, width=12)
    draw.ellipse([(wx - 35, wy - 35), (wx + 35, wy + 35)], fill=GOLD)
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        x2 = wx + int((wr - 10) * math.cos(rad))
        y2 = wy + int((wr - 10) * math.sin(rad))
        draw.line([(wx, wy), (x2, y2)], fill=GOLD, width=5)
    # Chariot body & flag
    draw.polygon([(cx - 100, ground_y - 280), (cx + 260, ground_y - 280),
                  (cx + 220, ground_y - 80), (cx - 100, ground_y - 80)], fill=SILHOUETTE)
    # Flagpole & flying banner
    draw.line([(cx + 200, ground_y - 720), (cx + 200, ground_y - 280)], fill=GOLD, width=6)
    draw.polygon([(cx + 200, ground_y - 720), (cx + 340, ground_y - 660), (cx + 200, ground_y - 600)], fill=GOLD)

def draw_sacred_gita_shrine(draw, cx=WIDTH//2, ground_y=1600):
    # Glowing sacred Bhagavad Gita book on lotus altar
    # Lotus petals altar
    for angle in range(-60, 70, 20):
        rad = math.radians(angle)
        px = cx + int(140 * math.sin(rad))
        py = ground_y - 320 - int(50 * math.cos(rad))
        draw.ellipse([(px - 35, py - 40), (px + 35, py + 40)], fill=GOLD)
    # Open sacred granth
    draw.rectangle([(cx - 160, ground_y - 480), (cx + 160, ground_y - 380)], fill=SILHOUETTE, outline=GOLD, width=6)
    draw.line([(cx, ground_y - 480), (cx, ground_y - 380)], fill=GOLD, width=5)
    # Radiating golden wisdom aura
    draw.ellipse([(cx - 240, ground_y - 560), (cx + 240, ground_y - 300)], outline=GOLD_AURA, width=4)

def synthesize_dynamic_scene(scene_key: str, out_path: str):
    """
    Intelligently analyzes the scene key and generates a tailored, high-production
    2D vector scene adhering to the P2 Mahabharata aesthetic.
    """
    key = scene_key.lower()

    # Determine Sky Mood
    if any(w in key for w in ["battle", "arrow", "fight", "kurukshetra", "shadyantra"]):
        sky = "battle"
    elif any(w in key for w in ["night", "curse", "cave", "poison", "sleeping"]):
        sky = "night"
    elif any(w in key for w in ["divine", "krishna", "god", "avatar", "shyam", "saraswati"]):
        sky = "divine"
    elif any(w in key for w in ["peace", "om", "mandir", "shloka", "sunrise"]):
        sky = "peace"
    else:
        sky = "dusk"

    img = draw_gradient_sky(sky)
    draw = ImageDraw.Draw(img)

    # Atmospherics
    add_god_rays(draw, center=(WIDTH//2, 500), count=11, length=750)
    add_floating_dust(draw, count=45, seed=abs(hash(scene_key)) % 1000)

    # Base Ground Terrain
    ground_y = 1620
    draw.polygon([(0, ground_y), (WIDTH, ground_y - 40), (WIDTH, HEIGHT), (0, HEIGHT)], fill=SILHOUETTE)

    # Determine Silhouette Subject
    cx = WIDTH // 2
    if any(w in key for w in ["shiva", "neelkanth", "kailash", "trishul"]):
        draw_shiva_silhouette(draw, cx=cx, ground_y=ground_y)
    elif any(w in key for w in ["gita", "pustak", "shloka", "upadesh"]):
        draw_sacred_gita_shrine(draw, cx=cx, ground_y=ground_y)
    elif any(w in key for w in ["chariot", "wheel", "rath", "kurukshetra"]):
        draw_chariot_scene(draw, cx=cx, ground_y=ground_y)
    elif any(w in key for w in ["temple", "mandir", "khatu", "shrine"]):
        draw_temple_shrine(draw, cx=cx, ground_y=ground_y)
    else:
        # Default noble archer / hero silhouette (Barbareek, Karna, Arjun, etc.)
        draw_archer_silhouette(draw, cx=cx, ground_y=ground_y, holding_bow=True)

    # Soft cinematic vignette blur
    img.save(out_path, "JPEG", quality=95)
    return out_path
