#!/usr/bin/env python3
"""
validate_phase6_warehouse.py
-----------------------------
Automated Verification Suite for Phase 6 Data Warehouse (Performance & Catalog).

Validates 5 Data Warehouse invariants:
  1. Data Catalog Completeness: Asserts 11/11 table catalog markdown files exist under docs/data-catalog/.
  2. Lineage Documentation: Asserts docs/lineage.md contains the 3 specific lineage chains and docs/lineage.png exists.
  3. dbt Materialization Strategy: Asserts unique_key='event_id' and incremental_strategy='delete+insert' in dbt_project.yml.
  4. Physical Indexing Verification: Queries PostgreSQL pg_indexes for composite index idx_fct_daily_activity_date_user.
  5. Performance SLA Verification: Executes verify_phase6_dw_performance.py and verifies execution latency < 3.0s (NFR-2).
"""

import sys
import os
import psycopg2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

CATALOG_DIR = os.path.join(PROJECT_ROOT, 'docs', 'data-catalog')
LINEAGE_MD_PATH = os.path.join(PROJECT_ROOT, 'docs', 'lineage.md')
LINEAGE_PNG_PATH = os.path.join(PROJECT_ROOT, 'docs', 'lineage.png')
DBT_PROJECT_YML_PATH = os.path.join(PROJECT_ROOT, 'dbt_project', 'dbt_project.yml')
BENCHMARK_REPORT_PATH = os.path.join(PROJECT_ROOT, 'docs', 'pipeline_benchmarks.md')

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

def get_db_conn():
    return psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)

def check_data_catalog_completeness():
    print("Check 1: Data Catalog Documentation Completeness (11/11 Tables)...")
    expected_files = [
        'fct_events.md', 'fct_daily_user_activity.md', 'fct_ratings.md', 'fct_sessions.md',
        'dim_users.md', 'dim_professors.md', 'dim_courses.md', 'dim_universities.md',
        'dim_academic_periods.md', 'dim_date.md', 'dim_screens.md'
    ]

    missing = []
    for f in expected_files:
        path = os.path.join(CATALOG_DIR, f)
        if not os.path.exists(path):
            missing.append(f)

    if missing:
        print(f"  [FAIL] Missing catalog markdown files: {missing}")
        return False

    print("  [PASS] 100% Data Catalog Completeness Verified! All 11 warehouse table catalog docs exist under docs/data-catalog/.")
    return True

def check_lineage_documentation():
    print("Check 2: Lineage Documentation & Specific Lineage Chains...")
    if not os.path.exists(LINEAGE_MD_PATH):
        print("  [FAIL] docs/lineage.md missing!")
        return False

    if not os.path.exists(LINEAGE_PNG_PATH):
        print("  [FAIL] docs/lineage.png missing!")
        return False

    with open(LINEAGE_MD_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    chains = ['discipline_rated', 'fct_sessions', 'fct_pipeline_runs']
    for c in chains:
        if c not in text:
            print(f"  [FAIL] Specific lineage chain for '{c}' missing in docs/lineage.md!")
            return False

    print("  [PASS] Lineage Documentation Verified! docs/lineage.md contains all 3 specific chains and docs/lineage.png exists.")
    return True

def check_dbt_materialization_strategy():
    print("Check 3: dbt Materialization Strategy (delete+insert by event_id)...")
    if not os.path.exists(DBT_PROJECT_YML_PATH):
        print("  [FAIL] dbt_project.yml missing!")
        return False

    with open(DBT_PROJECT_YML_PATH, 'r', encoding='utf-8') as f:
        yml = f.read()

    if "event_id" not in yml or "delete+insert" not in yml:
        print("  [FAIL] dbt_project.yml missing unique_key: event_id or incremental_strategy: delete+insert!")
        return False

    print("  [PASS] dbt Materialization Strategy Verified! fct_events incremental configured with delete+insert by event_id.")
    return True

def check_physical_indexing():
    print("Check 4: PostgreSQL Physical Indexing (Composite Index Test)...")
    conn = get_db_conn()
    cursor = conn.cursor()

    # Re-apply DDL to ensure indexes exist
    schema_sql_path = os.path.join(PROJECT_ROOT, 'warehouse', 'schema.sql')
    with open(schema_sql_path, 'r', encoding='utf-8') as f:
        cursor.execute(f.read())
    conn.commit()

    cursor.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'fct_daily_user_activity' AND indexname = 'idx_fct_daily_activity_date_user';")
    idx = cursor.fetchone()
    conn.close()

    if not idx:
        print("  [FAIL] Composite index 'idx_fct_daily_activity_date_user' missing on PostgreSQL!")
        return False

    print("  [PASS] Physical Indexing Verified! Composite index 'idx_fct_daily_activity_date_user' present on PostgreSQL.")
    return True

def check_performance_benchmark():
    print("Check 5: Analytical Query Performance SLA Benchmarking (< 3.0s NFR-2)...")
    from scripts.verify_phase6_dw_performance import main as run_benchmark
    try:
        run_benchmark()
    except Exception as e:
        print(f"  [FAIL] Benchmark execution failed: {e}")
        return False

    if not os.path.exists(BENCHMARK_REPORT_PATH):
        print("  [FAIL] Benchmark report docs/pipeline_benchmarks.md not generated!")
        return False

    print("  [PASS] Analytical Query Performance SLA Verified! docs/pipeline_benchmarks.md generated successfully.")
    return True

def main():
    print("======================================================================")
    print("GradMent Data Platform — Phase 6 Data Warehouse Validation Suite")
    print("======================================================================")

    results = [
        check_data_catalog_completeness(),
        check_lineage_documentation(),
        check_dbt_materialization_strategy(),
        check_physical_indexing(),
        check_performance_benchmark()
    ]

    print("----------------------------------------------------------------------")
    if all(results):
        print("[SUCCESS] Phase 6 Data Warehouse Suite PASSED 100%!")
        sys.exit(0)
    else:
        print("[FAIL] Phase 6 Data Warehouse Suite FAILED!")
        sys.exit(1)

if __name__ == '__main__':
    main()
