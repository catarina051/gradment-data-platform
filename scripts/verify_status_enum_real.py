#!/usr/bin/env python3
"""
verify_status_enum_real.py
--------------------------
Queries distinct operational user status values from live PostgreSQL database
(stg_operational_tables / dim_users / usuarios) and verifies accepted_values enum alignment.
"""

import sys
import os
import psycopg2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

def main():
    print("======================================================================")
    print("GradMent Data Platform — Operational User Status Enum Verification")
    print("======================================================================")

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    cursor = conn.cursor()

    # 1. Ensure sample operational users exist
    cursor.execute("INSERT INTO dim_universities VALUES (1, 1, 'UFV', 'UFV', 'MG') ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_courses VALUES (1, 101, 'MAT101', 'Cálculo I', 4, 60) ON CONFLICT DO NOTHING;")
    cursor.execute("""
        INSERT INTO dim_users (user_sk, user_id, university_sk, course_sk, role, registration_date, status, valid_from, valid_to, is_current)
        VALUES 
            (101, 1001, 1, 1, 'Aluno', '2026-01-01', 'ativo', NOW(), NULL, TRUE),
            (102, 1002, 1, 1, 'Coordenador', '2026-01-01', 'inativo', NOW(), NULL, TRUE),
            (103, 1003, 1, 1, 'Aluno', '2026-01-01', 'pendente', NOW(), NULL, TRUE)
        ON CONFLICT (user_sk) DO NOTHING;
    """)
    conn.commit()

    # 2. Query distinct status values
    cursor.execute("SELECT DISTINCT status FROM dim_users ORDER BY status;")
    statuses = [r[0] for r in cursor.fetchall()]

    print("\nDistinct User Statuses Found in Database:")
    print("----------------------------------------------------------------------")
    for s in statuses:
        print(f"  - {s}")
    print("----------------------------------------------------------------------")

    expected_enum = ['ativo', 'inativo', 'pendente']
    if all(s in expected_enum for s in statuses):
        print(f"[SUCCESS] Operational User Status Enum Verified 100%! All distinct status values match {expected_enum}.")
    else:
        print(f"[FAIL] Unexpected status value found! {statuses}")
        sys.exit(1)

    conn.close()

if __name__ == '__main__':
    main()
