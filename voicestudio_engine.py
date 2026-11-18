"""
voicestudio_engine.py - VoiceStudio (OmniVoice GGUF) Integration for Indian Mythology Reels.
Synthesizes natural, rich, human-sounding Hindi narration with zero robotic artifacts.
"""

import os
import sys
import shutil
import subprocess
import time

VOICESTUDIO_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Programs\VoiceStudio")
OMNIVOICE_BIN = os.path.join(VOICESTUDIO_DIR, "resources", "bin", "omnivoice-tts-windows-x86_64.exe")

# Model paths
MODELS_DIR = os.path.abspath(r"c:\Users\idea\OneDrive\Desktop\projects\VoiceStudio\models")
BASE_MODEL = os.path.join(MODELS_DIR, "omnivoice-base-Q4_K_M.gguf")
TOKENIZER_MODEL = os.path.join(MODELS_DIR, "omnivoice-tokenizer-Q4_K_M.gguf")

DEFAULT_INSTRUCT = {
    "Hindi": "male, low pitch, middle-aged, indian accent",
    "Hinglish": "male, low pitch, middle-aged, indian accent",
    "English": "male, low pitch, middle-aged, indian accent"
}

def get_ffmpeg_binary() -> str:
    bin_path = shutil.which("ffmpeg")
    if bin_path:
        return bin_path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def is_voicestudio_available() -> bool:
    """Check if VoiceStudio binary and GGUF models are ready."""
    return (
        os.path.exists(OMNIVOICE_BIN)
        and os.path.exists(BASE_MODEL)
        and os.path.exists(TOKENIZER_MODEL)
        and os.path.getsize(BASE_MODEL) > 300_000_000
        and os.path.getsize(TOKENIZER_MODEL) > 200_000_000
    )

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
VS_TEMP_AUDIO_DIR = os.path.join(WORKSPACE_DIR, "temp_vs_audio")

def synthesize_with_voicestudio(
    text: str,
    output_path: str,
    language: str = "Hindi",
    instruct: str | None = None,
    steps: int = 5
) -> bool:
    """
    Synthesizes speech using VoiceStudio's OmniVoice engine.
    Produces rich, natural, human-sounding speech from Hindi Devanagari text.
    """
    if not is_voicestudio_available():
        raise RuntimeError("VoiceStudio engine or models are not ready.")

    os.makedirs(VS_TEMP_AUDIO_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Use safe workspace directory for omnivoice output to prevent permission blocks
    unique_tag = f"vs_{int(time.time()*1000)}"
    temp_wav = os.path.join(VS_TEMP_AUDIO_DIR, f"{unique_tag}.wav")
    needs_mp3_conversion = output_path.lower().endswith(".mp3")

    cmd = [
        OMNIVOICE_BIN,
        "--model", BASE_MODEL,
        "--codec", TOKENIZER_MODEL,
        "--steps", str(steps),
        "--clamp-fp16",
        "-o", temp_wav,
        "--lang", "Hindi"
    ]

    instruction = instruct or DEFAULT_INSTRUCT.get(language, DEFAULT_INSTRUCT["Hindi"])
    cmd.extend(["--instruct", instruction])

    clean_text = text.strip()
    if not clean_text:
        return False

    print(f"[*] VoiceStudio synthesizing: {clean_text[:50]}... ({len(clean_text)} chars)")
    t0 = time.time()

    sub_env = os.environ.copy()
    sub_env["GGML_BACKEND"] = "CPU"
    sub_env["OMNIVOICE_GGUF_BACKEND"] = "cpu"

    result = subprocess.run(
        cmd,
        input=clean_text.encode("utf-8"),
        cwd=VS_TEMP_AUDIO_DIR,
        env=sub_env,
        capture_output=True,
        timeout=300
    )

    if result.returncode != 0:
        err = result.stderr.decode('utf-8', errors='replace')
        print(f"[!] VoiceStudio error: {err[-400:]}")
        return False

    elapsed = time.time() - t0
    print(f"[*] VoiceStudio generated in {elapsed:.1f}s")

    if needs_mp3_conversion:
        ffmpeg_bin = get_ffmpeg_binary()
        convert_cmd = [
            ffmpeg_bin, "-y",
            "-i", temp_wav,
            "-af", "loudnorm=I=-18.0:TP=-1.5:LRA=11",
            "-b:a", "192k",
            "-ar", "44100",
            output_path
        ]
        subprocess.run(convert_cmd, capture_output=True)
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass
    else:
        shutil.copy2(temp_wav, output_path)
        try:
            os.remove(temp_wav)
        except Exception:
            pass

    return os.path.exists(output_path) and os.path.getsize(output_path) > 1000

if __name__ == "__main__":
    test_out = r"D:\instagram-automation\temp\vs_test_hindi.mp3"
    ok = synthesize_with_voicestudio("मौत के बाद, सब सोचते हैं कि रावण सिर्फ एक असुर राजा था।", test_out)
    print("VoiceStudio test success:", ok)
