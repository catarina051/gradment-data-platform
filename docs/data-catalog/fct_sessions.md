# Data Catalog: `fct_sessions`

## Description
User session rollup derived from `fct_events` via a 30-minute inactivity threshold (grain: 1 row per session).

## Primary Key
- **Surrogate Key**: `session_sk` (BIGINT)
- **Natural Key**: `session_id` (UUID v4)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `session_sk` | BIGINT | NO | Surrogate primary key | — |
| `session_id` | VARCHAR(36) | NO | Degenerate UUID session identifier | — |
| `session_start_date_sk` | INT | NO | Foreign key to date dimension | `dim_date.date_sk` |
| `user_sk` | BIGINT | NO | Foreign key to user dimension | `dim_users.user_sk` |
| `session_duration_seconds` | INT | NO | Total duration in seconds | — |
| `screens_viewed_count` | INT | NO | Total screen navigation events | — |
| `errors_count` | INT | NO | Errors encountered during session | — |
| `is_cold_start` | SMALLINT | NO | Cold start session flag | — |

## Foreign Keys & Indexes
- `idx_fct_sessions_start_date_sk ON fct_sessions(session_start_date_sk)`
- `idx_fct_sessions_user_sk ON fct_sessions(user_sk)`
- `idx_fct_sessions_session_id ON fct_sessions(session_id)`
