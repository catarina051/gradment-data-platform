-- Core dimension model dim_screens
with raw_screens as (
    select distinct
        screen_name,
        category as feature_key,
        '/' || replace(screen_name, '_', '/') as route_path
    from {{ ref('stg_analytics_events') }}
    where screen_name is not null
)

select
    ('0x' || substring(md5(screen_name), 1, 15))::bit(60)::bigint as screen_sk,
    screen_name,
    feature_key,
    route_path
from raw_screens
