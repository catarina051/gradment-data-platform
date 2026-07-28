-- Singular test: fails if any rating in fct_ratings has scores outside [1, 5]
select
    rating_id,
    dificuldade,
    esforco
from {{ ref('fct_ratings') }}
where dificuldade < 1 or dificuldade > 5
   or esforco < 1 or esforco > 5
