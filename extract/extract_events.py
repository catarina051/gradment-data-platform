#!/usr/bin/env python3
"""
extract_events.py
-----------------
Telemetry Events Extractor for GradMent Data Platform (Phase 4).

Supports:
  - Synthetic Lane (synthetic seed dataset) and Real Lane (read-only MySQL analytics_ro connection).
  - Watermark-based incremental extraction by default.
  - `--full-refresh` CLI flag for complete backfill re-processing (FR-3).
  - Dynamic PostgreSQL monthly range partition creation before ingestion.
  - Idempotent insertion (`ON CONFLICT DO NOTHING`).
"""

import sys
import os
import argparse
import json
import psycopg2
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from extract.watermark import get_last_watermark, update_watermark, reset_watermark
from extract.partition_manager import ensure_partitions_for_timestamps

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

MYSQL_HOST = os.getenv('MYSQL_HOST', '172.20.0.20')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'analytics_ro')
MYSQL_PASS = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DATABASE', 'gradment')

SEEDS_PATH = os.path.join(PROJECT_ROOT, 'dbt_project', 'seeds', 'synthetic_events_seed.json')

def parse_utc_dt(ts_val):
    if isinstance(ts_val, datetime):
        return ts_val.astimezone(timezone.utc)
    ts_str = str(ts_val).replace('Z', '+00:00')
    return datetime.fromisoformat(ts_str).astimezone(timezone.utc)

def ensure_staging_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id VARCHAR(36) PRIMARY KEY,
                event_name VARCHAR(64) NOT NULL,
                category VARCHAR(32) NOT NULL,
                priority VARCHAR(16) NOT NULL,
                schema_version VARCHAR(16) NOT NULL,
                session_id VARCHAR(36) NOT NULL,
                user_id BIGINT NOT NULL,
                platform VARCHAR(32) NOT NULL,
                app_version VARCHAR(32) NOT NULL,
                screen_name VARCHAR(64),
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
    conn.commit()

def run_extraction(source='synthetic', full_refresh=False, limit=None):
    print(f"\n======================================================================")
    print(f"Starting Telemetry Event Extraction | Source: {source.upper()} | Full Refresh: {full_refresh} | Limit: {limit}")
    print(f"======================================================================")

    start_time = datetime.now(timezone.utc)
    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    ensure_staging_schema(conn)

    watermark_key = f"events_{source}"

    if full_refresh:
        reset_watermark(conn, watermark_key)
        watermark_ts = '1970-01-01T00:00:00+00:00'
    else:
        watermark_ts = get_last_watermark(conn, watermark_key)

    watermark_dt = parse_utc_dt(watermark_ts)
    print(f"[EXTRACT] Reading events logged strictly after watermark UTC: {watermark_dt.isoformat()}")

    extracted_events = []
    if source == 'synthetic':
        if not os.path.exists(SEEDS_PATH):
            print(f"[WARN] Seed file missing at {SEEDS_PATH}. Generating seeds on the fly...")
            from scripts.synthetic.generate_seeds import generate_events
            generate_events(days=30)

        with open(SEEDS_PATH, 'r', encoding='utf-8') as f:
            all_seeds = json.load(f)

        for ev in all_seeds:
            ev_dt = parse_utc_dt(ev['event_ts'])
            if full_refresh or ev_dt > watermark_dt:
                extracted_events.append(ev)
                if limit and len(extracted_events) >= limit:
                    break
    else:
        print(f"[EXTRACT] Real Lane mode: Connecting to MySQL ({MYSQL_HOST}:{MYSQL_PORT}) as '{MYSQL_USER}'...")
        import pymysql
        my_conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with my_conn.cursor() as my_cur:
                query = """
                    SELECT event_id, event_name, schema_version, user_id, session_id,
                           event_ts, platform, app_version, payload
                    FROM analytics_events
                    WHERE event_ts > %s
                    ORDER BY event_ts ASC
                """
                if limit:
                    query += f" LIMIT {int(limit)}"
                
                my_cur.execute(query, (watermark_dt.strftime('%Y-%m-%d %H:%M:%S'),))
                rows = my_cur.fetchall()
                for r in rows:
                    p_val = r['payload']
                    if isinstance(p_val, str):
                        try:
                            p_json = json.loads(p_val)
                        except Exception:
                            p_json = {}
                    elif isinstance(p_val, dict):
                        p_json = p_val
                    else:
                        p_json = {}

                    extracted_events.append({
                        'event_id': r['event_id'],
                        'event_name': r['event_name'],
                        'category': 'General',
                        'priority': 'Normal',
                        'schema_version': str(r['schema_version']),
                        'session_id': r['session_id'],
                        'user_id': r['user_id'] or 0,
                        'platform': r['platform'] or 'web',
                        'app_version': r['app_version'] or '1.0.0',
                        'screen_name': None,
                        'event_ts': r['event_ts'].isoformat() if isinstance(r['event_ts'], datetime) else str(r['event_ts']),
                        'payload_json': json.dumps(p_json)
                    })
        finally:
            my_conn.close()

    print(f"[EXTRACT] Extracted {len(extracted_events)} candidate events for loading.")

    if not extracted_events:
        print("[EXTRACT] No new events to load.")
        conn.close()
        return 0

    # Ensure dynamic monthly range partitions exist on PostgreSQL fct_events for target event dates
    timestamps = [ev['event_ts'] for ev in extracted_events]
    ensure_partitions_for_timestamps(conn, timestamps)

    # Insert into staging analytics_events table with idempotency
    inserted_count = 0
    max_dt = watermark_dt

    with conn.cursor() as cur:
        for ev in extracted_events:
            cur.execute("""
                INSERT INTO analytics_events (
                    id, event_name, category, priority, schema_version,
                    session_id, user_id, platform, app_version, screen_name,
                    timestamp, payload, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO NOTHING;
            """, (
                ev['event_id'], ev['event_name'], ev['category'], ev['priority'],
                ev['schema_version'], ev['session_id'], ev['user_id'], ev['platform'],
                ev['app_version'], ev['screen_name'], ev['event_ts'], ev['payload_json']
            ))
            if cur.rowcount > 0:
                inserted_count += 1
            ev_dt = parse_utc_dt(ev['event_ts'])
            if ev_dt > max_dt:
                max_dt = ev_dt

    conn.commit()
    if max_dt > watermark_dt:
        update_watermark(conn, watermark_key, max_dt.isoformat())

    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    from extract.audit import log_pipeline_run
    log_pipeline_run(
        conn=conn,
        dag_id='extract_transform_synthetic' if source == 'synthetic' else 'extract_transform_real',
        lane=source,
        start_dt=start_time,
        end_dt=end_time,
        rows_extracted=len(extracted_events),
        rows_loaded=inserted_count,
        status='SUCCESS'
    )

    print(f"[SUCCESS] Extraction completed in {duration:.2f}s!")
    print(f"  Rows Extracted: {len(extracted_events)} | Rows Inserted: {inserted_count} | New Watermark: {max_dt.isoformat()}")

    conn.close()
    return inserted_count

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GradMent Telemetry Event Extractor")
    parser.add_argument('--source', choices=['synthetic', 'real'], default='synthetic', help="Data source lane")
    parser.add_argument('--full-refresh', action='store_true', help="Bypass watermark and force full backfill extraction (FR-3)")
    parser.add_argument('--limit', type=int, default=None, help="Limit number of extracted rows for controlled testing")
    args = parser.parse_args()

    run_extraction(source=args.source, full_refresh=args.full_refresh, limit=args.limit)

