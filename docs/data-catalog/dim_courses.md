# Data Catalog: `dim_courses`

## Description
Academic course and discipline metadata dimension table.

## Primary Key
- **Surrogate Key**: `course_sk` (BIGINT)
- **Operational Key**: `discipline_id` (BIGINT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `course_sk` | BIGINT | NO | Primary surrogate key | — |
| `discipline_id` | BIGINT | NO | Operational discipline identifier | — |
| `codigo_disciplina` | VARCHAR(32) | NO | Course code (e.g. MAT101) | — |
| `nome_disciplina` | VARCHAR(255) | NO | Course name (e.g. Cálculo I) | — |
| `creditos` | INT | NO | Academic credits count | — |
| `ch_total` | INT | NO | Total workload hours | — |
