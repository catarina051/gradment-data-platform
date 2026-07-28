# Data Catalog: `fct_events`

## Description
Atomic event fact table tracking 100% of all telemetry events emitted across the GradMent Data Platform (grain: 1 row per event tracked). Partitioned natively by range on `event_ts` (monthly child partitions).

## Primary Key & Incremental Strategy
- **Surrogate Key**: `event_sk` (BIGINT)
- **Natural Key**: `event_id` (UUID v4)
- **Incremental Strategy**: `delete+insert` on `unique_key = 'event_id'`

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `event_sk` | BIGINT | NO | Surrogate primary key generated via hash | — |
| `event_id` | VARCHAR(36) | NO | Natural UUID v4 event identifier | — |
| `event_date_sk` | INT | NO | Foreign key to date dimension | `dim_date.date_sk` |
| `user_sk` | BIGINT | NO | Foreign key to user dimension | `dim_users.user_sk` |
| `session_id` | VARCHAR(36) | NO | Degenerate dimension for session grouping | — |
| `platform` | VARCHAR(32) | NO | Client platform (`web`, `mobile`) | — |
| `app_version` | VARCHAR(32) | NO | Client application version | — |
| `screen_sk` | BIGINT | YES | Foreign key to UI screen dimension | `dim_screens.screen_sk` |
| `course_sk` | BIGINT | YES | Foreign key to course dimension | `dim_courses.course_sk` |
| `professor_sk` | BIGINT | YES | Foreign key to professor dimension | `dim_professors.professor_sk` |
| `period_sk` | BIGINT | YES | Foreign key to academic period dimension | `dim_academic_periods.period_sk` |
| `event_name` | VARCHAR(64) | NO | Snake_case event identifier | — |
| `category` | VARCHAR(32) | NO | Event category (1 of 12 catalog categories) | — |
| `priority` | VARCHAR(16) | NO | Priority level (`Critical`, `High`, `Medium`, `Low`) | — |
| `schema_version` | VARCHAR(16) | NO | Event payload schema version | — |
| `event_ts` | TIMESTAMPTZ | NO | Event UTC timestamp (partition key) | — |
| `payload_json` | JSONB | NO | Flexible domain payload attribute map | — |

## Foreign Keys & Indexes
- `idx_fct_events_event_date_sk ON fct_events(event_date_sk)`
- `idx_fct_events_user_sk ON fct_events(user_sk)`
- `idx_fct_events_screen_sk ON fct_events(screen_sk)`
- `idx_fct_events_course_sk ON fct_events(course_sk)`
- `idx_fct_events_professor_sk ON fct_events(professor_sk)`
- `idx_fct_events_period_sk ON fct_events(period_sk)`
