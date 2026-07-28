{{ config(materialized='table') }}

WITH user_engagement AS (
    SELECT
        s.user_sk,
        COUNT(s.session_sk) AS session_count,
        SUM(s.session_duration_seconds) AS total_duration
    FROM {{ ref('fct_sessions') }} s
    GROUP BY s.user_sk
),
ranked_users AS (
    SELECT
        user_sk,
        session_count,
        total_duration,
        NTILE(10) OVER (ORDER BY session_count DESC) AS engagement_decile
    FROM user_engagement
),
high_value_events AS (
    SELECT
        COUNT(CASE WHEN event_name IN ('material_downloaded', 'planning_session_completed') THEN 1 END) AS high_value_count
    FROM {{ ref('fct_events') }}
),
institutional AS (
    SELECT
        ROUND(
            COUNT(DISTINCT CASE WHEN university_sk = 1 THEN user_sk END)::NUMERIC / NULLIF(COUNT(DISTINCT user_sk), 0), 4
        ) AS institutional_concentration_rate
    FROM {{ ref('fct_daily_user_activity') }}
)
SELECT
    COUNT(DISTINCT r.user_sk) AS total_engaged_users,
    SUM(CASE WHEN r.engagement_decile = 1 THEN r.session_count ELSE 0 END) AS top_decile_sessions,
    SUM(r.session_count) AS total_sessions,
    ROUND(
        SUM(CASE WHEN r.engagement_decile = 1 THEN r.session_count ELSE 0 END)::NUMERIC / NULLIF(SUM(r.session_count), 0), 4
    ) AS power_user_concentration_rate,
    COALESCE(h.high_value_count, 0) AS high_value_feature_usage_count,
    COALESCE(i.institutional_concentration_rate, 0.0) AS institutional_concentration_rate,
    ROUND(AVG(r.session_count)::NUMERIC / NULLIF(AVG(r.total_duration), 0), 6) AS willingness_to_engage_proxy
FROM ranked_users r
CROSS JOIN high_value_events h
CROSS JOIN institutional i
GROUP BY h.high_value_count, i.institutional_concentration_rate
