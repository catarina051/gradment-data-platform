{{ config(materialized='table') }}

SELECT
    CAST(start_time AS DATE) AS run_date,
    COUNT(run_id) AS total_runs,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) AS successful_runs,
    ROUND(COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END)::NUMERIC / NULLIF(COUNT(run_id), 0), 4) AS pipeline_success_rate,
    ROUND(AVG(duration_seconds), 2) AS avg_pipeline_runtime_seconds,
    SUM(rows_extracted) AS total_rows_extracted,
    SUM(rows_loaded) AS total_rows_loaded
FROM {{ ref('fct_pipeline_runs') }}
GROUP BY CAST(start_time AS DATE)
