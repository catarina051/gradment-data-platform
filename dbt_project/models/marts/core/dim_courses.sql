-- Core dimension model dim_courses
with source_courses as (
    select
        discipline_id,
        codigo_disciplina,
        nome_disciplina,
        creditos,
        ch_total
    from {{ ref('stg_curriculo_disciplinas') }}
)

select
    ('0x' || substring(md5(discipline_id::text), 1, 15))::bit(60)::bigint as course_sk,
    discipline_id,
    codigo_disciplina,
    nome_disciplina,
    creditos,
    ch_total
from source_courses
