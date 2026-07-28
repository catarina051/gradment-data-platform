{{ config(materialized='table') }}

WITH new_users AS (
    SELECT
        user_sk,
        user_id,
        registration_date
    FROM {{ ref('dim_users') }}
),
first_events AS (
    SELECT
        e.user_sk,
        MIN(e.event_ts) AS first_event_ts,
        MIN(CASE WHEN e.event_name = 'discipline_rated' THEN e.event_ts END) AS first_rating_ts,
        MIN(CASE WHEN e.event_name = 'material_uploaded' THEN e.event_ts END) AS first_upload_ts,
        MIN(CASE WHEN e.event_name = 'planning_session_completed' THEN e.event_ts END) AS first_planning_ts
    FROM {{ ref('fct_events') }} e
    GROUP BY e.user_sk
)
SELECT
    u.registration_date,
    COUNT(DISTINCT u.user_sk) AS total_cohort_new_users,
    COUNT(DISTINCT CASE WHEN f.first_event_ts IS NOT NULL AND f.first_event_ts <= (u.registration_date + INTERVAL '7 days') THEN u.user_sk END) AS activated_users_7d,
    ROUND(
        COUNT(DISTINCT CASE WHEN f.first_event_ts IS NOT NULL AND f.first_event_ts <= (u.registration_date + INTERVAL '7 days') THEN u.user_sk END)::NUMERIC /
        NULLIF(COUNT(DISTINCT u.user_sk), 0), 4
    ) AS activation_rate_7d,
    COUNT(DISTINCT CASE WHEN f.first_rating_ts IS NOT NULL THEN u.user_sk END) AS users_first_action_rating,
    COUNT(DISTINCT CASE WHEN f.first_upload_ts IS NOT NULL THEN u.user_sk END) AS users_first_action_upload
FROM new_users u
LEFT JOIN first_events f ON u.user_sk = f.user_sk
GROUP BY u.registration_date
