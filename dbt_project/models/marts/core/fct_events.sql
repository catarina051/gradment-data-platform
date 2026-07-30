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
),

dim_periods as (
    select * from {{ ref('dim_academic_periods') }}
)

select
    ('0x' || substring(md5(e.raw_event_id), 1, 15))::bit(60)::bigint as event_sk,
    e.raw_event_id as event_id,
    e.event_date_sk,
    u.user_sk,
    s.screen_sk,
    coalesce(
        case when (e.payload_json->>'course_id') is not null 
             then ('0x' || substring(md5((e.payload_json->>'course_id')::text), 1, 15))::bit(60)::bigint 
        end,
        u.course_sk
    ) as course_sk,
    p.professor_sk,
    coalesce(
        case when (e.payload_json->>'ano_periodo') is not null 
             then ('0x' || substring(md5(e.payload_json->>'ano_periodo'), 1, 15))::bit(60)::bigint 
        end,
        ('0x' || substring(md5('2026.1'), 1, 15))::bit(60)::bigint
    ) as period_sk,
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
