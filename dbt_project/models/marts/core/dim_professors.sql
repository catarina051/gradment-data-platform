-- Core dimension model dim_professors
with raw_professors as (
    select distinct
        payload_json->>'docente' as original_docente_string,
        trim(regexp_replace(payload_json->>'docente', '\s+', ' ', 'g')) as docente_name_clean
    from {{ ref('stg_analytics_events') }}
    where payload_json->>'docente' is not null
)

select
    abs(hashtext(docente_name_clean))::bigint as professor_sk,
    docente_name_clean,
    original_docente_string,
    jsonb_build_array(original_docente_string) as raw_name_variations_json
from raw_professors
