# Data Catalog: `dim_screens`

## Description
UI screen metadata dimension table for navigation funnel and screen view analytics.

## Primary Key
- **Surrogate Key**: `screen_sk` (BIGINT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `screen_sk` | BIGINT | NO | Primary surrogate key | — |
| `screen_name` | VARCHAR(64) | NO | Snake_case UI screen identifier | — |
| `feature_key` | VARCHAR(64) | NO | High-level feature domain key | — |
| `route_path` | VARCHAR(255) | NO | Client application route path | — |
