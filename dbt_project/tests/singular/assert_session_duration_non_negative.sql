-- Singular test: fails if any session in fct_sessions has a negative duration
select
    session_id,
    session_duration_seconds
from {{ ref('fct_sessions') }}
where session_duration_seconds < 0
