{{ config(materialized='table') }}

WITH dim_users_current AS (
    SELECT COUNT(*) AS total_current_users
    FROM {{ ref('dim_users') }}
    WHERE is_current = true
),
daily_dau AS (
    SELECT
        d.full_date AS activity_date,
        COUNT(DISTINCT a.user_sk) AS dau
    FROM {{ ref('fct_daily_user_activity') }} a
    JOIN {{ ref('dim_date') }} d ON a.date_sk = d.date_sk
    WHERE a.is_active_day = 1
    GROUP BY d.full_date
),
rolling_window AS (
    SELECT
        activity_date,
        dau,
        (
            SELECT COUNT(DISTINCT a7.user_sk)
            FROM {{ ref('fct_daily_user_activity') }} a7
            JOIN {{ ref('dim_date') }} d7 ON a7.date_sk = d7.date_sk
            WHERE d7.full_date BETWEEN d.activity_date - INTERVAL '6 days' AND d.activity_date
        ) AS wau,
        (
            SELECT COUNT(DISTINCT a30.user_sk)
            FROM {{ ref('fct_daily_user_activity') }} a30
            JOIN {{ ref('dim_date') }} d30 ON a30.date_sk = d30.date_sk
            WHERE d30.full_date BETWEEN d.activity_date - INTERVAL '29 days' AND d.activity_date
        ) AS mau
    FROM daily_dau d
),
session_stats AS (
    SELECT
        s.session_start_date_sk,
        ROUND(AVG(s.session_duration_seconds), 2) AS avg_session_duration_seconds,
        COUNT(DISTINCT s.session_sk) AS total_sessions,
        COUNT(DISTINCT CASE WHEN s.screens_viewed_count <= 1 THEN s.session_sk END) AS single_event_sessions
    FROM {{ ref('fct_sessions') }} s
    GROUP BY s.session_start_date_sk
),
user_session_ranks AS (
    SELECT
        user_sk,
        COUNT(session_sk) AS session_cnt,
        NTILE(10) OVER (ORDER BY COUNT(session_sk) DESC) AS decile
    FROM {{ ref('fct_sessions') }}
    GROUP BY user_sk
),
power_users_agg AS (
    SELECT
        COUNT(DISTINCT CASE WHEN decile = 1 THEN user_sk END) AS power_users_count
    FROM user_session_ranks
)
SELECT
    r.activity_date,
    r.dau,
    r.wau,
    r.mau,
    ROUND(r.dau::NUMERIC / NULLIF(r.mau, 0), 4) AS stickiness_dau_mau,
    COALESCE(s.avg_session_duration_seconds, 0) AS avg_session_duration_seconds,
    ROUND(s.total_sessions::NUMERIC / NULLIF(r.dau, 0), 2) AS sessions_per_user,
    ROUND(COALESCE(s.single_event_sessions, 0)::NUMERIC / NULLIF(s.total_sessions, 0), 4) AS bounce_rate,
    ROUND(r.dau::NUMERIC / NULLIF(u.total_current_users, 0), 4) AS feature_adoption_rate,
    (u.total_current_users - r.mau) AS dormant_users_count,
    COALESCE(p.power_users_count, 0) AS power_users_count
FROM rolling_window r
LEFT JOIN {{ ref('dim_date') }} d ON r.activity_date = d.full_date
LEFT JOIN session_stats s ON d.date_sk = s.session_start_date_sk
CROSS JOIN power_users_agg p
CROSS JOIN dim_users_current u
