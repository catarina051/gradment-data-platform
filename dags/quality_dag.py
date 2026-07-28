"""
quality_dag.py
--------------
Airflow DAG for Data Quality Validation (GradMent Data Platform - Phase 4/5).
Triggered upon successful completion of extraction and transformation pipelines.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data_engineering',
    'retries': 1,
}

with DAG(
    dag_id='quality_dag',
    default_args=default_args,
    description='Data Quality & Schema Drift Checks',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['quality', 'validation'],
) as dag:

    run_schema_validation = BashOperator(
        task_id='validate_star_schema',
        bash_command='python /opt/airflow/scripts/validate_star_schema.py',
    )

    run_pipeline_validation = BashOperator(
        task_id='validate_pipeline_execution',
        bash_command='python /opt/airflow/scripts/validate_phase4_pipeline.py',
    )

    run_schema_validation >> run_pipeline_validation
