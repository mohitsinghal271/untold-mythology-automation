#!/usr/bin/env python3
"""
database.py - SQLite Persistence Layer for Untold Mythology Studio.
Tracks reels, multi-part series, content deduplication, and performance analytics.
"""

import os
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mythology_studio.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all necessary tables for the studio."""
    conn = get_connection()
    c = conn.cursor()

    # Table 1: Reels Queue & History
    c.execute("""
    CREATE TABLE IF NOT EXISTS reels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        series_id TEXT,
        part_number INTEGER DEFAULT 1,
        total_parts INTEGER DEFAULT 1,
        title TEXT NOT NULL,
        top_hook TEXT NOT NULL,
        top_hook_hindi TEXT,
        category TEXT NOT NULL,
        status TEXT DEFAULT 'staged', -- 'staged', 'scheduled', 'published', 'failed'
        video_path TEXT,
        caption TEXT,
        cover_path TEXT,
        scheduled_time TEXT,
        published_time TEXT,
        instagram_media_id TEXT,
        instagram_url TEXT,
        error_message TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table 2: Serialized Story Tracking (Phase 14)
    c.execute("""
    CREATE TABLE IF NOT EXISTS series (
        series_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        total_parts INTEGER NOT NULL,
        current_part INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active', -- 'active', 'completed'
        character_bible TEXT,
        visual_palette TEXT,
        previous_summary TEXT,
        next_outline TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table 3: Strict Content Deduplication Memory
    c.execute("""
    CREATE TABLE IF NOT EXISTS content_memory (
        content_hash TEXT PRIMARY KEY,
        topic_text TEXT NOT NULL,
        hook_text TEXT NOT NULL,
        category TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table 4: Performance Analytics & Continuous Optimization
    c.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reel_id INTEGER,
        slug TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        saves INTEGER DEFAULT 0,
        retention_rate REAL DEFAULT 0.0,
        part_conversion_rate REAL DEFAULT 0.0,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reel_id) REFERENCES reels(id)
    );
    """)

    # Table 5: Publishing Schedule Slots
    c.execute("""
    CREATE TABLE IF NOT EXISTS schedule_slots (
        slot_id INTEGER PRIMARY KEY,
        slot_name TEXT,
        ist_time TEXT, -- '08:00', '11:00', '14:00', '18:00', '21:00'
        target_category TEXT,
        is_active INTEGER DEFAULT 1
    );
    """)

    # Populate default IST slots if empty
    c.execute("SELECT COUNT(*) FROM schedule_slots;")
    if c.fetchone()[0] == 0:
        default_slots = [
            (1, "Morning Devotion & Boons", "08:00", "divine_power", 1),
            (2, "Series Chapter (Midday)", "11:00", "series_ongoing", 1),
            (3, "Untold Characters & Comparisons", "14:00", "character_deepdive", 1),
            (4, "Ancient Mysteries & Curses", "18:00", "mysteries_curses", 1),
            (5, "Prime-time Series Cliffhanger", "21:00", "series_cliffhanger", 1),
        ]
        c.executemany("INSERT INTO schedule_slots VALUES (?, ?, ?, ?, ?);", default_slots)

    conn.commit()
    conn.close()

# Deduplication Helpers
def compute_hash(topic: str, hook: str) -> str:
    norm = (topic.strip().lower() + ":" + hook.strip().lower()).encode("utf-8")
    return hashlib.sha256(norm).hexdigest()

def is_content_duplicate(topic: str, hook: str) -> bool:
    h = compute_hash(topic, hook)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM content_memory WHERE content_hash = ?", (h,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def record_content_hash(topic: str, hook: str, category: str):
    h = compute_hash(topic, hook)
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO content_memory (content_hash, topic_text, hook_text, category) VALUES (?, ?, ?, ?)",
              (h, topic, hook, category))
    conn.commit()
    conn.close()

# Reel Record Management
def upsert_reel(data: Dict[str, Any]) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO reels (
        slug, series_id, part_number, total_parts, title, top_hook, top_hook_hindi,
        category, status, video_path, caption, cover_path, scheduled_time, published_time
    ) VALUES (
        :slug, :series_id, :part_number, :total_parts, :title, :top_hook, :top_hook_hindi,
        :category, :status, :video_path, :caption, :cover_path, :scheduled_time, :published_time
    )
    ON CONFLICT(slug) DO UPDATE SET
        video_path = excluded.video_path,
        caption = excluded.caption,
        cover_path = excluded.cover_path,
        status = excluded.status,
        updated_at = CURRENT_TIMESTAMP;
    """, data)
    reel_id = c.lastrowid
    conn.commit()
    conn.close()
    return reel_id

def get_staged_reels(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reels WHERE status IN ('staged', 'scheduled') ORDER BY id ASC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def mark_reel_published(slug: str, media_id: str, url: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE reels SET
        status = 'published',
        instagram_media_id = ?,
        instagram_url = ?,
        published_time = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE slug = ?
    """, (media_id, url, slug))
    conn.commit()
    conn.close()

def mark_reel_failed(slug: str, error: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE reels SET
        status = 'failed',
        error_message = ?,
        retry_count = retry_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE slug = ?
    """, (error, slug))
    conn.commit()
    conn.close()

# Series Management (Phase 14)
def get_active_series() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE status = 'active' ORDER BY updated_at ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def create_or_update_series(series_data: Dict[str, Any]):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO series (
        series_id, title, category, total_parts, current_part, status,
        character_bible, visual_palette, previous_summary, next_outline
    ) VALUES (
        :series_id, :title, :category, :total_parts, :current_part, :status,
        :character_bible, :visual_palette, :previous_summary, :next_outline
    )
    ON CONFLICT(series_id) DO UPDATE SET
        current_part = excluded.current_part,
        status = excluded.status,
        previous_summary = excluded.previous_summary,
        next_outline = excluded.next_outline,
        updated_at = CURRENT_TIMESTAMP;
    """, series_data)
    conn.commit()
    conn.close()

# Initialize upon module load
init_db()
