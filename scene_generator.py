#!/usr/bin/env python3
"""
scene_generator.py - "Mahabharat Style" Cinematic 2D Vector Story Renderer.
Implements the exact directorial aesthetic from P2_mahabharat.md:
  - 100% UNIQUE scenes for every single beat across all 5 stories (30 dedicated scenes).
  - Mood Skies: Dusk (#2A1747->#8E3A7A->#F08A3C), Night (#0E1430->#232B5C), Divine (#3B2A7A), Battle (#5A0E12->#C4321C), Peace (Gold/Blue)
  - Volumetric god rays, floating golden dust (#E8B64A), light vignette.
  - Shadow-puppet character silhouettes with glowing gold ornaments (Kavach, Kundal, Mukut, Chakra, Bow, etc.).
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH = 1080
HEIGHT = 1920

SKIES = {
    "dusk": [(42, 23, 71), (142, 58, 122), (240, 138, 60)],      # #2A1747 -> #8E3A7A -> #F08A3C
    "night": [(14, 20, 48), (35, 43, 92), (18, 22, 50)],         # #0E1430 -> #232B5C
    "divine": [(59, 42, 122), (110, 75, 175), (235, 195, 120)],  # #3B2A7A center glow
    "battle": [(90, 14, 18), (155, 30, 25), (196, 50, 28)],      # #5A0E12 -> #C4321C
    "peace": [(35, 45, 90), (120, 140, 195), (250, 215, 130)]    # Sunrise gold & sky blue
}

GOLD = (232, 182, 74)       # #E8B64A
GOLD_BRIGHT = (255, 225, 120)
CREAM = (245, 233, 207)     # #F5E9CF
SILHOUETTE = (18, 14, 26)   # Deep rich shadow puppet silhouette
BLOOD_RED = (220, 30, 35)

def draw_3color_gradient(colors):
    """Draws a vertical 3-stop smooth gradient sky."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    c1, c2, c3 = colors
    h_half = HEIGHT // 2

    for y in range(HEIGHT):
        if y < h_half:
            ratio = y / h_half
            r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
            g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
            b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        else:
            ratio = (y - h_half) / h_half
            r = int(c2[0] * (1 - ratio) + c3[0] * ratio)
            g = int(c2[1] * (1 - ratio) + c3[1] * ratio)
            b = int(c2[2] * (1 - ratio) + c3[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img

def add_floating_golden_dust(draw, seed=101, count=45):
    """Adds soft floating golden dust particles (#E8B64A) across the scene."""
    np.random.seed(seed)
    for _ in range(count):
        x = int(np.random.randint(40, WIDTH - 40))
        y = int(np.random.randint(120, HEIGHT - 250))
        radius = int(np.random.choice([2, 3, 4]))
        alpha_color = GOLD_BRIGHT if radius == 4 else GOLD
        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=alpha_color)

def add_god_rays(draw, center=(WIDTH // 2, 600), count=9, length=650):
    """Draws radial volumetric god rays radiating from divine center."""
    cx, cy = center
    for i in range(count):
        angle = -70 + i * (140 / max(1, count - 1))
        rad = math.radians(angle)
        rad_spread = math.radians(angle + 4.5)
        x1 = cx + int(length * math.sin(rad))
        y1 = cy + int(length * math.cos(rad))
        x2 = cx + int(length * math.sin(rad_spread))
        y2 = cy + int(length * math.cos(rad_spread))
        draw.polygon([(cx, cy), (x1, y1), (x2, y2)], fill=(255, 235, 160))

# ==================== REEL 1: KARNA'S SECRET IDENTITY ====================

def render_karna_ganga_sunrise(out_path: str):
    """Karna offering morning arghya water to rising sun in holy Ganga."""
    img = draw_3color_gradient(SKIES["dusk"])
    draw = ImageDraw.Draw(img)
    # Sun
    sun_cx, sun_cy = WIDTH // 2, 900
    for r in range(220, 60, -15):
        draw.ellipse([(sun_cx - r, sun_cy - r), (sun_cx + r, sun_cy + r)], fill=(255, 175, 60))
    draw.ellipse([(sun_cx - 60, sun_cy - 60), (sun_cx + 60, sun_cy + 60)], fill=(255, 245, 180))
    # River
    draw.rectangle([(0, 1150), (WIDTH, HEIGHT)], fill=(28, 18, 42))
    for y in range(1160, HEIGHT, 35):
        draw.line([(30, y), (WIDTH - 30, y)], fill=(120, 55, 75), width=2)
    # Karna offering water
    kx, ky = WIDTH // 2, 1200
    draw.rectangle([(kx - 45, ky - 130), (kx + 45, ky + 120)], fill=SILHOUETTE)
    draw.ellipse([(kx - 30, ky - 200), (kx + 30, ky - 130)], fill=SILHOUETTE)
    draw.ellipse([(kx - 30, ky - 110), (kx + 30, ky - 30)], fill=GOLD, outline=GOLD_BRIGHT, width=3)
    # Raised arms with water pouring
    draw.polygon([(kx - 40, ky - 120), (kx - 80, ky - 230), (kx - 60, ky - 230), (kx - 25, ky - 120)], fill=SILHOUETTE)
    draw.polygon([(kx + 40, ky - 120), (kx + 80, ky - 230), (kx + 60, ky - 230), (kx + 25, ky - 120)], fill=SILHOUETTE)
    # Golden water stream pouring down
    draw.line([(kx, ky - 230), (kx, ky - 90)], fill=GOLD_BRIGHT, width=5)
    add_floating_golden_dust(draw, seed=11)
    img.save(out_path, quality=95)

def render_karna_kunti_revelation(out_path: str):
    """Mother Kunti with folded hands pleading to Karna under magenta twilight."""
    img = draw_3color_gradient(SKIES["dusk"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1350), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Karna (left)
    kx, ky = 360, 1180
    draw.rectangle([(kx - 42, ky - 130), (kx + 42, ky + 100)], fill=SILHOUETTE)
    draw.rectangle([(kx - 46, ky + 100), (kx + 46, ky + 290)], fill=SILHOUETTE)
    draw.ellipse([(kx - 30, ky - 200), (kx + 30, ky - 130)], fill=SILHOUETTE)
    draw.ellipse([(kx - 30, ky - 115), (kx + 30, ky - 40)], fill=GOLD, outline=GOLD_BRIGHT, width=3)
    # Kunti (right)
    qx, qy = 720, 1200
    draw.rectangle([(qx - 38, qy - 110), (qx + 38, qy + 90)], fill=SILHOUETTE)
    draw.rectangle([(qx - 45, qy + 90), (qx + 45, qy + 270)], fill=SILHOUETTE)
    draw.ellipse([(qx - 28, qy - 180), (qx + 28, qy - 110)], fill=SILHOUETTE)
    draw.arc([(qx - 40, qy - 205), (qx + 40, qy - 100)], start=160, end=380, fill=GOLD, width=4)
    # Folded Hands
    draw.line([(qx - 40, qy - 60), (qx - 75, qy - 40)], fill=SILHOUETTE, width=10)
    add_floating_golden_dust(draw, seed=12)
    img.save(out_path, quality=95)

def render_karna_hastinapur_throne(out_path: str):
    """Grand golden throne room of Hastinapur with pillars and royal chandelier."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    # Palace Pillars
    for px in [120, 320, 760, 960]:
        draw.rectangle([(px - 35, 300), (px + 35, 1450)], fill=SILHOUETTE)
        draw.polygon([(px - 55, 300), (px + 55, 300), (px, 240)], fill=GOLD)
    # Floor
    draw.rectangle([(0, 1400), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Golden Throne in Center
    tx, ty = WIDTH // 2, 1250
    draw.polygon([(tx - 120, ty + 150), (tx + 120, ty + 150), (tx + 100, ty - 80), (tx - 100, ty - 80)], fill=GOLD)
    draw.polygon([(tx - 60, ty - 80), (tx + 60, ty - 80), (tx, ty - 180)], fill=GOLD_BRIGHT)
    # Golden Crown hovering above throne
    draw.polygon([(tx - 40, ty - 220), (tx + 40, ty - 220), (tx, ty - 280)], fill=GOLD_BRIGHT)
    add_floating_golden_dust(draw, seed=13)
    img.save(out_path, quality=95)

def render_karna_duryodhan_friendship(out_path: str):
    """Duryodhan and Karna clasping hands in eternal brotherhood against battle sunset."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Two warrior silhouettes facing each other clasping hands
    wx1, wy = 420, 1180
    wx2 = 660
    # Left warrior (Duryodhan with Crown)
    draw.rectangle([(wx1 - 45, wy - 120), (wx1 + 45, wy + 110)], fill=SILHOUETTE)
    draw.rectangle([(wx1 - 50, wy + 110), (wx1 + 50, wy + 280)], fill=SILHOUETTE)
    draw.ellipse([(wx1 - 30, wy - 190), (wx1 + 30, wy - 120)], fill=SILHOUETTE)
    draw.polygon([(wx1 - 25, wy - 185), (wx1, wy - 245), (wx1 + 25, wy - 185)], fill=GOLD)
    # Right warrior (Karna with glowing Kavach)
    draw.rectangle([(wx2 - 45, wy - 120), (wx2 + 45, wy + 110)], fill=SILHOUETTE)
    draw.rectangle([(wx2 - 50, wy + 110), (wx2 + 50, wy + 280)], fill=SILHOUETTE)
    draw.ellipse([(wx2 - 30, wy - 190), (wx2 + 30, wy - 120)], fill=SILHOUETTE)
    draw.ellipse([(wx2 - 25, wy - 110), (wx2 + 25, wy - 40)], fill=GOLD, outline=GOLD_BRIGHT, width=3)
    # Clasping arms meeting in the center with golden energy spark
    draw.line([(wx1 + 35, wy - 40), (wx2 - 35, wy - 40)], fill=GOLD_BRIGHT, width=12)
    draw.ellipse([(530, wy - 55), (550, wy - 25)], fill=(255, 255, 220))
    add_floating_golden_dust(draw, seed=14)
    img.save(out_path, quality=95)

def render_karna_vow_kunti(out_path: str):
    """Karna granting the sacred vow to Kunti under star-lit violet sky."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # River shoreline
    draw.line([(0, 1350), (WIDTH, 1350)], fill=GOLD, width=3)
    # Karna extending right hand in blessing
    kx, ky = 400, 1190
    draw.rectangle([(kx - 40, ky - 120), (kx + 40, ky + 100)], fill=SILHOUETTE)
    draw.rectangle([(kx - 45, ky + 100), (kx + 45, ky + 280)], fill=SILHOUETTE)
    draw.ellipse([(kx - 28, ky - 190), (kx + 28, ky - 120)], fill=SILHOUETTE)
    draw.ellipse([(kx - 25, ky - 110), (kx + 25, ky - 40)], fill=GOLD)
    draw.line([(kx + 30, ky - 60), (kx + 110, ky - 80)], fill=SILHOUETTE, width=12) # Extended blessing arm
    # Hand emitting golden rays of vachan
    for ang in range(-45, 50, 20):
        rad = math.radians(ang)
        draw.line([(kx + 110, ky - 80), (kx + 110 + int(60*math.cos(rad)), ky - 80 + int(60*math.sin(rad)))], fill=GOLD_BRIGHT, width=3)
    # Kunti bowing low in gratitude
    qx, qy = 700, 1260
    draw.rectangle([(qx - 40, qy - 80), (qx + 40, qy + 100)], fill=SILHOUETTE)
    draw.ellipse([(qx - 25, qy - 140), (qx + 25, qy - 80)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=15)
    img.save(out_path, quality=95)

def render_karna_daanveer_kavach(out_path: str):
    """Karna's golden armor radiating cosmic light from his chest."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 750
    # Giant radial god rays from glowing Kavach
    add_god_rays(draw, center=(cx, cy), count=13, length=750)
    # Grand Kavach-Kundal floating in celestial glory
    draw.ellipse([(cx - 160, cy - 160), (cx + 160, cy + 160)], outline=GOLD_BRIGHT, width=8)
    draw.ellipse([(cx - 110, cy - 110), (cx + 110, cy + 110)], fill=GOLD, outline=GOLD_BRIGHT, width=4)
    # Central Sun Motif on Armor
    draw.ellipse([(cx - 45, cy - 45), (cx + 45, cy + 45)], fill=(255, 245, 180))
    # Two Golden Kundals beside the armor
    draw.ellipse([(cx - 240, cy - 60), (cx - 180, cy)], fill=GOLD_BRIGHT)
    draw.ellipse([(cx + 180, cy - 60), (cx + 240, cy)], fill=GOLD_BRIGHT)
    # Ground silhouette
    draw.rectangle([(0, 1450), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=16, count=60)
    img.save(out_path, quality=95)

# ==================== REEL 2: ABHIMANYU'S CHAKRAVYUH ====================

def render_chakravyuh_drona_formation(out_path: str):
    """The massive 7-tier circular Chakravyuh maze formation drawn by Drona."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 850
    # 7 concentric spinning rings
    for idx, r in enumerate(range(480, 110, -55)):
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=GOLD if idx % 2 == 0 else (150, 25, 20), width=4)
    # Dronacharya on chariot overlooking the maze
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    dx, dy = WIDTH // 2, 1220
    draw.rectangle([(dx - 45, dy - 120), (dx + 45, dy + 110)], fill=SILHOUETTE)
    draw.ellipse([(dx - 30, dy - 190), (dx + 30, dy - 120)], fill=SILHOUETTE)
    draw.line([(dx, dy - 180), (dx, dy - 240)], fill=GOLD, width=4) # Guru staff
    add_floating_golden_dust(draw, seed=21)
    img.save(out_path, quality=95)

def render_arjun_lured_away(out_path: str):
    """Arjun and Krishna's chariot lured away into distant dust horizon by Samsaptakas."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    # Distant dusty horizon
    draw.rectangle([(0, 1200), (WIDTH, HEIGHT)], fill=(45, 15, 20))
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Small distant chariot disappearing into sunset
    cx, cy = 680, 1150
    draw.ellipse([(cx - 70, cy - 25), (cx + 70, cy + 25)], fill=SILHOUETTE)
    draw.line([(cx - 70, cy), (cx - 150, cy)], fill=SILHOUETTE, width=6) # Chariot pole
    draw.polygon([(cx + 20, cy - 80), (cx + 50, cy - 30), (cx - 10, cy - 30)], fill=GOLD) # Hanuman flag fluttering
    # Dust cloud behind chariot
    draw.ellipse([(cx - 200, cy - 60), (cx - 80, cy + 30)], fill=(120, 40, 30))
    add_floating_golden_dust(draw, seed=22)
    img.save(out_path, quality=95)

def render_abhimanyu_entry_chariot(out_path: str):
    """Young Abhimanyu in glowing silver-gold chariot crashing through the 1st gate."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1350), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Shattered wooden barricades flying
    for bx, by in [(220, 1150), (320, 1050), (180, 950)]:
        draw.polygon([(bx, by), (bx + 80, by + 20), (bx + 60, by + 70)], fill=(80, 40, 20))
    # Abhimanyu's heroic chariot charging forward
    ax, ay = 620, 1180
    draw.rectangle([(ax - 50, ay - 110), (ax + 50, ay + 90)], fill=SILHOUETTE)
    draw.ellipse([(ax - 28, ay - 175), (ax + 28, ay - 110)], fill=SILHOUETTE)
    draw.polygon([(ax - 24, ay - 170), (ax, ay - 225), (ax + 24, ay - 170)], fill=GOLD_BRIGHT)
    # Drawn golden bow
    draw.arc([(ax - 20, ay - 240), (ax + 160, ay + 60)], start=270, end=90, fill=GOLD, width=6)
    add_floating_golden_dust(draw, seed=23)
    img.save(out_path, quality=95)

def render_subhadra_asleep_revelation(out_path: str):
    """Queen Subhadra falling asleep on royal couch while pregnant with Abhimanyu."""
    img = draw_3color_gradient(SKIES["night"])
    draw = ImageDraw.Draw(img)
    # Palace arches
    draw.rectangle([(100, 300), (980, 1400)], fill=(20, 25, 60))
    draw.arc([(100, 200), (980, 600)], start=180, end=360, fill=GOLD, width=5)
    # Subhadra resting peacefully
    sx, sy = WIDTH // 2, 1100
    draw.ellipse([(sx - 150, sy - 50), (sx + 150, sy + 70)], fill=SILHOUETTE)
    draw.ellipse([(sx - 120, sy - 90), (sx - 60, sy - 30)], fill=SILHOUETTE) # Head resting on cushion
    # Golden glow on her womb (unborn Abhimanyu listening)
    draw.ellipse([(sx - 10, sy - 30), (sx + 70, sy + 50)], fill=GOLD, outline=GOLD_BRIGHT, width=3)
    add_floating_golden_dust(draw, seed=24)
    img.save(out_path, quality=95)

def render_abhimanyu_chariot_wheel_fight(out_path: str):
    """Abhimanyu holding the heavy wooden chariot wheel high defending against all arrows."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    ax, ay = WIDTH // 2, 1180
    # Young hero silhouette
    draw.rectangle([(ax - 38, ay - 110), (ax + 38, ay + 90)], fill=SILHOUETTE)
    draw.rectangle([(ax - 42, ay + 90), (ax + 42, ay + 280)], fill=SILHOUETTE)
    draw.ellipse([(ax - 26, ay - 175), (ax + 26, ay - 110)], fill=SILHOUETTE)
    draw.polygon([(ax - 22, ay - 170), (ax, ay - 220), (ax + 22, ay - 170)], fill=GOLD_BRIGHT)
    # Giant Broken Chariot Wheel held high in both hands
    wx, wy = ax - 20, ay - 160
    draw.ellipse([(wx - 120, wy - 120), (wx + 120, wy + 120)], outline=GOLD, width=8)
    for sp in range(8):
        s_rad = math.radians(sp * 45)
        draw.line([(wx, wy), (wx + int(110 * math.cos(s_rad)), wy + int(110 * math.sin(s_rad)))], fill=GOLD, width=4)
    # Host of enemy arrows splintering against the wheel
    for arr_y in [wy - 70, wy - 20, wy + 40]:
        draw.line([(wx + 220, arr_y), (wx + 125, arr_y)], fill=GOLD_BRIGHT, width=3)
    add_floating_golden_dust(draw, seed=25)
    img.save(out_path, quality=95)

def render_abhimanyu_immortal_hero(out_path: str):
    """Divine pillar of gold light receiving Abhimanyu's immortal heroic soul."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 700
    # Golden celestial light beam descending
    draw.polygon([(cx - 70, 0), (cx + 70, 0), (cx + 180, HEIGHT), (cx - 180, HEIGHT)], fill=(255, 235, 170))
    add_god_rays(draw, center=(cx, cy), count=11, length=700)
    # Heroic warrior silhouette ascending
    draw.ellipse([(cx - 30, cy - 120), (cx + 30, cy - 60)], fill=GOLD_BRIGHT)
    draw.polygon([(cx - 40, cy - 60), (cx + 40, cy - 60), (cx, cy + 80)], fill=GOLD)
    add_floating_golden_dust(draw, seed=26, count=65)
    img.save(out_path, quality=95)

# ==================== REEL 3: WHY KRISHNA BROKE HIS VOW ====================

def render_krishna_vow_charioteer(out_path: str):
    """Lord Krishna sitting calmly holding the reins of 4 white horses, serene vow."""
    img = draw_3color_gradient(SKIES["peace"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Chariot seat
    kx, ky = 480, 1160
    draw.rectangle([(kx - 45, ky - 120), (kx + 45, ky + 100)], fill=(30, 45, 95))
    draw.rectangle([(kx - 50, ky + 100), (kx + 50, ky + 290)], fill=GOLD)
    draw.ellipse([(kx - 30, ky - 190), (kx + 30, ky - 120)], fill=(35, 55, 115))
    draw.polygon([(kx - 25, ky - 185), (kx, ky - 250), (kx + 25, ky - 185)], fill=GOLD_BRIGHT) # Mor Mukut
    draw.ellipse([(kx - 6, ky - 265), (kx + 6, ky - 245)], fill=(20, 180, 160)) # Feather
    # Reins in hand
    for hy in [ky + 10, ky + 30, ky + 50, ky + 70]:
        draw.line([(kx + 35, ky - 20), (kx + 220, hy)], fill=GOLD, width=3)
    add_floating_golden_dust(draw, seed=31)
    img.save(out_path, quality=95)

def render_bheeshma_fierce_vow(out_path: str):
    """Bheeshma Pitamah standing tall on his chariot making his fierce battlefield vow."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    bx, by = WIDTH // 2, 1150
    draw.rectangle([(bx - 50, by - 140), (bx + 50, by + 120)], fill=SILHOUETTE)
    draw.rectangle([(bx - 55, by + 120), (bx + 55, by + 320)], fill=SILHOUETTE)
    draw.ellipse([(bx - 32, by - 210), (bx + 32, by - 140)], fill=SILHOUETTE)
    draw.polygon([(bx - 30, by - 205), (bx, by - 275), (bx + 30, by - 205)], fill=GOLD) # Mukut
    # Long flowing white beard
    draw.polygon([(bx - 15, by - 150), (bx + 15, by - 150), (bx, by - 80)], fill=CREAM)
    # Massive golden bow drawn taut
    draw.arc([(bx - 80, by - 280), (bx + 160, by + 180)], start=270, end=90, fill=GOLD_BRIGHT, width=8)
    add_floating_golden_dust(draw, seed=32)
    img.save(out_path, quality=95)

def render_arjun_chariot_pierced(out_path: str):
    """Arjun fallen to his knees on his arrow-pierced chariot, Gandiv slipping."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1350), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Chariot body riddled with arrows
    draw.rectangle([(280, 1150), (820, 1380)], fill=(60, 20, 25))
    for ax, ay in [(340, 1100), (450, 1080), (600, 1120), (740, 1090)]:
        draw.line([(ax + 80, ay - 60), (ax, ay)], fill=GOLD, width=4)
    # Arjun kneeling in despair
    jx, jy = 520, 1220
    draw.rectangle([(jx - 35, jy - 80), (jx + 35, jy + 60)], fill=SILHOUETTE)
    draw.ellipse([(jx - 25, jy - 140), (jx + 25, jy - 80)], fill=SILHOUETTE)
    # Dropped Gandiv Bow on floor
    draw.arc([(jx - 120, jy + 50), (jx + 20, jy + 140)], start=180, end=360, fill=GOLD, width=5)
    add_floating_golden_dust(draw, seed=33)
    img.save(out_path, quality=95)

def render_krishna_leaping_rage(out_path: str):
    """Lord Krishna leaping from the chariot with righteous anger, Pitambara flying."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    # Cosmic aura explosion
    cx, cy = WIDTH // 2, 750
    for r in range(320, 80, -25):
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(190, 45, 25))
    add_god_rays(draw, center=(cx, cy), count=11, length=650)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Leaping Krishna Silhouette in mid-air
    kx, ky = 520, 1100
    draw.rectangle([(kx - 45, ky - 120), (kx + 45, ky + 100)], fill=(30, 45, 95))
    draw.ellipse([(kx - 30, ky - 190), (kx + 30, ky - 120)], fill=(35, 55, 115))
    draw.polygon([(kx - 25, ky - 185), (kx, ky - 255), (kx + 25, ky - 185)], fill=GOLD_BRIGHT)
    # Flowing yellow Pitambara silk flying behind him
    draw.polygon([(kx - 45, ky - 30), (kx - 220, ky - 110), (kx - 160, ky + 80), (kx - 45, ky + 50)], fill=GOLD)
    add_floating_golden_dust(draw, seed=34)
    img.save(out_path, quality=95)

def render_krishna_wheel_sudarshana(out_path: str):
    """Krishna brandishing the shattered chariot wheel like the flaming Sudarshana Chakra."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 700
    add_god_rays(draw, center=(cx, cy), count=13, length=700)
    # The Flaming Chariot Wheel Sudarshana
    draw.ellipse([(cx - 150, cy - 150), (cx + 150, cy + 150)], outline=GOLD_BRIGHT, width=10)
    draw.ellipse([(cx - 100, cy - 100), (cx + 100, cy + 100)], fill=GOLD, outline=GOLD_BRIGHT, width=5)
    for sp in range(12):
        s_rad = math.radians(sp * 30)
        draw.line([(cx, cy), (cx + int(90*math.cos(s_rad)), cy + int(90*math.sin(s_rad)))], fill=(90, 20, 25), width=4)
    # Krishna holding it overhead
    kx, ky = cx, 1150
    draw.rectangle([(kx - 45, ky - 120), (kx + 45, ky + 110)], fill=(30, 45, 95))
    draw.rectangle([(kx - 50, ky + 110), (kx + 50, ky + 310)], fill=GOLD)
    draw.line([(kx - 30, ky - 80), (cx - 40, cy + 120)], fill=(30, 45, 95), width=16)
    draw.line([(kx + 30, ky - 80), (cx + 40, cy + 120)], fill=(30, 45, 95), width=16)
    draw.rectangle([(0, 1420), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=35, count=60)
    img.save(out_path, quality=95)

def render_bheeshma_devotion_surrender(out_path: str):
    """Bheeshma Pitamah dropping his bow with folded hands, tears of sublime devotion."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Bheeshma bowing on knees with hands folded
    bx, by = WIDTH // 2, 1200
    draw.rectangle([(bx - 45, by - 90), (bx + 45, by + 90)], fill=SILHOUETTE)
    draw.ellipse([(bx - 28, by - 160), (bx + 28, by - 90)], fill=SILHOUETTE)
    draw.polygon([(bx - 25, by - 155), (bx, by - 215), (bx + 25, by - 155)], fill=GOLD)
    # Folded hands raised upwards to heaven
    draw.line([(bx, by - 40), (bx, by - 110)], fill=SILHOUETTE, width=12)
    # Soft divine light falling upon him
    draw.polygon([(bx - 120, 0), (bx + 120, 0), (bx + 60, by - 160), (bx - 60, by - 160)], fill=(255, 235, 180))
    add_floating_golden_dust(draw, seed=36)
    img.save(out_path, quality=95)

# ==================== REEL 4: ASHWATTHAMA'S IMMORTAL CURSE ====================

def render_ashwatthama_dark_forest(out_path: str):
    """Midnight misty jungle with towering ancient trees and wandering shadow."""
    img = draw_3color_gradient(SKIES["night"])
    draw = ImageDraw.Draw(img)
    # Giant white moon
    moon_cx, moon_cy = 780, 360
    draw.ellipse([(moon_cx - 80, moon_cy - 80), (moon_cx + 80, moon_cy + 80)], fill=(245, 248, 255))
    # Dense forest silhouettes
    for tx in [100, 260, 480, 880, 1020]:
        draw.rectangle([(tx - 25, 600), (tx + 25, 1420)], fill=SILHOUETTE)
        draw.ellipse([(tx - 120, 400), (tx + 120, 850)], fill=SILHOUETTE)
    draw.rectangle([(0, 1400), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Wandering tall shadow
    ax, ay = 360, 1220
    draw.rectangle([(ax - 35, ay - 130), (ax + 35, ay + 110)], fill=SILHOUETTE)
    draw.ellipse([(ax - 26, ay - 195), (ax + 26, ay - 130)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=41, count=25)
    img.save(out_path, quality=95)

def render_ashwatthama_divine_mani(out_path: str):
    """Close silhouette showing the glowing divine ruby/emerald gem on forehead."""
    img = draw_3color_gradient(SKIES["night"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 850
    # Head Silhouette
    draw.ellipse([(cx - 140, cy - 180), (cx + 140, cy + 180)], fill=SILHOUETTE)
    # Long matted warrior locks
    draw.polygon([(cx - 140, cy), (cx - 240, cy + 280), (cx - 80, cy + 240)], fill=SILHOUETTE)
    draw.polygon([(cx + 140, cy), (cx + 240, cy + 280), (cx + 80, cy + 240)], fill=SILHOUETTE)
    # Glowing Divine Mani on Forehead (radiant crimson & emerald light rays)
    mx, my = cx, cy - 80
    for r in range(90, 20, -10):
        draw.ellipse([(mx - r, my - r), (mx + r, my + r)], fill=(220, 40, 50))
    draw.ellipse([(mx - 20, my - 20), (mx + 20, my + 20)], fill=(255, 230, 120))
    add_floating_golden_dust(draw, seed=42)
    img.save(out_path, quality=95)

def render_brahmashirsha_astra_fire(out_path: str):
    """Blazing apocalyptic celestial orb of the Brahmashirsha Astra illuminating sky."""
    img = draw_3color_gradient(SKIES["battle"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 700
    # Massive crackling celestial fireball
    for r in range(320, 80, -25):
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(240, 70, 25))
    draw.ellipse([(cx - 80, cy - 80), (cx + 80, cy + 80)], fill=(255, 245, 180))
    add_god_rays(draw, center=(cx, cy), count=13, length=700)
    # Earth cracking underneath
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    for lx in range(80, WIDTH, 120):
        draw.line([(lx, 1380), (lx + 40, HEIGHT)], fill=(255, 120, 40), width=4)
    add_floating_golden_dust(draw, seed=43)
    img.save(out_path, quality=95)

def render_krishna_curses_ashwatthama(out_path: str):
    """Lord Krishna towering in cosmic blue light extracting the gem and pronouncing curse."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Towering Lord Krishna (left)
    kx, ky = 380, 1100
    draw.rectangle([(kx - 50, ky - 150), (kx + 50, ky + 130)], fill=(30, 45, 95))
    draw.rectangle([(kx - 55, ky + 130), (kx + 55, ky + 340)], fill=GOLD)
    draw.ellipse([(kx - 35, ky - 230), (kx + 35, ky - 150)], fill=(35, 55, 115))
    draw.polygon([(kx - 30, ky - 225), (kx, ky - 295), (kx + 30, ky - 225)], fill=GOLD_BRIGHT)
    # Divine arm outstretched taking the jewel
    draw.line([(kx + 45, ky - 80), (kx + 160, ky - 110)], fill=(30, 45, 95), width=16)
    # Ashwatthama kneeling in agony (right)
    ax, ay = 680, 1220
    draw.rectangle([(ax - 40, ay - 90), (ax + 40, ay + 90)], fill=SILHOUETTE)
    draw.ellipse([(ax - 28, ay - 160), (ax + 28, ay - 90)], fill=SILHOUETTE)
    # Blood dripping from forehead
    draw.ellipse([(ax - 8, ay - 145), (ax + 8, ay - 130)], fill=BLOOD_RED)
    add_floating_golden_dust(draw, seed=44)
    img.save(out_path, quality=95)

def render_asirgarh_shiva_lingam(out_path: str):
    """Ancient Shivalingam inside ruined Asirgarh temple with fresh red rose offering at dawn."""
    img = draw_3color_gradient(SKIES["peace"])
    draw = ImageDraw.Draw(img)
    # Ancient stone temple arches
    draw.rectangle([(120, 650), (220, 1420)], fill=SILHOUETTE)
    draw.rectangle([(860, 650), (960, 1420)], fill=SILHOUETTE)
    draw.arc([(120, 450), (960, 950)], start=180, end=360, fill=SILHOUETTE, width=40)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Sacred Stone Shivalingam on Yoni pedestal in center
    sx, sy = WIDTH // 2, 1260
    draw.rectangle([(sx - 70, sy), (sx + 70, sy + 70)], fill=(35, 40, 55))
    draw.ellipse([(sx - 45, sy - 90), (sx + 45, sy + 10)], fill=(25, 30, 45))
    # Sacred Tripundra Tilak (3 white lines)
    for ly in [sy - 50, sy - 42, sy - 34]:
        draw.line([(sx - 20, ly), (sx + 20, ly)], fill=CREAM, width=2)
    # Fresh Red Rose offering on top of the Lingam
    draw.ellipse([(sx - 12, sy - 95), (sx + 12, sy - 75)], fill=(225, 30, 45))
    add_floating_golden_dust(draw, seed=45, count=30)
    img.save(out_path, quality=95)

def render_ashwatthama_lone_silhouette(out_path: str):
    """Tall mysterious lone figure walking into morning fog towards the horizon."""
    img = draw_3color_gradient(SKIES["night"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Lone tall wanderer walking away
    ax, ay = WIDTH // 2, 1200
    draw.rectangle([(ax - 38, ay - 140), (ax + 38, ay + 110)], fill=SILHOUETTE)
    draw.rectangle([(ax - 44, ay + 110), (ax + 44, ay + 310)], fill=SILHOUETTE)
    draw.ellipse([(ax - 28, ay - 210), (ax + 28, ay - 140)], fill=SILHOUETTE)
    # Glowing faint red wound on forehead
    draw.ellipse([(ax - 6, ay - 195), (ax + 6, ay - 180)], fill=(255, 30, 40))
    # Soft morning mist across bottom
    for my in range(1280, HEIGHT, 25):
        draw.line([(40, my), (WIDTH - 40, my)], fill=(45, 55, 80), width=6)
    add_floating_golden_dust(draw, seed=46, count=25)
    img.save(out_path, quality=95)

# ==================== REEL 5: EKLAVYA'S GURU DAKSHINA ====================

def render_eklavya_forest_archer(out_path: str):
    """Eklavya practicing archery alone under lush jungle canopy."""
    img = draw_3color_gradient(SKIES["peace"])
    draw = ImageDraw.Draw(img)
    # Forest canopy
    draw.ellipse([(0, 350), (450, 850)], fill=SILHOUETTE)
    draw.ellipse([(630, 320), (1080, 820)], fill=SILHOUETTE)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Eklavya drawing large bow
    ex, ey = 380, 1200
    draw.rectangle([(ex - 40, ey - 120), (ex + 40, ey + 90)], fill=SILHOUETTE)
    draw.rectangle([(ex - 44, ey + 90), (ex + 44, ey + 280)], fill=SILHOUETTE)
    draw.ellipse([(ex - 28, ey - 190), (ex + 28, ey - 120)], fill=SILHOUETTE)
    # Golden Arc Bow
    draw.arc([(ex - 20, ey - 280), (ex + 220, ey + 180)], start=270, end=90, fill=GOLD, width=6)
    # Glowing Arrow
    draw.line([(ex + 20, ey - 50), (ex + 350, ey - 50)], fill=GOLD_BRIGHT, width=4)
    add_floating_golden_dust(draw, seed=51)
    img.save(out_path, quality=95)

def render_eklavya_clay_drona_idol(out_path: str):
    """Eklavya bowing before the sculpted mud idol of Guru Dronacharya."""
    img = draw_3color_gradient(SKIES["peace"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Sculpted mud statue of Drona on raised altar
    dx, dy = 740, 1160
    draw.rectangle([(dx - 55, dy - 60), (dx + 55, dy + 200)], fill=(90, 75, 60))
    draw.ellipse([(dx - 35, dy - 140), (dx + 35, dy - 60)], fill=(90, 75, 60))
    draw.line([(dx, dy - 125), (dx, dy - 90)], fill=GOLD, width=4) # Tilak
    # Eklavya prostrating before the statue
    ex, ey = 360, 1280
    draw.rectangle([(ex - 50, ey - 40), (ex + 50, ey + 40)], fill=SILHOUETTE)
    draw.ellipse([(ex + 40, ey - 35), (ex + 85, ey + 15)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=52)
    img.save(out_path, quality=95)

def render_eklavya_arrow_dog_mouth(out_path: str):
    """The dog silenced with 7 golden arrows locking its mouth without a drop of blood."""
    img = draw_3color_gradient(SKIES["dusk"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1380), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Dog silhouette standing astonished
    dx, dy = WIDTH // 2, 1240
    draw.ellipse([(dx - 80, dy - 40), (dx + 80, dy + 40)], fill=SILHOUETTE)
    draw.ellipse([(dx - 120, dy - 80), (dx - 60, dy - 20)], fill=SILHOUETTE) # Head
    draw.polygon([(dx - 110, dy - 110), (dx - 80, dy - 70), (dx - 125, dy - 70)], fill=SILHOUETTE) # Ear
    # 7 Arrows criss-crossing inside open mouth
    for ay in range(dy - 70, dy - 35, 6):
        draw.line([(dx - 170, ay - 10), (dx - 50, ay + 10)], fill=GOLD_BRIGHT, width=3)
    add_floating_golden_dust(draw, seed=53)
    img.save(out_path, quality=95)

def render_drona_demanding_dakshina(out_path: str):
    """Guru Dronacharya with arm outstretched pointing demandingly at Eklavya's thumb."""
    img = draw_3color_gradient(SKIES["dusk"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Guru Dronacharya standing strict (left)
    dx, dy = 380, 1160
    draw.rectangle([(dx - 45, dy - 130), (dx + 45, dy + 110)], fill=SILHOUETTE)
    draw.rectangle([(dx - 50, dy + 110), (dx + 50, dy + 290)], fill=SILHOUETTE)
    draw.ellipse([(dx - 30, dy - 200), (dx + 30, dy - 130)], fill=SILHOUETTE)
    # Outstretched arm pointing right
    draw.line([(dx + 35, dy - 70), (dx + 160, dy - 70)], fill=SILHOUETTE, width=14)
    # Eklavya (right) looking with calm devotion
    ex, ey = 720, 1180
    draw.rectangle([(ex - 40, ey - 120), (ex + 40, ey + 100)], fill=SILHOUETTE)
    draw.rectangle([(ex - 44, ey + 100), (ex + 44, ey + 270)], fill=SILHOUETTE)
    draw.ellipse([(ex - 28, ey - 190), (ex + 28, ey - 120)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=54)
    img.save(out_path, quality=95)

def render_eklavya_severing_thumb(out_path: str):
    """Eklavya serenely slicing his right thumb with a hunting knife, golden sacrifice."""
    img = draw_3color_gradient(SKIES["divine"])
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, 850
    # Center focus: Hand and Knife
    draw.rectangle([(cx - 70, cy), (cx + 70, cy + 220)], fill=SILHOUETTE)
    draw.ellipse([(cx - 70, cy - 40), (cx + 70, cy + 40)], fill=SILHOUETTE)
    # Glowing severed thumb floating in golden aura
    tx, ty = cx - 100, cy - 80
    draw.ellipse([(tx - 25, ty - 35), (tx + 25, ty + 35)], fill=GOLD_BRIGHT, outline=(255, 245, 180), width=4)
    # Drops of sacred offering blood & golden dust
    for by in [cy - 30, cy + 10, cy + 50]:
        draw.ellipse([(tx - 6, by), (tx + 6, by + 12)], fill=BLOOD_RED)
    # God rays celebrating the supreme sacrifice
    add_god_rays(draw, center=(cx, cy - 80), count=11, length=600)
    draw.rectangle([(0, 1420), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    add_floating_golden_dust(draw, seed=55, count=55)
    img.save(out_path, quality=95)

def render_eklavya_eternal_legend(out_path: str):
    """Eklavya firing arrows using index and middle finger, immortal legend."""
    img = draw_3color_gradient(SKIES["peace"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 1360), (WIDTH, HEIGHT)], fill=SILHOUETTE)
    # Eklavya shooting straight into the golden dawn sky
    ex, ey = WIDTH // 2, 1180
    draw.rectangle([(ex - 42, ey - 130), (ex + 42, ey + 100)], fill=SILHOUETTE)
    draw.rectangle([(ex - 46, ey + 100), (ex + 46, ey + 300)], fill=SILHOUETTE)
    draw.ellipse([(ex - 30, ey - 200), (ex + 30, ey - 130)], fill=SILHOUETTE)
    # Aiming high into heaven
    draw.arc([(ex - 40, ey - 320), (ex + 240, ey + 100)], start=260, end=90, fill=GOLD, width=7)
    draw.line([(ex, ey - 90), (ex + 220, ey - 250)], fill=GOLD_BRIGHT, width=5)
    add_god_rays(draw, center=(ex + 220, ey - 250), count=9, length=500)
    add_floating_golden_dust(draw, seed=56, count=45)
    img.save(out_path, quality=95)

# ----------------- REGISTRY & DISPATCHER -----------------

SCENE_RENDERERS = {
    # Reel 1
    "karna_ganga_sunrise": render_karna_ganga_sunrise,
    "karna_kunti_revelation": render_karna_kunti_revelation,
    "karna_hastinapur_throne": render_karna_hastinapur_throne,
    "karna_duryodhan_friendship": render_karna_duryodhan_friendship,
    "karna_vow_kunti": render_karna_vow_kunti,
    "karna_daanveer_kavach": render_karna_daanveer_kavach,

    # Reel 2
    "chakravyuh_drona_formation": render_chakravyuh_drona_formation,
    "arjun_lured_away": render_arjun_lured_away,
    "abhimanyu_entry_chariot": render_abhimanyu_entry_chariot,
    "subhadra_asleep_revelation": render_subhadra_asleep_revelation,
    "abhimanyu_chariot_wheel_fight": render_abhimanyu_chariot_wheel_fight,
    "abhimanyu_immortal_hero": render_abhimanyu_immortal_hero,

    # Reel 3
    "krishna_vow_charioteer": render_krishna_vow_charioteer,
    "bheeshma_fierce_vow": render_bheeshma_fierce_vow,
    "arjun_chariot_pierced": render_arjun_chariot_pierced,
    "krishna_leaping_rage": render_krishna_leaping_rage,
    "krishna_wheel_sudarshana": render_krishna_wheel_sudarshana,
    "bheeshma_devotion_surrender": render_bheeshma_devotion_surrender,

    # Reel 4
    "ashwatthama_dark_forest": render_ashwatthama_dark_forest,
    "ashwatthama_divine_mani": render_ashwatthama_divine_mani,
    "brahmashirsha_astra_fire": render_brahmashirsha_astra_fire,
    "krishna_curses_ashwatthama": render_krishna_curses_ashwatthama,
    "asirgarh_shiva_lingam": render_asirgarh_shiva_lingam,
    "ashwatthama_lone_silhouette": render_ashwatthama_lone_silhouette,

    # Reel 5
    "eklavya_forest_archer": render_eklavya_forest_archer,
    "eklavya_clay_drona_idol": render_eklavya_clay_drona_idol,
    "eklavya_arrow_dog_mouth": render_eklavya_arrow_dog_mouth,
    "drona_demanding_dakshina": render_drona_demanding_dakshina,
    "eklavya_severing_thumb": render_eklavya_severing_thumb,
    "eklavya_eternal_legend": render_eklavya_eternal_legend,
}

def get_scene_image(scene_name: str, assets_dir: str) -> str:
    """Returns local path to scene image, rendering if missing."""
    os.makedirs(assets_dir, exist_ok=True)
    out_file = os.path.join(assets_dir, f"{scene_name}.jpg")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
        return out_file

    renderer = SCENE_RENDERERS.get(scene_name.lower())
    if renderer:
        renderer(out_file)
    else:
        # Dynamic procedural synthesis for any new Hindu mythology scene
        try:
            from dynamic_scenes import synthesize_dynamic_scene
            synthesize_dynamic_scene(scene_name, out_file)
        except Exception as e:
            print(f"[!] Dynamic scene synthesis notice: {e}, falling back to sunrise")
            render_karna_ganga_sunrise(out_file)

    return out_file

if __name__ == "__main__":
    test_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "test_scenes")
    print(f"Generating all {len(SCENE_RENDERERS)} distinct Mahabharat scenes...")
    for s_name in SCENE_RENDERERS.keys():
        f = get_scene_image(s_name, test_d)
        print("  Created:", s_name)
    print("All scenes generated successfully!")
