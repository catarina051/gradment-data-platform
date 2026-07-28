-- Daily retention & engagement rollup fct_daily_user_activity
with daily_events as (
    select
        event_date_sk as date_sk,
        user_sk,
        count(distinct session_id) as session_count,
        count(*) as events_count,
        sum(case when event_name in ('discipline_rated', 'professor_rated') then 1 else 0 end) as ratings_submitted_count,
        sum(case when event_name = 'material_downloaded' then 1 else 0 end) as downloads_count,
        sum(case when event_name = 'material_uploaded' then 1 else 0 end) as uploads_count,
        max(case when event_name in ('discipline_rated', 'professor_rated', 'material_uploaded', 'planning_wizard_completed') then 1 else 0 end) as has_completed_core_action
    from {{ ref('fct_events') }}
    group by event_date_sk, user_sk
),

user_univ as (
    select distinct
        user_sk,
        university_sk
    from {{ ref('dim_users') }}
)

select
    abs(hashtext(de.date_sk::text || '-' || de.user_sk::text))::bigint as daily_activity_sk,
    de.date_sk,
    de.user_sk,
    coalesce(uu.university_sk, 1) as university_sk,
    1::smallint as is_active_day,
    de.session_count,
    de.events_count,
    de.ratings_submitted_count,
    de.downloads_count,
    de.uploads_count,
    de.has_completed_core_action::smallint as has_completed_core_action
from daily_events de
left join user_univ uu on de.user_sk = uu.user_sk
