-- Core dimension model dim_users (SCD Type 2 snapshot backing)
with user_snapshots as (
    select
        dbt_scd_id as user_sk_str,
        user_id,
        university_id,
        course_id,
        role,
        registration_date,
        status,
        dbt_valid_from as valid_from,
        dbt_valid_to as valid_to,
        case when dbt_valid_to is null then true else false end as is_current
    from {{ ref('dim_users_snapshot') }}
)

select
    ('0x' || substring(md5(user_sk_str), 1, 15))::bit(60)::bigint as user_sk,
    user_id,
    ('0x' || substring(md5(university_id::text), 1, 15))::bit(60)::bigint as university_sk,
    case when course_id is not null then ('0x' || substring(md5(course_id::text), 1, 15))::bit(60)::bigint else null end as course_sk,
    role,
    registration_date,
    status,
    valid_from,
    valid_to,
    is_current
from user_snapshots
