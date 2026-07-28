# Data Catalog: `dim_universities`

## Description
University metadata dimension table for multi-tenant analytical slicing.

## Primary Key
- **Surrogate Key**: `university_sk` (BIGINT)
- **Operational Key**: `university_id` (BIGINT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `university_sk` | BIGINT | NO | Primary surrogate key | — |
| `university_id` | BIGINT | NO | Operational university identifier | — |
| `name` | VARCHAR(255) | NO | Institution name | — |
| `acronym` | VARCHAR(32) | NO | Institution acronym (e.g. UFV) | — |
| `state` | VARCHAR(2) | NO | Brazilian state abbreviation (e.g. MG) | — |
