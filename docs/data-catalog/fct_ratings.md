# Data Catalog: `fct_ratings`

## Description
Specialized domain fact table capturing academic course, discipline, and professor evaluation scores (grain: 1 row per submitted evaluation).

## Primary Key
- **Surrogate Key**: `rating_sk` (BIGINT)
- **Natural Key**: `rating_id` (UUID v4)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `rating_sk` | BIGINT | NO | Surrogate primary key | — |
| `rating_id` | VARCHAR(36) | NO | Natural UUID v4 evaluation identifier | — |
| `date_sk` | INT | NO | Foreign key to date dimension | `dim_date.date_sk` |
| `user_sk` | BIGINT | NO | Foreign key to user dimension | `dim_users.user_sk` |
| `course_sk` | BIGINT | NO | Foreign key to course dimension | `dim_courses.course_sk` |
| `professor_sk` | BIGINT | YES | Foreign key to professor dimension | `dim_professors.professor_sk` |
| `period_sk` | BIGINT | NO | Foreign key to academic period dimension | `dim_academic_periods.period_sk` |
| `dificuldade` | SMALLINT | NO | Difficulty score (1 to 5) | — |
| `esforco` | SMALLINT | NO | Effort score (1 to 5) | — |
| `passou` | SMALLINT | NO | Passing outcome flag (1=yes, 0=no) | — |
| `rating_ts` | TIMESTAMPTZ | NO | Submission UTC timestamp | — |

## Foreign Keys & Indexes
- `idx_fct_ratings_date_sk ON fct_ratings(date_sk)`
- `idx_fct_ratings_user_sk ON fct_ratings(user_sk)`
- `idx_fct_ratings_course_sk ON fct_ratings(course_sk)`
- `idx_fct_ratings_professor_sk ON fct_ratings(professor_sk)`
- `idx_fct_ratings_period_sk ON fct_ratings(period_sk)`
