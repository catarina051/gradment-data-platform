# Data Catalog: `dim_professors`

## Description
Faculty dimension supporting fuzzy name resolution and variations (department and university keys intentionally deferred).

## Primary Key
- **Surrogate Key**: `professor_sk` (BIGINT)

## Columns
| Column Name | Data Type | Nullable | Description | References |
|---|---|---|---|---|
| `professor_sk` | BIGINT | NO | Primary surrogate key | — |
| `docente_name_clean` | VARCHAR(255) | NO | Standardized cleaned professor name | — |
| `original_docente_string` | VARCHAR(255) | NO | Raw string as reported in operational source | — |
| `raw_name_variations_json` | JSONB | NO | Array of observed string variations | — |
