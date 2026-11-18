#!/usr/bin/env python3
"""
sfx_generator.py - Procedural Cinematic Sound Effects Generator for Indian Mythology Reels.
Synthesizes:
  1. Divine Sub-Bass Reveal Boom (deep 40-70Hz resonant hit)
  2. Temple Bell Chime (harmonically tuned ancient bronze bell)
  3. Conch Blast / War Horn (resonant ceremonial horn)
  4. Ambient Drone / Tanpura Bed (calm mystical backdrop)
  5. Arrow Whoosh / Release (high-speed swift air slice)
All synthesized in pure numpy, saved to WAV/MP3 without external audio dependencies.
"""

import os
import math
import wave
import struct
import numpy as np
import imageio_ffmpeg
import subprocess

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
SAMPLE_RATE = 44100

def write_wav(filename: str, audio: np.ndarray, sample_rate: int = SAMPLE_RATE):
    """Writes a 16-bit mono WAV file from a float numpy array in [-1.0, 1.0]."""
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    audio = np.clip(audio, -1.0, 1.0)
    int_data = (audio * 32767).astype(np.int16)
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_data.tobytes())

def generate_divine_boom(filename: str, duration: float = 2.5):
    """Deep cinematic sub-bass impact with decaying rumble."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Pitch envelope: slides from 85Hz down to 35Hz
    freq = 35.0 + 50.0 * np.exp(-t * 3.5)
    phase = 2.0 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    # Sub bass wave + subtle 2nd harmonic
    sub = np.sin(phase) + 0.3 * np.sin(phase * 2.0)
    # Exponential decay
    envelope = np.exp(-t * 2.2)
    # Soft noise transient at impact (first 0.08s)
    noise = np.random.uniform(-0.15, 0.15, len(t)) * np.exp(-t * 30.0)
    audio = (sub * envelope) + noise
    write_wav(filename, audio)

def generate_temple_bell(filename: str, duration: float = 3.0):
    """Resonant bronze temple bell with rich bell harmonics (ghanti)."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Bell partial frequencies (fundamental + inharmonics typical of bronze bells)
    partials = [(520.0, 1.0, 1.2), (1045.0, 0.6, 2.0), (1560.0, 0.4, 3.2), (2180.0, 0.25, 4.5), (3120.0, 0.15, 6.0)]
    audio = np.zeros_like(t)
    for freq, amp, decay in partials:
        audio += amp * np.sin(2.0 * np.pi * freq * t) * np.exp(-t * decay)
    audio = audio / np.max(np.abs(audio) + 1e-6) * 0.8
    write_wav(filename, audio)

def generate_conch_blast(filename: str, duration: float = 2.8):
    """Sacred Shankh / Conch blast: warm horn swell with slight vibrato."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Fundamental around 210Hz (G#3) with gentle rise and vibrato
    vibrato = 1.0 + 0.015 * np.sin(2.0 * np.pi * 5.0 * t)
    pitch_bend = 195.0 + 20.0 * (1.0 - np.exp(-t * 2.0))
    freq = pitch_bend * vibrato
    phase = 2.0 * np.pi * np.cumsum(freq) / SAMPLE_RATE

    # Rich harmonic spectrum of a shell horn
    horn = (
        1.0 * np.sin(phase) +
        0.7 * np.sin(phase * 2.0) +
        0.5 * np.sin(phase * 3.0) +
        0.3 * np.sin(phase * 4.0) +
        0.15 * np.sin(phase * 5.0)
    )
    # Attack swell (0.4s) -> sustain -> gentle release
    attack = np.clip(t / 0.45, 0.0, 1.0)
    release = np.clip((duration - t) / 0.7, 0.0, 1.0)
    envelope = attack * release
    audio = (horn * envelope) * 0.75
    write_wav(filename, audio)

def generate_ambient_drone(filename: str, duration: float = 65.0):
    """Mystical ambient Indian drone: soft tanpura root (C#) + atmospheric fifth."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    f_root = 138.59  # C#3
    f_fifth = 207.65 # G#3
    f_octave = 277.18

    drone = (
        0.5 * np.sin(2 * np.pi * f_root * t) +
        0.3 * np.sin(2 * np.pi * f_fifth * t + 0.4) +
        0.2 * np.sin(2 * np.pi * f_octave * t + 0.8) +
        0.08 * np.sin(2 * np.pi * (f_root / 2.0) * t)
    )
    # Slow natural swell
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.15 * t)
    audio = drone * lfo * 0.22 # Kept low so voiceover sits proudly on top
    write_wav(filename, audio)

def build_sfx_library(assets_dir: str) -> dict:
    """Pre-generates and caches all sound effects in assets_dir."""
    os.makedirs(assets_dir, exist_ok=True)
    library = {
        "conch": os.path.join(assets_dir, "sfx_conch.wav"),
        "boom": os.path.join(assets_dir, "sfx_boom.wav"),
        "bell": os.path.join(assets_dir, "sfx_bell.wav"),
        "drone": os.path.join(assets_dir, "amb_drone.wav")
    }

    if not os.path.exists(library["conch"]):
        generate_conch_blast(library["conch"], duration=3.0)
    if not os.path.exists(library["boom"]):
        generate_divine_boom(library["boom"], duration=2.5)
    if not os.path.exists(library["bell"]):
        generate_temple_bell(library["bell"], duration=3.2)
    if not os.path.exists(library["drone"]):
        generate_ambient_drone(library["drone"], duration=80.0)

    return library

if __name__ == "__main__":
    test_d = r"D:\instagram-automation\temp\sfx_test"
    lib = build_sfx_library(test_d)
    print("Generated sound library:", lib)
