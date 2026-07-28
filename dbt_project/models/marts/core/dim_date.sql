-- Core dimension model dim_date (singular Date Dimension)
with date_spine as (
    select
        datum::date as full_date
    from generate_series(
        '2025-01-01'::date,
        '2027-12-31'::date,
        '1 day'::interval
    ) as datum
)

select
    to_char(full_date, 'YYYYMMDD')::int as date_sk,
    full_date,
    extract(year from full_date)::int as year,
    extract(quarter from full_date)::int as quarter,
    extract(month from full_date)::int as month,
    to_char(full_date, 'TMMonth') as month_name,
    extract(isoyear from full_date)::int as week_of_year,
    extract(isodow from full_date)::int as day_of_week,
    case when extract(isodow from full_date) in (6, 7) then true else false end as is_weekend,
    true as is_academic_term
from date_spine
