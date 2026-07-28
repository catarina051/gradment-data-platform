#!/usr/bin/env python3
"""
watermark.py
------------
Watermark State Management for GradMent Data Platform (Phase 4).

Manages high-watermark timestamps in the target warehouse database (`extract_watermarks` table),
enabling incremental extraction by default and support for watermark resets.
"""

import sys
import os
import psycopg2

def ensure_watermark_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS extract_watermarks (
                source_name VARCHAR(64) PRIMARY KEY,
                last_extracted_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
    conn.commit()

def get_last_watermark(conn, source_name: str) -> str:
    ensure_watermark_table(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT last_extracted_at FROM extract_watermarks WHERE source_name = %s;", (source_name,))
        row = cur.fetchone()
        if row and row[0]:
            return row[0].isoformat() if hasattr(row[0], 'isoformat') else str(row[0])
    return '1970-01-01T00:00:00+00:00'

def update_watermark(conn, source_name: str, timestamp_str: str):
    ensure_watermark_table(conn)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO extract_watermarks (source_name, last_extracted_at, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (source_name)
            DO UPDATE SET last_extracted_at = EXCLUDED.last_extracted_at, updated_at = NOW();
        """, (source_name, timestamp_str))
    conn.commit()

def reset_watermark(conn, source_name: str):
    ensure_watermark_table(conn)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM extract_watermarks WHERE source_name = %s;", (source_name,))
    conn.commit()
    print(f"[WATERMARK] Reset watermark for source '{source_name}'.")
