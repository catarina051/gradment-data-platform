#!/usr/bin/env python3
"""
generate_dashboards.py
----------------------
Compiles Metabase dashboard exports and generates the embedded data snapshot
for the public showcase app (`showcase/data_snapshot.json`).
"""

import sys
import os
import re
import json
import psycopg2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
METABASE_EXPORT_PATH = os.path.join(PROJECT_ROOT, 'metabase', 'export_dashboards.json')
SHOWCASE_DATA_PATH = os.path.join(PROJECT_ROOT, 'showcase', 'data_snapshot.json')

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

def get_db_conn():
    return psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)

def fetch_table_data(conn, table_name, order_by=""):
    with conn.cursor() as cur:
        query = f"SELECT * FROM {table_name} {order_by} LIMIT 10;"
        cur.execute(query)
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        result_rows = []
        for r in rows:
            formatted_row = {}
            for col, val in zip(colnames, r):
                if hasattr(val, 'isoformat'):
                    formatted_row[col] = val.isoformat()
                elif hasattr(val, '__float__'):
                    formatted_row[col] = float(val)
                else:
                    formatted_row[col] = val
            result_rows.append(formatted_row)
        return result_rows

def build_mart_views(conn):
    with conn.cursor() as cur:
        marts = [
            'mrt_acquisition', 'mrt_activation', 'mrt_retention', 'mrt_engagement',
            'mrt_content', 'mrt_product', 'mrt_quality', 'mrt_data_engineering', 'mrt_monetization_readiness'
        ]
        for m in marts:
            sql_path = os.path.join(PROJECT_ROOT, 'dbt_project', 'models', 'marts', 'metrics', f"{m}.sql")
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            clean_sql = re.sub(r"\{\{\s*config\([^\)]+\)\s*\}\}", "", sql)
            clean_sql = clean_sql.replace("{{ ref('dim_users') }}", "dim_users")
            clean_sql = clean_sql.replace("{{ ref('dim_date') }}", "dim_date")
            clean_sql = clean_sql.replace("{{ ref('fct_events') }}", "fct_events")
            clean_sql = clean_sql.replace("{{ ref('fct_ratings') }}", "fct_ratings")
            clean_sql = clean_sql.replace("{{ ref('fct_sessions') }}", "fct_sessions")
            clean_sql = clean_sql.replace("{{ ref('fct_daily_user_activity') }}", "fct_daily_user_activity")
            clean_sql = clean_sql.replace("{{ ref('fct_pipeline_runs') }}", "fct_pipeline_runs")

            cur.execute(f"DROP VIEW IF EXISTS {m} CASCADE;")
            cur.execute(f"CREATE VIEW {m} AS {clean_sql};")
    conn.commit()

def main():
    print("======================================================================")
    print("GradMent Data Platform — Dashboard Export & Showcase Snapshot Generator")
    print("======================================================================")

    conn = get_db_conn()

    # Populate synthetic dataset
    from scripts.verify_phase6_dw_performance import populate_scaled_test_data
    populate_scaled_test_data(conn, days_count=180)
    build_mart_views(conn)

    snapshot_data = {
        'acquisition': fetch_table_data(conn, 'mrt_acquisition', 'ORDER BY metric_date DESC'),
        'activation': fetch_table_data(conn, 'mrt_activation', 'ORDER BY registration_date DESC'),
        'retention': fetch_table_data(conn, 'mrt_retention', 'ORDER BY cohort_date DESC'),
        'engagement': fetch_table_data(conn, 'mrt_engagement', 'ORDER BY activity_date DESC'),
        'content': fetch_table_data(conn, 'mrt_content', 'ORDER BY metric_date DESC'),
        'product': fetch_table_data(conn, 'mrt_product', 'ORDER BY rank_most_used ASC'),
        'quality': fetch_table_data(conn, 'mrt_quality', 'ORDER BY error_date DESC'),
        'data_engineering': fetch_table_data(conn, 'mrt_data_engineering', 'ORDER BY run_date DESC'),
        'monetization': fetch_table_data(conn, 'mrt_monetization_readiness')
    }

    conn.close()

    os.makedirs(os.path.dirname(SHOWCASE_DATA_PATH), exist_ok=True)
    with open(SHOWCASE_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(snapshot_data, f, indent=2)
    print(f"[SUCCESS] Generated showcase embedded data snapshot at {SHOWCASE_DATA_PATH}!")

    # Metabase Export Structure
    metabase_export = {
        'version': '1.0',
        'dashboards': [
            {'name': 'Executive Dashboard', 'cards': 3, 'kpi_count': 14},
            {'name': 'Product & Feature Dashboard', 'cards': 3, 'kpi_count': 13},
            {'name': 'Academic & Content Dashboard', 'cards': 2, 'kpi_count': 10},
            {'name': 'Engineering & Observability Dashboard', 'cards': 2, 'kpi_count': 7},
            {'name': 'Data Team Dashboard', 'cards': 2, 'kpi_count': 8},
            {'name': 'Monetization & Business Validation Dashboard', 'cards': 1, 'kpi_count': 4}
        ]
    }

    os.makedirs(os.path.dirname(METABASE_EXPORT_PATH), exist_ok=True)
    with open(METABASE_EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(metabase_export, f, indent=2)
    print(f"[SUCCESS] Generated Metabase dashboard export artifact at {METABASE_EXPORT_PATH}!")

if __name__ == '__main__':
    main()
