#!/usr/bin/env python3
"""
inspect_dashboard_queries.py
----------------------------
Executes 3 representative dashboard queries against PostgreSQL and prints raw output rows:
  1. Executive Dashboard Card 1 (Scalar/Time-Series: DAU, WAU, MAU, Stickiness)
  2. Product Dashboard Card 1 (Tabular Ranked Features: feature_key, unique_users, rank)
  3. Product Dashboard Card 3 (Tabular Cohort Matrix: cohort_date, cohort_size, retention rates)
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
    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    
    # Ensure dataset & mart views exist
    from scripts.generate_dashboards import build_mart_views
    from scripts.verify_phase6_dw_performance import populate_scaled_test_data
    populate_scaled_test_data(conn, days_count=180)
    build_mart_views(conn)

    cursor = conn.cursor()

    print("======================================================================")
    print("GradMent Data Platform — Raw Dashboard Query Execution Results")
    print("======================================================================")

    # 1. Executive Card 1
    q1 = "SELECT activity_date, dau, wau, mau, stickiness_dau_mau FROM mrt_engagement ORDER BY activity_date DESC LIMIT 5;"
    print("\nQUERY 1: Executive Dashboard Card 1 (Executive North Star & Stickiness)")
    print(f"SQL: {q1}")
    cursor.execute(q1)
    cols1 = [d[0] for d in cursor.description]
    print(f"Headers: {cols1}")
    for row in cursor.fetchall():
        print(f"  Row: {row}")

    # 2. Product Card 1
    q2 = "SELECT feature_key, unique_users_count, total_events_count, rank_most_used FROM mrt_product ORDER BY rank_most_used ASC LIMIT 5;"
    print("\nQUERY 2: Product Dashboard Card 1 (Ranked Feature Usage)")
    print(f"SQL: {q2}")
    cursor.execute(q2)
    cols2 = [d[0] for d in cursor.description]
    print(f"Headers: {cols2}")
    for row in cursor.fetchall():
        print(f"  Row: {row}")

    # 3. Product Card 3
    q3 = "SELECT cohort_date, cohort_size, d1_active_users, d7_active_users, d1_retention_rate, d7_retention_rate FROM mrt_retention ORDER BY cohort_date DESC LIMIT 5;"
    print("\nQUERY 3: Product Dashboard Card 3 (Cohort Retention Matrix)")
    print(f"SQL: {q3}")
    cursor.execute(q3)
    cols3 = [d[0] for d in cursor.description]
    print(f"Headers: {cols3}")
    for row in cursor.fetchall():
        print(f"  Row: {row}")

    conn.close()

if __name__ == '__main__':
    main()
