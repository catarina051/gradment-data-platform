-- Staging model typed over GradMent operational database tables (usuarios, etc.)
with stg_usuarios as (
    select
        id_usuario as user_id,
        id_universidade as university_id,
        id_curso as course_id,
        perfil as role,
        data_cadastro as registration_date,
        status
    from {{ source('operational_db', 'usuarios') }}
)

select
    u.user_id,
    u.university_id,
    u.course_id,
    u.role,
    u.registration_date,
    u.status
from stg_usuarios u
