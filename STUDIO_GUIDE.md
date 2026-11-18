# Indian Mythology Instagram Reels Studio 🎬🏹

An autonomous pipeline for producing viral **Indian Mythology & History Cartoon Reels** in the exact visual style of top creators (like `@THE_KNOW_BRAINER`).

Built on top of the **Instagram Agent Skill** (`Jakeschincariol/instagram-agent-skill`) with custom engines for Hindi/Hinglish voiceover, 2D vector cartoon visuals, and Instagram-compliant formatting.

---

## ✨ Features

- **26 Viral Hook Formulas**: Applies proven high-retention storytelling hooks and timed beat sheets.
- **Top Hook Gold Banner**: Classic gold serif header (`"WHO WAS RAVAN, REALLY?"`) pinned at the top.
- **Bottom Subtitle Pill**: High-contrast dark translucent pill with synced white text (`"Maut ke baad,"`).
- **Deep Storytelling Voiceover**: Natural neural narration using `hi-IN-MadhurNeural` (Edge-TTS) with sentence timestamps.
- **2D Vector Animation Aesthetic**: Warm golden temples, Sheshnaag, Vishnu in divine blue, Ravan with 10 heads, glowing energy lines.
- **Ken-Burns Motion**: Dynamic zoom & pan to keep viewer engagement high and stop the scroll.
- **Automated Caption & Hashtag Linting**: 125-character visible fold compliance + 5 high-reach hashtags.
- **Export Package**: Generates ready-to-post `.mp4` video, `caption.txt`, and `cover.jpg` in `output/ready_to_upload/<topic>/`.

---

## 🚀 Quick Start

### 1. Generate a Reel (Default: Who Was Ravan?)
```bash
python pipeline.py --topic ravan
```

### 2. Choose from Curated Topics
```bash
python pipeline.py --topic karna
python pipeline.py --topic ashwatthama
```

### 3. Direct Instagram Upload & Profile Setup
- To update your profile (Profile picture, search-optimized Name, and high-retention Bio):
```bash
python setup_profile.py
```
- Direct Reel upload via `instagrapi`:
```bash
python pipeline.py --topic ravan --upload
```

---

## 🎨 Channel Assets & Wallpapers

- **Profile Picture**: [profile_pic.jpg](file:///c:/Users/idea/OneDrive/Desktop/projects/instagram-agent-skill/assets/profile_pic.jpg) (1080x1080 Golden Sudarshana Chakra Emblem)
- **Mobile Wallpapers (1080x1920)**:
  - [sudarshana_chakra_wallpaper.jpg](file:///c:/Users/idea/OneDrive/Desktop/projects/instagram-agent-skill/assets/wallpapers/sudarshana_chakra_wallpaper.jpg)
  - [karna_sunrise_wallpaper.jpg](file:///c:/Users/idea/OneDrive/Desktop/projects/instagram-agent-skill/assets/wallpapers/karna_sunrise_wallpaper.jpg)
  - [ashwatthama_gem_wallpaper.jpg](file:///c:/Users/idea/OneDrive/Desktop/projects/instagram-agent-skill/assets/wallpapers/ashwatthama_gem_wallpaper.jpg)
  - [abhimanyu_hero_wallpaper.jpg](file:///c:/Users/idea/OneDrive/Desktop/projects/instagram-agent-skill/assets/wallpapers/abhimanyu_hero_wallpaper.jpg)

---

## 📂 Project Structure

```
instagram-agent-skill/
├── config.json                 # Channel configuration, dimensions, styles
├── mythology_scriptwriter.py   # Story scripts, hook formulas, caption linter
├── audio_engine.py             # Edge-TTS voiceover & timing engine
├── scene_generator.py          # 2D vector scene renderer
├── video_compositor.py         # MoviePy 1080x1920 9:16 compositor
├── instagram_uploader.py       # Staging package & instagrapi uploader
├── pipeline.py                 # Master orchestrator script
├── output/
│   ├── ready_to_upload/        # Final videos, captions, and covers
│   └── temp/                   # Temporary audio beats & rendered clips
└── skills/                     # The 13 Claude / Antigravity Instagram skills
```
