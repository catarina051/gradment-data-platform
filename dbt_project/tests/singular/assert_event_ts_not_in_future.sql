-- Singular test: fails if any event in fct_events has a timestamp significantly in the future (> current_timestamp + 5 min)
select
    event_id,
    event_name,
    event_ts
from {{ ref('fct_events') }}
where event_ts > current_timestamp + interval '5 minutes'
