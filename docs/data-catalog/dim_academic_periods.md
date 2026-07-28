# Data Catalog: `dim_academic_periods`

## Description
Academic semester and term dimension table (e.g. 2025.1, 2025.2, 2026.1).

## Primary Key
- **Surrogate Key**: `period_sk` (BIGINT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `period_sk` | BIGINT | NO | Primary surrogate key | — |
| `academic_period` | VARCHAR(16) | NO | Semester code (e.g. 2025.1) | — |
| `year` | INT | NO | Academic year | — |
| `semester` | INT | NO | Semester index (1 or 2) | — |
