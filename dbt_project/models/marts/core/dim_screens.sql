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
    abs(hashtext(screen_name))::bigint as screen_sk,
    screen_name,
    feature_key,
    route_path
from raw_screens
