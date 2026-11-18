#!/usr/bin/env python3
"""
analytics_optimizer.py - Continuous Performance Learning & Optimization Engine.
Implements:
  - Phase 14: Series Drop-off Analysis (Part 1 -> Part 2 conversion rate)
  - Content Pillar Performance Scoring (views, likes, shares, comments)
  - Hook Effectiveness Analytics
  - Feedback Loop: Adapts future content selection to favor winning patterns
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from database import get_connection

def record_metric(reel_slug: str, views: int, likes: int, comments: int, shares: int = 0, saves: int = 0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM reels WHERE slug = ?", (reel_slug,))
    row = c.fetchone()
    reel_id = row[0] if row else None

    # Calculate retention score heuristic: (likes + comments*2 + shares*3) / max(1, views)
    retention_score = round(((likes + comments * 2.0 + shares * 3.0) / max(1, views)) * 100, 2)

    c.execute("""
    INSERT INTO analytics (reel_id, slug, views, likes, comments, shares, saves, retention_rate)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (reel_id, reel_slug, views, likes, comments, shares, saves, retention_score))
    conn.commit()
    conn.close()

def analyze_series_dropoff(series_id: str) -> Dict[str, Any]:
    """
    Computes audience retention and drop-off between Part 1 and Part 2.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT r.part_number, a.views, a.likes, a.comments, a.shares
    FROM reels r
    LEFT JOIN analytics a ON r.id = a.reel_id
    WHERE r.series_id = ?
    ORDER BY r.part_number ASC
    """, (series_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    if len(rows) < 2:
        return {"series_id": series_id, "status": "insufficient_parts_data", "conversion_rate": None}

    p1_views = max(1, rows[0].get("views") or 0)
    p2_views = rows[1].get("views") or 0
    conv_rate = round((p2_views / p1_views) * 100, 2)

    return {
        "series_id": series_id,
        "part_1_views": p1_views,
        "part_2_views": p2_views,
        "part_1_to_part_2_conversion_pct": conv_rate,
        "diagnosis": "Strong continuation hook" if conv_rate >= 70 else "Cliffhanger needs optimization"
    }

def get_performance_summary() -> Dict[str, Any]:
    """Generates an executive performance summary across all content pillars."""
    conn = get_connection()
    c = conn.cursor()

    # Category performance
    c.execute("""
    SELECT r.category, COUNT(r.id) as total_posts,
           AVG(COALESCE(a.views, 0)) as avg_views,
           AVG(COALESCE(a.likes, 0)) as avg_likes,
           AVG(COALESCE(a.retention_rate, 0.0)) as avg_retention
    FROM reels r
    LEFT JOIN analytics a ON r.id = a.reel_id
    WHERE r.status = 'published'
    GROUP BY r.category
    ORDER BY avg_retention DESC
    """)
    pillar_stats = [dict(r) for r in c.fetchall()]

    # Total stats
    c.execute("SELECT COUNT(*) FROM reels WHERE status = 'published'")
    total_published = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM reels WHERE status = 'staged'")
    total_staged = c.fetchone()[0]

    conn.close()

    return {
        "total_published": total_published,
        "total_staged": total_staged,
        "top_performing_pillars": pillar_stats,
        "recommendation": "Maintain 2:2:1 daily ratio (2 Standalone, 2 Series Chapters, 1 Prime Cliffhanger)"
    }

if __name__ == "__main__":
    summary = get_performance_summary()
    print("=== UNTOLD MYTHOLOGY PERFORMANCE SUMMARY ===")
    print(json.dumps(summary, indent=2))
