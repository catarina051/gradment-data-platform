#!/usr/bin/env python3
"""
audit.py
--------
Pipeline Audit Log Helper for GradMent Data Platform (Phase 4).

Logs pipeline runs to `fct_pipeline_runs` table with accurate start_time,
end_time, duration_seconds (end_time - start_time), rows_extracted, rows_loaded, and status.
"""

import uuid
from datetime import datetime, timezone
import psycopg2

def ensure_audit_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fct_pipeline_runs (
                run_sk BIGINT PRIMARY KEY,
                run_id VARCHAR(36) NOT NULL UNIQUE,
                dag_id VARCHAR(64) NOT NULL,
                lane VARCHAR(32) NOT NULL DEFAULT 'synthetic',
                start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                end_time TIMESTAMP WITH TIME ZONE NOT NULL,
                duration_seconds NUMERIC(10, 2) NOT NULL,
                rows_extracted INT NOT NULL DEFAULT 0,
                rows_loaded INT NOT NULL DEFAULT 0,
                status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
                error_message TEXT
            );
        """)
    conn.commit()

def log_pipeline_run(conn, dag_id: str, lane: str, start_dt: datetime, end_dt: datetime, rows_extracted: int, rows_loaded: int, status: str = 'SUCCESS', error_msg: str = None):
    ensure_audit_table(conn)
    duration_seconds = round((end_dt - start_dt).total_seconds(), 2)
    run_uuid = str(uuid.uuid4())
    run_sk = abs(hash(run_uuid)) % (10**12)

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO fct_pipeline_runs (
                run_sk, run_id, dag_id, lane, start_time, end_time, duration_seconds,
                rows_extracted, rows_loaded, status, error_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            run_sk, run_uuid, dag_id, lane, start_dt, end_dt,
            duration_seconds, rows_extracted, rows_loaded, status, error_msg
        ))
    conn.commit()
    print(f"[AUDIT LOG] Logged pipeline run '{run_uuid}': Start={start_dt.isoformat()}, End={end_dt.isoformat()}, Duration={duration_seconds}s, Extracted={rows_extracted}, Loaded={rows_loaded}, Status={status}")
    return run_uuid
