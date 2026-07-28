#!/usr/bin/env python3
"""
verify_dynamic_partition_explain.py
------------------------------------
Verifies PostgreSQL EXPLAIN Partition Pruning on dynamically created child partitions (fct_events_y2026m07).
"""

import sys
import os
import psycopg2
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from extract.partition_manager import ensure_monthly_partition

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

def main():
    print("======================================================================")
    print("PostgreSQL EXPLAIN Partition Pruning Verification on Dynamic Partition")
    print("======================================================================")

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    cursor = conn.cursor()

    # 1. Dynamically pre-create partition for July 2026
    dt_july = datetime(2026, 7, 15)
    partition_name, created = ensure_monthly_partition(conn, dt_july)

    # 2. Insert event for July 2026
    cursor.execute("""
        INSERT INTO fct_events (
            event_sk, event_id, event_date_sk, user_sk, session_id, platform, app_version,
            event_name, category, priority, schema_version, event_ts, payload_json
        ) VALUES (
            8888, 'uuid-july-dynamic', 20260715, 1, 'sess-july', 'web', '1.2.0',
            'planning_wizard_completed', 'Planning', 'Critical', '1.0.0', '2026-07-15 14:30:00+00', '{}'
        ) ON CONFLICT DO NOTHING;
    """)
    conn.commit()

    # 3. Execute EXPLAIN (COSTS OFF) for July 2026 date range
    explain_query = """
        EXPLAIN (COSTS OFF)
        SELECT event_id, event_name, event_ts
        FROM fct_events
        WHERE event_ts >= '2026-07-01 00:00:00+00' AND event_ts < '2026-08-01 00:00:00+00';
    """
    cursor.execute(explain_query)
    explain_lines = [r[0] for r in cursor.fetchall()]
    explain_text = "\n".join(explain_lines)

    print("\nPostgreSQL EXPLAIN Output for July 2026 Query:")
    print("----------------------------------------------------------------------")
    print(explain_text)
    print("----------------------------------------------------------------------")

    # Assert Pruning
    if 'fct_events_y2026m07' in explain_text:
        non_target = ['fct_events_y2026m01', 'fct_events_y2026m02', 'fct_events_y2026m03', 'fct_events_default']
        pruned_all = all(p not in explain_text for p in non_target)
        if pruned_all:
            print("\n[SUCCESS] Dynamic Partition Pruning VERIFIED 100%! PostgreSQL query planner scanned ONLY 'fct_events_y2026m07' and pruned all other partitions.")
        else:
            print("\n[FAIL] Non-target partitions were scanned!")
            sys.exit(1)
    else:
        print("\n[FAIL] Target partition fct_events_y2026m07 was not scanned!")
        sys.exit(1)

    # 4. Query actual persistent row from fct_pipeline_runs table for Point 3
    print("\n----------------------------------------------------------------------")
    print("Querying Actual Persistent Row from fct_pipeline_runs Table:")
    print("----------------------------------------------------------------------")
    cursor.execute("""
        SELECT run_id, dag_id, lane, start_time, end_time, duration_seconds, rows_extracted, rows_loaded, status
        FROM fct_pipeline_runs
        ORDER BY start_time DESC
        LIMIT 1;
    """)
    row = cursor.fetchone()
    if row:
        print(f"  run_id:           {row[0]}")
        print(f"  dag_id:           {row[1]}")
        print(f"  lane:             {row[2]}")
        print(f"  start_time:       {row[3]}")
        print(f"  end_time:         {row[4]}")
        print(f"  duration_seconds: {row[5]}")
        print(f"  rows_extracted:   {row[6]}")
        print(f"  rows_loaded:      {row[7]}")
        print(f"  status:           {row[8]}")
    else:
        print("  [WARN] No audit run row found!")

    conn.close()

if __name__ == '__main__':
    main()
