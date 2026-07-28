# Data Catalog: `dim_date`

## Description
Pre-populated calendar date dimension table (integer YYYYMMDD format).

## Primary Key
- **Surrogate Key**: `date_sk` (INT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `date_sk` | INT | NO | Primary surrogate key (YYYYMMDD) | — |
| `full_date` | DATE | NO | Standard calendar date | — |
| `year` | INT | NO | Year number | — |
| `quarter` | INT | NO | Quarter index (1 to 4) | — |
| `month` | INT | NO | Month index (1 to 12) | — |
| `month_name` | VARCHAR(16) | NO | Month full name (e.g. Janeiro) | — |
| `week_of_year` | INT | NO | ISO week number | — |
| `day_of_week` | INT | NO | Day of week (1=Monday, 7=Sunday) | — |
| `is_weekend` | BOOLEAN | NO | Weekend indicator flag | — |
| `is_academic_term` | BOOLEAN | NO | Academic term active flag | — |

## Indexes
- `idx_dim_date_full_date ON dim_date(full_date)`
