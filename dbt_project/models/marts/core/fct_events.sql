-- Core atomic event fact table fct_events (grain = 1 row per event tracked)
-- session_id, platform, and app_version are stored as DEGENERATE DIMENSIONS.
with stg_events as (
    select * from {{ ref('stg_analytics_events') }}
),

dim_users as (
    select * from {{ ref('dim_users') }} where is_current = true
),

dim_screens as (
    select * from {{ ref('dim_screens') }}
),

dim_professors as (
    select * from {{ ref('dim_professors') }}
)

select
    abs(hashtext(e.raw_event_id))::bigint as event_sk,
    e.raw_event_id as event_id,
    e.event_date_sk,
    u.user_sk,
    s.screen_sk,
    null::bigint as course_sk,
    p.professor_sk,
    null::bigint as period_sk,
    e.session_id, -- Degenerate dimension (raw UUID, no FK to fct_sessions to avoid circular loading dependency)
    e.platform,   -- Degenerate dimension
    e.app_version, -- Degenerate dimension
    e.event_name,
    e.category,
    e.priority,
    e.schema_version,
    e.event_ts,
    e.payload_json
from stg_events e
left join dim_users u on e.user_id = u.user_id
left join dim_screens s on e.screen_name = s.screen_name
left join dim_professors p on trim(regexp_replace(e.payload_json->>'docente', '\s+', ' ', 'g')) = p.docente_name_clean
