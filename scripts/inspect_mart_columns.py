#!/usr/bin/env python3
"""
inspect_mart_columns.py
------------------------
Inspects physical SQL column definitions and sample query outputs for the 4 requested metric mart models:
  1. mrt_quality
  2. mrt_content
  3. mrt_engagement
  4. mrt_monetization_readiness
"""

import os
import psycopg2

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_DIR = os.path.join(PROJECT_ROOT, 'dbt_project', 'models', 'marts', 'metrics')

def main():
    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    cursor = conn.cursor()

    marts = ['mrt_quality', 'mrt_content', 'mrt_engagement', 'mrt_monetization_readiness']

    print("======================================================================")
    print("GradMent Data Platform — Metric Mart SQL Inspection & Sample Outputs")
    print("======================================================================")

    for mart in marts:
        sql_path = os.path.join(METRICS_DIR, f"{mart}.sql")
        print(f"\n----------------------------------------------------------------------------------------------------")
        print(f"MODEL: {mart}.sql (File Path: {sql_path})")
        print(f"----------------------------------------------------------------------------------------------------")
        
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Remove dbt config line for native postgres execution
        clean_sql = re.sub(r"\{\{\s*config\([^\)]+\)\s*\}\}", "", sql)
        clean_sql = clean_sql.replace("{{ ref('dim_users') }}", "dim_users")
        clean_sql = clean_sql.replace("{{ ref('dim_date') }}", "dim_date")
        clean_sql = clean_sql.replace("{{ ref('fct_events') }}", "fct_events")
        clean_sql = clean_sql.replace("{{ ref('fct_ratings') }}", "fct_ratings")
        clean_sql = clean_sql.replace("{{ ref('fct_sessions') }}", "fct_sessions")
        clean_sql = clean_sql.replace("{{ ref('fct_daily_user_activity') }}", "fct_daily_user_activity")
        clean_sql = clean_sql.replace("{{ ref('fct_pipeline_runs') }}", "fct_pipeline_runs")

        # Execute view creation in temp table or select directly
        query_sql = f"WITH mart_view AS ({clean_sql}) SELECT * FROM mart_view LIMIT 1;"
        cursor.execute(query_sql)

        colnames = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        print(f"Columns Created ({len(colnames)} total):")
        for i, col in enumerate(colnames, 1):
            print(f"  [{i:02d}] {col}")

        print(f"\nSample Output Row (1 row):")
        print(row)

    conn.close()

if __name__ == '__main__':
    import re
    main()
