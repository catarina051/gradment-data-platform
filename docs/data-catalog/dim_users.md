# Data Catalog: `dim_users`

## Description
User profile dimension modeling role and status history over time using Slowly Changing Dimension Type 2 (SCD2).

## Primary Key
- **Surrogate Key**: `user_sk` (BIGINT)
- **Operational Key**: `user_id` (BIGINT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `user_sk` | BIGINT | NO | Surrogate primary key per version snapshot | — |
| `user_id` | BIGINT | NO | Operational user identifier | — |
| `university_sk` | BIGINT | NO | Foreign key to university dimension | `dim_universities.university_sk` |
| `course_sk` | BIGINT | YES | Foreign key to course dimension | `dim_courses.course_sk` |
| `role` | VARCHAR(32) | NO | User role (`Aluno`, `Coordenador`, `Admin`) | — |
| `registration_date` | DATE | NO | Registration date | — |
| `status` | VARCHAR(32) | NO | Operational status (`ativo`, `inativo`, `pendente`) | — |
| `valid_from` | TIMESTAMPTZ | NO | SCD2 effective start timestamp | — |
| `valid_to` | TIMESTAMPTZ | YES | SCD2 effective end timestamp (NULL if current) | — |
| `is_current` | BOOLEAN | NO | Current version indicator flag | — |

## Indexes
- `idx_dim_users_user_id ON dim_users(user_id)`
- `idx_dim_users_university_sk ON dim_users(university_sk)`
- `idx_dim_users_course_sk ON dim_users(course_sk)`
- `idx_dim_users_lookup ON dim_users(user_id, is_current)`
