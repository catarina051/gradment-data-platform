-- Staging model extracting curriculo_disciplinas
with source_disciplinas as (
    select
        id_disciplina as discipline_id,
        codigo_disciplina,
        nome_disciplina,
        creditos,
        ch_total
    from {{ source('operational_db', 'curriculo_disciplinas') }}
)

select
    discipline_id,
    codigo_disciplina,
    nome_disciplina,
    creditos,
    ch_total
from source_disciplinas
