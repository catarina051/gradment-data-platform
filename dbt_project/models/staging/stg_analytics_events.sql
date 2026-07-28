-- Staging model extracting raw telemetry events from analytics_events
with source_events as (
    select
        id as raw_event_id,
        event_name,
        category,
        priority,
        schema_version,
        session_id,
        user_id,
        platform,
        app_version,
        screen_name,
        timestamp as event_ts,
        payload as payload_json,
        created_at
    from {{ source('raw_telemetry', 'analytics_events') }}
)

select
    raw_event_id,
    event_name,
    category,
    priority,
    schema_version,
    session_id,
    user_id,
    platform,
    app_version,
    screen_name,
    event_ts,
    payload_json,
    created_at,
    to_char(event_ts, 'YYYYMMDD')::int as event_date_sk
from source_events
