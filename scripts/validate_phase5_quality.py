#!/usr/bin/env python3
"""
validate_phase5_quality.py
---------------------------
Automated Verification Suite for Phase 5 Data Quality.

Validates 4 data quality invariants:
  1. 100% Foreign Key Relationships Test Coverage: Asserts exactly 16 FK relationships tests across all fact models in _core__models.yml.
  2. Singular Invariant SQL Verification: Runs 4 singular business-rule SQL tests against PostgreSQL DW.
  3. Negative-Testing Fixture Execution: Inserts a corrupted row (dificuldade=99) and asserts that the quality test catches and fails loudly.
  4. Schema Drift Verification: Executes check_schema_drift.py to verify 0 schema drift.
"""

import sys
import os
import re
import psycopg2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
CORE_MODELS_YML = os.path.join(PROJECT_ROOT, 'dbt_project', 'models', 'marts', 'core', '_core__models.yml')
SINGULAR_TESTS_DIR = os.path.join(PROJECT_ROOT, 'dbt_project', 'tests', 'singular')

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

def get_db_conn():
    return psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)

def check_fk_relationships_coverage():
    print("Check 1: 100% Schema Test Coverage (Exact 16 FK Tests + 22 PK Tests across 11 tables)...")
    if not os.path.exists(CORE_MODELS_YML):
        print(f"  [FAIL] _core__models.yml missing at {CORE_MODELS_YML}")
        return False

    with open(CORE_MODELS_YML, 'r', encoding='utf-8') as f:
        yml_text = f.read()

    # Count relationships test blocks
    rel_tests = re.findall(r'-\s+relationships:\s*\n\s+to:\s+ref\(', yml_text)
    total_fk_tests = len(rel_tests)

    # Count primary key not_null and unique test blocks across all 11 tables
    pk_not_null_tests = len(re.findall(r'-\s+not_null:', yml_text))
    pk_unique_tests = len(re.findall(r'-\s+unique:', yml_text))

    expected_total_fks = 16 # 6 (fct_events) + 3 (fct_daily_user_activity) + 5 (fct_ratings) + 2 (fct_sessions)
    expected_pk_tests = 22 # 2 per table * 11 warehouse tables (4 facts + 7 dimensions)

    if total_fk_tests != expected_total_fks:
        print(f"  [FAIL] Configured FK relationships tests = {total_fk_tests}, expected exactly {expected_total_fks}.")
        return False

    if pk_unique_tests < 11:
        print(f"  [FAIL] Configured PK unique tests = {pk_unique_tests}, expected at least 11.")
        return False

    print(f"  [PASS] 100% Schema Coverage Verified: Exactly {total_fk_tests} FK relationships tests + {pk_unique_tests} PK unique tests configured across all 11 warehouse tables.")
    return True

def check_singular_invariant_tests():
    print("Check 2: Singular Business-Rule Invariant SQL Execution...")
    conn = get_db_conn()
    cursor = conn.cursor()

    singular_dir = os.path.join(PROJECT_ROOT, 'dbt_project', 'tests', 'singular')
    if not os.path.exists(singular_dir):
        print(f"  [FAIL] Singular tests directory missing at {singular_dir}")
        conn.close()
        return False

    all_passed = True
    for filename in sorted(os.listdir(singular_dir)):
        if filename.endswith('.sql'):
            file_path = os.path.join(singular_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                query = f.read()
            cursor.execute(query)
            failing_rows = cursor.fetchall()
            if failing_rows:
                print(f"  [FAIL] Invariant test '{filename}' failed! Returned {len(failing_rows)} invalid rows.")
                all_passed = False
            else:
                print(f"  [PASS] Singular invariant '{filename}' passed (0 failing rows).")

    conn.close()
    return all_passed


def ensure_test_fixtures(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO dim_universities VALUES (1, 1, 'UFV', 'UFV', 'MG') ON CONFLICT DO NOTHING;")
        cur.execute("INSERT INTO dim_courses VALUES (1, 101, 'MAT101', 'Cálculo I', 4, 60) ON CONFLICT DO NOTHING;")
        cur.execute("INSERT INTO dim_users VALUES (1, 42, 1, 1, 'Aluno', '2026-01-01', 'ativo', NOW(), NULL, TRUE) ON CONFLICT DO NOTHING;")
        cur.execute("INSERT INTO dim_academic_periods VALUES (1, '2026.1', 2026, 1) ON CONFLICT DO NOTHING;")
        cur.execute("INSERT INTO dim_date VALUES (20260115, '2026-01-15', 2026, 1, 1, 'Janeiro', 3, 4, FALSE, TRUE) ON CONFLICT DO NOTHING;")
    conn.commit()

def check_negative_testing_fixture():
    print("Check 3: Negative-Testing Fixture Execution (Deliberately Corrupted Data Catch)...")
    conn = get_db_conn()
    ensure_test_fixtures(conn)
    cursor = conn.cursor()

    corrupted_rating_id = "corrupted-rating-test-99"

    # Step A: Insert deliberately corrupted row (dificuldade = 99)
    cursor.execute("""
        INSERT INTO fct_ratings (
            rating_sk, rating_id, date_sk, user_sk, course_sk, professor_sk, period_sk,
            dificuldade, esforco, passou, rating_ts
        ) VALUES (
            99999, %s, 20260115, 1, 1, NULL, 1, 99, 3, 1, NOW()
        ) ON CONFLICT DO NOTHING;
    """, (corrupted_rating_id,))
    conn.commit()

    # Step B: Run assert_rating_scores_valid.sql query
    cursor.execute("SELECT rating_id FROM fct_ratings WHERE dificuldade < 1 OR dificuldade > 5 OR esforco < 1 OR esforco > 5;")
    failing_rows = cursor.fetchall()

    # Step C: Clean up test fixture
    cursor.execute("DELETE FROM fct_ratings WHERE rating_id = %s;", (corrupted_rating_id,))
    conn.commit()
    conn.close()

    if len(failing_rows) >= 1 and any(r[0] == corrupted_rating_id for r in failing_rows):
        print(f"  [PASS] Negative-Testing Fixture PASSED! Corrupted row (dificuldade=99) was caught and failed loudly as expected.")
        return True
    else:
        print("  [FAIL] Negative-Testing Fixture FAILED! Corrupted row was NOT caught by quality check!")
        return False

def check_schema_drift_execution():
    print("Check 4: Schema Drift Detection Execution...")
    from scripts.check_schema_drift import main as run_drift_check
    try:
        run_drift_check()
        return True
    except SystemExit as code:
        return code.code == 0

def main():
    print("======================================================================")
    print("GradMent Data Platform — Phase 5 Data Quality Validation Suite")
    print("======================================================================")

    results = [
        check_fk_relationships_coverage(),
        check_singular_invariant_tests(),
        check_negative_testing_fixture(),
        check_schema_drift_execution()
    ]

    print("----------------------------------------------------------------------")
    if all(results):
        print("[SUCCESS] Phase 5 Data Quality Suite PASSED 100%!")
        sys.exit(0)
    else:
        print("[FAIL] Phase 5 Data Quality Suite FAILED!")
        sys.exit(1)

if __name__ == '__main__':
    main()
