"""
quality_dag.py
--------------
Airflow DAG for Data Quality Validation (GradMent Data Platform - Phase 5).
Triggered upon pipeline completion. Gates downstream dashboard consumption by executing
dbt schema/singular tests and schema drift detection as mandatory blocking steps.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='quality_dag',
    default_args=default_args,
    description='Data Quality, Singular Invariant & Schema Drift Validation Gate',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['quality', 'validation', 'phase5'],
) as dag:

    check_schema_drift_task = BashOperator(
        task_id='check_schema_drift',
        bash_command='python /opt/airflow/scripts/check_schema_drift.py',
    )

    dbt_test_task = BashOperator(
        task_id='dbt_test_blocking_gate',
        bash_command='cd /opt/airflow/dbt_project && dbt test',
    )

    run_phase5_validation = BashOperator(
        task_id='validate_phase5_quality_suite',
        bash_command='python /opt/airflow/scripts/validate_phase5_quality.py',
    )

    check_schema_drift_task >> dbt_test_task >> run_phase5_validation
