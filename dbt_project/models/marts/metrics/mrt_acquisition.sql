{{ config(materialized='table') }}

WITH user_stats AS (
    SELECT
        registration_date,
        COUNT(DISTINCT user_sk) AS new_users
    FROM {{ ref('dim_users') }}
    GROUP BY registration_date
),
activity_stats AS (
    SELECT
        d.full_date AS activity_date,
        COUNT(DISTINCT a.user_sk) AS active_users,
        COUNT(DISTINCT CASE WHEN u.registration_date < d.full_date THEN a.user_sk END) AS returning_users
    FROM {{ ref('fct_daily_user_activity') }} a
    JOIN {{ ref('dim_date') }} d ON a.date_sk = d.date_sk
    JOIN {{ ref('dim_users') }} u ON a.user_sk = u.user_sk
    GROUP BY d.full_date
)
SELECT
    COALESCE(u.registration_date, a.activity_date) AS metric_date,
    COALESCE(u.new_users, 0) AS new_users,
    COALESCE(a.returning_users, 0) AS returning_users,
    COALESCE(a.active_users, 0) AS total_active_users,
    SUM(COALESCE(u.new_users, 0)) OVER (ORDER BY COALESCE(u.registration_date, a.activity_date)) AS total_users_cumulative,
    ROUND(
        (COALESCE(u.new_users, 0) - LAG(COALESCE(u.new_users, 0), 1) OVER (ORDER BY COALESCE(u.registration_date, a.activity_date)))::NUMERIC / 
        NULLIF(LAG(COALESCE(u.new_users, 0), 1) OVER (ORDER BY COALESCE(u.registration_date, a.activity_date)), 0), 4
    ) AS user_growth_rate
FROM user_stats u
FULL OUTER JOIN activity_stats a ON u.registration_date = a.activity_date
