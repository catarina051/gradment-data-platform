"""
extract_transform_synthetic.py
------------------------------
Airflow DAG for Synthetic Data Lane (GradMent Data Platform - Phase 4).
Runs hourly by default. Generates synthetic seeds, ensures range partitions, extracts events,
runs dbt snapshots, executes full dbt pipeline (staging -> marts), and logs audit metrics.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='extract_transform_synthetic',
    default_args=default_args,
    description='Synthetic Lane ETL Pipeline (Hourly Incremental Load)',
    schedule_interval='@hourly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['synthetic', 'etl', 'phase4'],
) as dag:

    generate_seeds = BashOperator(
        task_id='generate_synthetic_seeds',
        bash_command='python /opt/airflow/scripts/synthetic/generate_seeds.py 1',
    )

    extract_events = BashOperator(
        task_id='extract_synthetic_events',
        bash_command='python /opt/airflow/extract/extract_events.py --source synthetic',
    )

    extract_reference = BashOperator(
        task_id='extract_synthetic_reference_data',
        bash_command='python /opt/airflow/extract/extract_reference_tables.py --source synthetic',
    )

    dbt_snapshot = BashOperator(
        task_id='dbt_snapshot',
        bash_command='cd /opt/airflow/dbt_project && dbt snapshot',
    )

    # Item 2 Clarification: dbt_run_full_pipeline executes dbt run for ALL models (staging -> marts)
    dbt_run_full_pipeline = BashOperator(
        task_id='dbt_run_full_pipeline',
        bash_command='cd /opt/airflow/dbt_project && dbt run',
    )

    log_audit = BashOperator(
        task_id='log_pipeline_run',
        bash_command='python /opt/airflow/extract/audit.py --dag extract_transform_synthetic',
    )

    generate_seeds >> [extract_events, extract_reference] >> dbt_snapshot >> dbt_run_full_pipeline >> log_audit
