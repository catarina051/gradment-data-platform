-- Specialized academic evaluation fact table fct_ratings
with rating_events as (
    select
        event_id as rating_id,
        event_date_sk as date_sk,
        user_sk,
        course_sk,
        professor_sk,
        period_sk,
        event_ts as rating_ts,
        coalesce((payload_json->>'dificuldade')::smallint, 3) as dificuldade,
        coalesce((payload_json->>'esforco')::smallint, 3) as esforco,
        coalesce((payload_json->>'passou')::smallint, 1) as passou
    from {{ ref('fct_events') }}
    where event_name in ('discipline_rated', 'professor_rated')
)

select
    ('0x' || substring(md5(rating_id), 1, 15))::bit(60)::bigint as rating_sk,
    rating_id,
    date_sk,
    user_sk,
    coalesce(course_sk, 1) as course_sk,
    professor_sk,
    coalesce(period_sk, 1) as period_sk,
    dificuldade,
    esforco,
    passou,
    rating_ts
from rating_events
