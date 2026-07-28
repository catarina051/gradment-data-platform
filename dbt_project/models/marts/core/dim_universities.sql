-- Core dimension model dim_universities
with source_universities as (
    select
        1 as university_id,
        'Universidade Federal de Viçosa' as name,
        'UFV' as acronym,
        'MG' as state
)

select
    abs(hashtext(university_id::text))::bigint as university_sk,
    university_id,
    name,
    acronym,
    state
from source_universities
