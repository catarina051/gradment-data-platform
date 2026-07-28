"""
extract_transform_real.py
-------------------------
Airflow DAG for Real Production Lane (GradMent Data Platform - Phase 4).

Disabled by default (is_paused_upon_creation=True).
PREREQUISITE FOR ACTIVATION: The read-only `analytics_ro` MySQL user must be created
in GradMent production DB with restricted SELECT grants (excluding passwords/tokens per Section 16).
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='extract_transform_real',
    default_args=default_args,
    description='Real Production Lane ETL Pipeline (Disabled by default)',
    schedule_interval='@hourly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    is_paused_upon_creation=True, # Paused by default until analytics_ro is provisioned
    tags=['real', 'production', 'private'],
) as dag:

    extract_real_events = BashOperator(
        task_id='extract_real_events',
        bash_command='python /opt/airflow/extract/extract_events.py --source real',
    )

    extract_real_reference = BashOperator(
        task_id='extract_real_reference',
        bash_command='python /opt/airflow/extract/extract_reference_tables.py --source real',
    )

    dbt_snapshot_real = BashOperator(
        task_id='dbt_snapshot_real',
        bash_command='cd /opt/airflow/dbt_project && dbt snapshot',
    )

    dbt_run_real_pipeline = BashOperator(
        task_id='dbt_run_real_pipeline',
        bash_command='cd /opt/airflow/dbt_project && dbt run',
    )

    [extract_real_events, extract_real_reference] >> dbt_snapshot_real >> dbt_run_real_pipeline
