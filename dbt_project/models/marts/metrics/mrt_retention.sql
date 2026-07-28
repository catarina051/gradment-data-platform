{{ config(materialized='table') }}

WITH cohorts AS (
    SELECT
        user_sk,
        registration_date AS cohort_date
    FROM {{ ref('dim_users') }}
),
user_activity AS (
    SELECT
        a.user_sk,
        d.full_date AS activity_date
    FROM {{ ref('fct_daily_user_activity') }} a
    JOIN {{ ref('dim_date') }} d ON a.date_sk = d.date_sk
)
SELECT
    c.cohort_date,
    COUNT(DISTINCT c.user_sk) AS cohort_size,
    COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '1 day' THEN c.user_sk END) AS d1_active_users,
    COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '7 days' THEN c.user_sk END) AS d7_active_users,
    COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '14 days' THEN c.user_sk END) AS d14_active_users,
    COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '30 days' THEN c.user_sk END) AS d30_active_users,
    ROUND(
        COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '1 day' THEN c.user_sk END)::NUMERIC / NULLIF(COUNT(DISTINCT c.user_sk), 0), 4
    ) AS d1_retention_rate,
    ROUND(
        COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '7 days' THEN c.user_sk END)::NUMERIC / NULLIF(COUNT(DISTINCT c.user_sk), 0), 4
    ) AS d7_retention_rate,
    ROUND(
        COUNT(DISTINCT CASE WHEN act.activity_date = c.cohort_date + INTERVAL '30 days' THEN c.user_sk END)::NUMERIC / NULLIF(COUNT(DISTINCT c.user_sk), 0), 4
    ) AS d30_retention_rate
FROM cohorts c
LEFT JOIN user_activity act ON c.user_sk = act.user_sk
GROUP BY c.cohort_date
