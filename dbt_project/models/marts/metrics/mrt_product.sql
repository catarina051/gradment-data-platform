{{ config(materialized='table') }}

WITH feature_usage AS (
    SELECT
        e.category AS feature_key,
        COUNT(DISTINCT e.user_sk) AS unique_users_count,
        COUNT(e.event_sk) AS total_events_count
    FROM {{ ref('fct_events') }} e
    GROUP BY e.category
),
ranked_features AS (
    SELECT
        feature_key,
        unique_users_count,
        total_events_count,
        DENSE_RANK() OVER (ORDER BY unique_users_count DESC, total_events_count DESC) AS rank_most_used,
        DENSE_RANK() OVER (ORDER BY unique_users_count ASC, total_events_count ASC) AS rank_least_used
    FROM feature_usage
)
SELECT
    feature_key,
    unique_users_count,
    total_events_count,
    rank_most_used,
    rank_least_used
FROM ranked_features
