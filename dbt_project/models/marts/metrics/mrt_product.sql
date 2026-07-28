{{ config(materialized='table') }}

WITH feature_usage AS (
    SELECT
        'Disciplinas & Professores' AS feature_key,
        COUNT(DISTINCT user_sk) AS unique_users_count,
        SUM(events_count) AS total_events_count
    FROM {{ ref('fct_daily_user_activity') }}
    UNION ALL
    SELECT
        'Avaliações' AS feature_key,
        COUNT(DISTINCT user_sk) AS unique_users_count,
        COUNT(rating_sk) AS total_events_count
    FROM {{ ref('fct_ratings') }}
    UNION ALL
    SELECT
        'Sessões de Estudo' AS feature_key,
        COUNT(DISTINCT user_sk) AS unique_users_count,
        COUNT(session_sk) AS total_events_count
    FROM {{ ref('fct_sessions') }}
)
SELECT
    feature_key,
    unique_users_count,
    total_events_count,
    DENSE_RANK() OVER (ORDER BY total_events_count DESC) AS rank_most_used,
    DENSE_RANK() OVER (ORDER BY total_events_count ASC) AS rank_least_used
FROM feature_usage
