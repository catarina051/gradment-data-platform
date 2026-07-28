{% snapshot dim_users_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='user_id',
      strategy='timestamp',
      updated_at='registration_date',
    )
}}

select
    user_id,
    university_id,
    course_id,
    role,
    registration_date,
    status
from {{ ref('stg_operational_tables') }}

{% endsnapshot %}
