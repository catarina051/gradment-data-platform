{{ config(materialized='table') }}

WITH rating_stats AS (
    SELECT
        d.full_date AS evaluation_date,
        COUNT(r.rating_sk) AS total_ratings,
        AVG(r.dificuldade) AS avg_dificuldade,
        AVG(r.esforco) AS avg_esforco,
        COUNT(DISTINCT r.professor_sk) AS professors_ranked,
        COUNT(DISTINCT r.course_sk) AS courses_ranked
    FROM {{ ref('fct_ratings') }} r
    JOIN {{ ref('dim_date') }} d ON r.date_sk = d.date_sk
    GROUP BY d.full_date
),
event_content_stats AS (
    SELECT
        CAST(e.event_ts AS DATE) AS event_date,
        COUNT(CASE WHEN e.event_name = 'material_downloaded' THEN 1 END) AS downloads,
        COUNT(CASE WHEN e.event_name = 'material_uploaded' THEN 1 END) AS uploads,
        COUNT(CASE WHEN e.event_name = 'search_performed' THEN 1 END) AS searches,
        COUNT(CASE WHEN e.event_name = 'search_result_opened' THEN 1 END) AS search_results_opened,
        COUNT(CASE WHEN e.event_name = 'search_abandoned' THEN 1 END) AS empty_searches
    FROM {{ ref('fct_events') }} e
    GROUP BY CAST(e.event_ts AS DATE)
)
SELECT
    COALESCE(r.evaluation_date, ec.event_date) AS metric_date,
    COALESCE(r.total_ratings, 0) AS total_ratings,
    ROUND(COALESCE(r.avg_dificuldade, 0)::NUMERIC, 2) AS avg_dificuldade,
    ROUND(COALESCE(r.avg_esforco, 0)::NUMERIC, 2) AS avg_esforco,
    COALESCE(r.professors_ranked, 0) AS professors_ranked,
    COALESCE(r.courses_ranked, 0) AS courses_ranked,
    COALESCE(ec.downloads, 0) AS downloads,
    COALESCE(ec.uploads, 0) AS uploads,
    COALESCE(ec.searches, 0) AS searches,
    ROUND(COALESCE(ec.search_results_opened, 0)::NUMERIC / NULLIF(ec.searches, 0), 4) AS search_success_rate,
    ROUND(COALESCE(ec.empty_searches, 0)::NUMERIC / NULLIF(ec.searches, 0), 4) AS empty_search_rate
FROM rating_stats r
FULL OUTER JOIN event_content_stats ec ON r.evaluation_date = ec.event_date
