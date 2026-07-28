-- Core dimension model dim_academic_periods
with source_periods as (
    select '2026.1' as academic_period, 2026 as year, 1 as semester
    union all
    select '2026.2' as academic_period, 2026 as year, 2 as semester
)

select
    abs(hashtext(academic_period))::bigint as period_sk,
    academic_period,
    year,
    semester
from source_periods
