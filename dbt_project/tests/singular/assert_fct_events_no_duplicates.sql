-- Singular test: fails if fct_events contains duplicate event_id entries (deduplication invariant)
select
    event_id,
    count(*) as occurrence_count
from {{ ref('fct_events') }}
group by event_id
having count(*) > 1
