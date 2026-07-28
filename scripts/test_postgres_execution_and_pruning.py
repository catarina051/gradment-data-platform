#!/usr/bin/env python3
"""
test_postgres_execution_and_pruning.py
----------------------------------------
Native PostgreSQL Execution & Partition Pruning Verification Script.

Executes 5 strict PostgreSQL validation steps:
  1. Connection to PostgreSQL server (localhost:5432).
  2. Database Creation & DDL Execution: Executes warehouse/schema.sql natively against PostgreSQL.
  3. Schema Table & Partition Discovery: Verifies all 11 tables and 4 monthly partition tables in PostgreSQL catalog.
  4. Data Ingestion Test: Inserts sample events across January, February, and March 2026.
  5. EXPLAIN Partition Pruning Verification: Runs EXPLAIN (COSTS OFF) on date-filtered query and asserts that non-matching partitions are pruned.
"""

import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_SQL_PATH = os.path.join(PROJECT_ROOT, 'warehouse', 'schema.sql')

PG_HOST = 'localhost'
PG_PORT = 5432
PG_USER = 'postgres'
PG_PASS = 'postgres'
PG_DB = 'gradment_dw_test'

def main():
    print("======================================================================")
    print("GradMent Data Platform — Native PostgreSQL Verification Suite")
    print("======================================================================")

    # 1. Connect to default postgres DB and recreate test database
    try:
        conn_default = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname='postgres'
        )
        conn_default.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur_default = conn_default.cursor()
        
        # Terminate active connections to test database if exists
        cur_default.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{PG_DB}' AND pid <> pg_backend_pid();
        """)
        cur_default.execute(f"DROP DATABASE IF EXISTS {PG_DB};")
        cur_default.execute(f"CREATE DATABASE {PG_DB};")
        cur_default.close()
        conn_default.close()
        print(f"[PASS] Recreated fresh PostgreSQL test database '{PG_DB}' on {PG_HOST}:{PG_PORT}.")
    except Exception as e:
        print(f"[FAIL] Could not connect to PostgreSQL or create database: {e}")
        sys.exit(1)

    # 2. Connect to gradment_dw_test and execute warehouse/schema.sql
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB
        )
        cursor = conn.cursor()

        with open(SCHEMA_SQL_PATH, 'r', encoding='utf-8') as f:
            sql_ddl = f.read()

        cursor.execute(sql_ddl)
        conn.commit()
        print("[PASS] Successfully executed warehouse/schema.sql natively in PostgreSQL with 0 errors!")
    except Exception as e:
        print(f"[FAIL] PostgreSQL DDL execution error: {e}")
        sys.exit(1)

    # 3. Check created tables and partitions in PostgreSQL catalog
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [r[0] for r in cursor.fetchall()]
    
    expected_base_tables = {
        'fct_events', 'fct_daily_user_activity', 'fct_ratings', 'fct_sessions',
        'dim_users', 'dim_professors', 'dim_courses', 'dim_universities',
        'dim_academic_periods', 'dim_date', 'dim_screens'
    }
    expected_partitions = {
        'fct_events_y2026m01', 'fct_events_y2026m02', 'fct_events_y2026m03', 'fct_events_default'
    }

    found_base = set(t for t in tables if not t.startswith('fct_events_y2026') and t != 'fct_events_default')
    found_partitions = set(t for t in tables if t.startswith('fct_events_y2026') or t == 'fct_events_default')

    if expected_base_tables - found_base:
        print(f"[FAIL] Missing base tables: {expected_base_tables - found_base}")
        sys.exit(1)
        
    if expected_partitions != found_partitions:
        print(f"[FAIL] Missing partition child tables: {expected_partitions - found_partitions}")
        sys.exit(1)

    print(f"[PASS] Verified 11 base warehouse tables + 4 monthly partition tables in PostgreSQL: {', '.join(sorted(found_partitions))}")

    # 4. Ingest sample data to test partitioning
    try:
        # Populate minimum FK dimension rows
        cursor.execute("INSERT INTO dim_universities VALUES (1, 1, 'UFV', 'UFV', 'MG');")
        cursor.execute("INSERT INTO dim_courses VALUES (1, 101, 'MAT101', 'Cálculo I', 4, 60);")
        cursor.execute("INSERT INTO dim_users VALUES (1, 42, 1, 1, 'Aluno', '2026-01-01', 'ativo', NOW(), NULL, TRUE);")
        cursor.execute("INSERT INTO dim_date VALUES (20260115, '2026-01-15', 2026, 1, 1, 'Janeiro', 3, 4, FALSE, TRUE);")
        cursor.execute("INSERT INTO dim_date VALUES (20260215, '2026-02-15', 2026, 1, 2, 'Fevereiro', 7, 7, TRUE, TRUE);")
        cursor.execute("INSERT INTO dim_date VALUES (20260315, '2026-03-15', 2026, 1, 3, 'Março', 11, 7, TRUE, TRUE);")

        # Insert 3 events into fct_events across different months
        cursor.execute("""
            INSERT INTO fct_events (
                event_sk, event_id, event_date_sk, user_sk, session_id, platform, app_version,
                event_name, category, priority, schema_version, event_ts, payload_json
            ) VALUES
            (101, 'uuid-jan-1', 20260115, 1, 'sess-1', 'web', '1.0', 'app_launched', 'Auth', 'Critical', '1.0.0', '2026-01-15 10:00:00+00', '{}'),
            (102, 'uuid-feb-1', 20260215, 1, 'sess-2', 'web', '1.0', 'discipline_rated', 'Ratings', 'High', '1.0.0', '2026-02-15 14:00:00+00', '{}'),
            (103, 'uuid-mar-1', 20260315, 1, 'sess-3', 'web', '1.0', 'material_downloaded', 'Downloads', 'Medium', '1.0.0', '2026-03-15 16:00:00+00', '{}');
        """)
        conn.commit()

        # Check counts per partition table directly
        cursor.execute("SELECT COUNT(*) FROM fct_events_y2026m01;")
        c_jan = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fct_events_y2026m02;")
        c_feb = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fct_events_y2026m03;")
        c_mar = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fct_events_default;")
        c_def = cursor.fetchone()[0]

        print(f"[PASS] Data routed automatically to PostgreSQL partitions: Jan={c_jan}, Feb={c_feb}, Mar={c_mar}, Default={c_def}")
        assert c_jan == 1 and c_feb == 1 and c_mar == 1 and c_def == 0, "Partition routing mismatch!"
    except Exception as e:
        print(f"[FAIL] Partition data routing failed: {e}")
        sys.exit(1)

    # 5. Execute EXPLAIN to verify partition pruning
    print("\n--- Running EXPLAIN Partition Pruning Verification Query ---")
    query_jan = """
        EXPLAIN (COSTS OFF)
        SELECT event_id, event_name, event_ts
        FROM fct_events
        WHERE event_ts >= '2026-01-01 00:00:00+00' AND event_ts < '2026-02-01 00:00:00+00';
    """
    cursor.execute(query_jan)
    explain_lines = [r[0] for r in cursor.fetchall()]
    explain_text = "\n".join(explain_lines)

    print("PostgreSQL EXPLAIN Output:")
    print("----------------------------------------------------------------------")
    print(explain_text)
    print("----------------------------------------------------------------------")

    # Assert Partition Pruning: fct_events_y2026m01 MUST be present; feb/mar/default MUST NOT be scanned!
    if 'fct_events_y2026m01' in explain_text:
        if 'fct_events_y2026m02' not in explain_text and 'fct_events_y2026m03' not in explain_text and 'fct_events_default' not in explain_text:
            print("[SUCCESS] EXPLAIN Partition Pruning VERIFIED 100%! PostgreSQL scanned ONLY fct_events_y2026m01 and pruned all non-matching partitions.")
        else:
            print("[FAIL] Partition pruning failed: non-matching partitions were scanned!")
            sys.exit(1)
    else:
        print("[FAIL] Expected partition fct_events_y2026m01 not found in EXPLAIN plan!")
        sys.exit(1)

    conn.close()
    print("\n======================================================================")
    print("[SUCCESS] Native PostgreSQL DDL & Partition Pruning Validation PASSED 100%!")
    print("======================================================================")

if __name__ == '__main__':
    main()
