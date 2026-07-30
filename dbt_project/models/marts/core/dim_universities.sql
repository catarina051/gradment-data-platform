-- Core dimension model dim_universities
with source_universities as (
    select
        university_id,
        case
            when university_id = 1 then 'Universidade Federal de Viçosa'
            else 'Universidade ' || university_id::text
        end as name,
        case
            when university_id = 1 then 'UFV'
            else 'UNI' || university_id::text
        end as acronym,
        'MG' as state
    from {{ ref('stg_operational_tables') }}
    group by university_id
)

select
    ('0x' || substring(md5(university_id::text), 1, 15))::bit(60)::bigint as university_sk,
    university_id,
    name,
    acronym,
    state
from source_universities
