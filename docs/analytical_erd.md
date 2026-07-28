# Analytical Star Schema ERD

This document presents the visual **Entity-Relationship Diagram (ERD)** for the **GradMent Data Platform** analytical data warehouse, designed according to Kimball star schema methodology.

> [!IMPORTANT]
> **Degenerate Dimension Note**: `fct_events` records `session_id` as a degenerate attribute (plain UUID string) without a foreign key constraint to `fct_sessions`. `fct_sessions` is populated downstream by grouping `fct_events` by `session_id`.

```mermaid
erDiagram
    dim_date {
        int date_sk PK
        date full_date UK
        int year
        int quarter
        int month
        string month_name
        int week_of_year
        int day_of_week
        boolean is_weekend
        boolean is_academic_term
    }

    dim_universities {
        bigint university_sk PK
        bigint university_id UK
        string name
        string acronym
        string state
    }

    dim_courses {
        bigint course_sk PK
        bigint discipline_id UK
        string codigo_disciplina
        string nome_disciplina
        int creditos
        int ch_total
    }

    dim_professors {
        bigint professor_sk PK
        string docente_name_clean
        string original_docente_string
        jsonb raw_name_variations_json
    }

    dim_academic_periods {
        bigint period_sk PK
        string academic_period UK
        int year
        int semester
    }

    dim_screens {
        bigint screen_sk PK
        string screen_name UK
        string feature_key
        string route_path
    }

    dim_users {
        bigint user_sk PK
        bigint user_id
        bigint university_sk FK
        bigint course_sk FK
        string role
        date registration_date
        string status
        timestamp valid_from
        timestamp valid_to
        boolean is_current
    }

    fct_events {
        bigint event_sk PK
        string event_id UK
        int event_date_sk FK
        bigint user_sk FK
        bigint screen_sk FK
        bigint course_sk FK
        bigint professor_sk FK
        bigint period_sk FK
        string session_id "Degenerate Dim"
        string platform "Degenerate Dim"
        string app_version "Degenerate Dim"
        string event_name
        string category
        string priority
        string schema_version
        timestamp event_ts
        jsonb payload_json
    }

    fct_daily_user_activity {
        bigint daily_activity_sk PK
        int date_sk FK
        bigint user_sk FK
        bigint university_sk FK
        smallint is_active_day
        int session_count
        int events_count
        int ratings_submitted_count
        int downloads_count
        int uploads_count
        smallint has_completed_core_action
    }

    fct_ratings {
        bigint rating_sk PK
        string rating_id UK
        int date_sk FK
        bigint user_sk FK
        bigint course_sk FK
        bigint professor_sk FK
        bigint period_sk FK
        smallint dificuldade
        smallint esforco
        smallint passou
        timestamp rating_ts
    }

    fct_sessions {
        bigint session_sk PK
        string session_id UK
        int session_start_date_sk FK
        bigint user_sk FK
        int session_duration_seconds
        int screens_viewed_count
        int errors_count
        smallint is_cold_start
    }

    dim_universities ||--o{ dim_users : "enrolls"
    dim_courses ||--o{ dim_users : "studies"
    dim_date ||--o{ fct_events : "emitted on"
    dim_users ||--o{ fct_events : "emits"
    dim_screens ||--o{ fct_events : "occurs on"
    dim_courses ||--o{ fct_events : "relates to"
    dim_professors ||--o{ fct_events : "relates to"
    dim_academic_periods ||--o{ fct_events : "during"

    dim_date ||--o{ fct_daily_user_activity : "summarizes on"
    dim_users ||--o{ fct_daily_user_activity : "performs activity"
    dim_universities ||--o{ fct_daily_user_activity : "denormalized slice"

    dim_date ||--o{ fct_ratings : "evaluated on"
    dim_users ||--o{ fct_ratings : "evaluates"
    dim_courses ||--o{ fct_ratings : "rated"
    dim_professors ||--o{ fct_ratings : "rated"
    dim_academic_periods ||--o{ fct_ratings : "evaluated during"

    dim_date ||--o{ fct_sessions : "starts on"
    dim_users ||--o{ fct_sessions : "conducts"
```

## Dimensional Structure Summary

- **Atomic Fact**: `fct_events` (1 row per event tracked).
- **Domain Facts**: `fct_ratings` (academic ratings), `fct_sessions` (derived user sessions).
- **Rollup Fact**: `fct_daily_user_activity` (daily user engagement & retention).
- **Dimensions**: `dim_users` (SCD2), `dim_professors`, `dim_courses`, `dim_universities`, `dim_academic_periods`, `dim_date`, `dim_screens`.
