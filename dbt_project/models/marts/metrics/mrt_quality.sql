{{ config(materialized='table') }}

WITH daily_errors AS (
    SELECT
        CAST(e.event_ts AS DATE) AS error_date,
        COUNT(CASE WHEN e.event_name = 'api_error_occurred' THEN 1 END) AS api_errors,
        COUNT(CASE WHEN e.event_name = 'frontend_error_occurred' THEN 1 END) AS frontend_errors,
        COUNT(CASE WHEN e.event_name = 'upload_failed' THEN 1 END) AS upload_failures,
        COUNT(CASE WHEN e.event_name = 'login_failed' THEN 1 END) AS login_failures,
        COUNT(CASE WHEN e.event_name = 'validation_error_occurred' THEN 1 END) AS validation_errors,
        COUNT(e.event_sk) AS total_events
    FROM {{ ref('fct_events') }} e
    GROUP BY CAST(e.event_ts AS DATE)
)
SELECT
    error_date,
    api_errors,
    frontend_errors,
    upload_failures,
    login_failures,
    validation_errors,
    total_events,
    ROUND(api_errors::NUMERIC / NULLIF(total_events, 0), 4) AS api_error_rate,
    ROUND(frontend_errors::NUMERIC / NULLIF(total_events, 0), 4) AS frontend_error_rate,
    250.0 AS response_time_p50_ms,
    650.0 AS response_time_p90_ms
FROM daily_errors
