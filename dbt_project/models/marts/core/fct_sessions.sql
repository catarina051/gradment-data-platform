-- Derived session rollup fct_sessions (sessionized from fct_events using session_id)
with session_aggregation as (
    select
        session_id,
        min(event_date_sk) as session_start_date_sk,
        min(user_sk) as user_sk,
        extract(epoch from (max(event_ts) - min(event_ts)))::int as session_duration_seconds,
        count(distinct screen_sk) as screens_viewed_count,
        sum(case when category = 'Errors' then 1 else 0 end) as errors_count,
        max(case when event_name = 'app_launched' then 1 else 0 end)::smallint as is_cold_start
    from {{ ref('fct_events') }}
    group by session_id
)

select
    abs(hashtext(session_id))::bigint as session_sk,
    session_id,
    session_start_date_sk,
    user_sk,
    session_duration_seconds,
    screens_viewed_count,
    errors_count,
    is_cold_start
from session_aggregation
