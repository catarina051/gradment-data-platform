# Data Catalog: `fct_daily_user_activity`

## Description
Daily engagement & retention rollup per user (grain: 1 row per user per active day). Drives DAU, WAU, MAU, and North Star engagement metrics.

## Primary Key
- **Surrogate Key**: `daily_activity_sk` (BIGINT)
- **Natural Composite Constraint**: `UNIQUE (date_sk, user_sk)`

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `daily_activity_sk` | BIGINT | NO | Surrogate primary key | — |
| `date_sk` | INT | NO | Foreign key to date dimension | `dim_date.date_sk` |
| `user_sk` | BIGINT | NO | Foreign key to user dimension | `dim_users.user_sk` |
| `university_sk` | BIGINT | NO | Foreign key to university dimension | `dim_universities.university_sk` |
| `is_active_day` | SMALLINT | NO | Indicator flag (1 if active, 0 otherwise) | — |
| `session_count` | INT | NO | Total user sessions on date | — |
| `events_count` | INT | NO | Total events triggered on date | — |
| `ratings_submitted_count` | INT | NO | Discipline ratings submitted on date | — |
| `downloads_count` | INT | NO | Document downloads executed on date | — |
| `uploads_count` | INT | NO | Material uploads executed on date | — |
| `has_completed_core_action` | SMALLINT | NO | Core action indicator flag | — |

## Foreign Keys & Indexes
- `idx_fct_daily_activity_date_user ON fct_daily_user_activity(date_sk, user_sk)` *(Composite Index for DAU/Retention)*
- `idx_fct_daily_user_activity_date_sk ON fct_daily_user_activity(date_sk)`
- `idx_fct_daily_user_activity_user_sk ON fct_daily_user_activity(user_sk)`
- `idx_fct_daily_user_activity_university_sk ON fct_daily_user_activity(university_sk)`
