-- Core dimension model dim_courses
with source_courses as (
    select
        101 as discipline_id,
        'MAT101' as codigo_disciplina,
        'Cálculo I' as nome_disciplina,
        4 as creditos,
        60 as ch_total
)

select
    abs(hashtext(discipline_id::text))::bigint as course_sk,
    discipline_id,
    codigo_disciplina,
    nome_disciplina,
    creditos,
    ch_total
from source_courses
