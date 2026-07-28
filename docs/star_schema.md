# Analytical Database Design — Star Schema Specification

## 1. Overview & Architecture Strategy

This document specifies the **Kimball Star Schema** data warehouse architecture for the **GradMent Data Platform**. The schema is designed to support high-performance analytical queries for product metrics, user engagement tracking, academic evaluations, retention cohorts, and funnel conversions defined in Section 19 of the Master Implementation Plan.

### Key Architectural Principles:
1. **Atomic Event Fact (`fct_events`)**: Retains complete event-level granularity (1 row per event tracked) covering 100% of the 39 catalog events across 12 categories.
2. **Degenerate Session Dimension**: `fct_events` records the raw `session_id` (UUID) as a degenerate dimension rather than a Foreign Key to `fct_sessions`. This avoids circular loading dependencies, as `fct_sessions` is derived downstream from `fct_events` via a 30-minute inactivity cutoff.
3. **Degenerate Device Dimensions**: `platform` and `app_version` are low-cardinality attributes stored directly as degenerate dimensions on `fct_events`, avoiding unnecessary table joins.
4. **SCD Type 2 User Dimension (`dim_users`)**: Implements Slowly Changing Dimension (SCD) Type 2 (`valid_from`, `valid_to`, `is_current`) on `dim_users` (formerly `dim_students`) to track user role changes (e.g., Aluno → Coordenador) over time.
5. **Specialized Fact Rollups (`fct_daily_user_activity`, `fct_ratings`, `fct_sessions`)**: Provide pre-aggregated, measure-rich structures for fast retrieval of North Star metrics, academic rating distributions, and session metrics without scanning billions of raw event records.
6. **Singular Date Dimension (`dim_date`)**: Standardized singular naming convention aligned with Section 5.2 of the Master Plan.

---

## 2. Fact Tables Specification

### 2.1 `fct_events` — Atomic Event Fact Table

- **Description**: Central atomic fact table recording every telemetry and product usage event emitted across the GradMent application.
- **Grain**: 1 row per emitted event.
- **Coverage**: All 39 catalog events across 12 categories (`Auth`, `Navigation`, `Search`, `Ratings`, `Downloads`, `Uploads`, `Planning`, `Favorites`, `Notifications`, `Errors`, `System`, `Admin`).
- **Partitioning**: Monthly declarative partitioning on `event_ts`.
- **Incremental Strategy**: `event_id` unique key constraint guarantees idempotent incremental loads (FR-9).

#### Attributes & Column Definitions:

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `event_sk` | `BIGINT` | No | PK | Surrogate key for the event row. |
| `event_id` | `VARCHAR(36)` | No | Natural Key / Unique | Unique event UUID from envelope. |
| `event_date_sk` | `INT` | No | FK → `dim_date.date_sk` | Date of event emission (`YYYYMMDD`). |
| `user_sk` | `BIGINT` | No | FK → `dim_users.user_sk` | Active surrogate key of emitting user. |
| `screen_sk` | `BIGINT` | Yes | FK → `dim_screens.screen_sk` | Screen where event occurred (if applicable). |
| `course_sk` | `BIGINT` | Yes | FK → `dim_courses.course_sk` | Associated course/discipline (if applicable). |
| `professor_sk` | `BIGINT` | Yes | FK → `dim_professors.professor_sk` | Associated professor/docente (if applicable). |
| `period_sk` | `BIGINT` | Yes | FK → `dim_academic_periods.period_sk` | Academic term (e.g. 2026.1). |
| `session_id` | `VARCHAR(36)` | No | Degenerate Dimension | Raw session UUID (enables downstream session derivation without circular FK). |
| `platform` | `VARCHAR(32)` | No | Degenerate Dimension | Client platform (`web`, `mobile_android`, `mobile_ios`). |
| `app_version` | `VARCHAR(32)` | No | Degenerate Dimension | Client software release version. |
| `event_name` | `VARCHAR(64)` | No | Attribute | Canonical event name (e.g. `discipline_rated`). |
| `category` | `VARCHAR(32)` | No | Attribute | Event category (1 of 12 catalog categories). |
| `priority` | `VARCHAR(16)` | No | Attribute | Event priority (`critical`, `high`, `medium`, `low`). |
| `schema_version` | `VARCHAR(16)` | No | Attribute | Envelope/payload schema version (e.g. `1.0.0`). |
| `event_ts` | `TIMESTAMP WITH TIME ZONE` | No | Attribute | Emitted timestamp in UTC. |
| `payload_json` | `JSONB` / `JSON` | No | Attribute | Untruncated full JSON payload for non-promoted custom fields. |

---

### 2.2 `fct_daily_user_activity` — Retention & Engagement Rollup

- **Description**: Daily user activity summary driving North Star metrics (WAU core action completion) and retention cohorts (D1, D7, D14, D30).
- **Grain**: 1 row per `user_id` per calendar date.
- **Source**: Aggregated daily from `fct_events`.

#### Attributes & Column Definitions:

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `daily_activity_sk` | `BIGINT` | No | PK | Surrogate key for daily rollup record. |
| `date_sk` | `INT` | No | FK → `dim_date.date_sk` | Calendar date of activity. |
| `user_sk` | `BIGINT` | No | FK → `dim_users.user_sk` | User surrogate key. |
| `university_sk` | `BIGINT` | No | FK → `dim_universities.university_sk` | User's primary university (denormalized for fast slicing). |
| `is_active_day` | `SMALLINT` | No | Measure | 1 if user logged at least 1 event on this date; 0 otherwise. |
| `session_count` | `INT` | No | Measure | Distinct count of `session_id` instances on date. |
| `events_count` | `INT` | No | Measure | Total event volume generated by user on date. |
| `ratings_submitted_count` | `INT` | No | Measure | Count of academic rating events (`discipline_rated`, `professor_rated`). |
| `downloads_count` | `INT` | No | Measure | Count of material download events (`material_downloaded`). |
| `uploads_count` | `INT` | No | Measure | Count of material upload events (`material_uploaded`). |
| `has_completed_core_action` | `SMALLINT` | No | Measure | 1 if user performed rating, upload, or planning completion; 0 otherwise. |

---

### 2.3 `fct_ratings` — Academic Evaluation Specialized Fact

- **Description**: Structured domain fact table isolating student ratings for courses and professors.
- **Grain**: 1 evaluation transaction.
- **Source**: Extracted from `fct_events` for `discipline_rated` and `professor_rated` events.

#### Attributes & Column Definitions:

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `rating_sk` | `BIGINT` | No | PK | Surrogate key for rating transaction. |
| `rating_id` | `VARCHAR(36)` | No | Natural Key / Unique | Unique event UUID or rating record ID. |
| `date_sk` | `INT` | No | FK → `dim_date.date_sk` | Evaluation date. |
| `user_sk` | `BIGINT` | No | FK → `dim_users.user_sk` | Evaluating user. |
| `course_sk` | `BIGINT` | No | FK → `dim_courses.course_sk` | Evaluated course/discipline. |
| `professor_sk` | `BIGINT` | Yes | FK → `dim_professors.professor_sk` | Evaluated professor (nullable if course-only rating). |
| `period_sk` | `BIGINT` | No | FK → `dim_academic_periods.period_sk` | Academic term evaluated. |
| `dificuldade` | `SMALLINT` | No | Measure | Perceived difficulty score (1 to 5). |
| `esforco` | `SMALLINT` | No | Measure | Effort level required score (1 to 5). |
| `passou` | `SMALLINT` | No | Measure | Passing status indicator (1 = passed, 0 = failed/did not finish). |
| `rating_ts` | `TIMESTAMP WITH TIME ZONE` | No | Attribute | Exact timestamp evaluation was logged. |

---

### 2.4 `fct_sessions` — Session Rollup

- **Description**: Session summary table derived from raw event streams using a 30-minute inactivity threshold.
- **Grain**: 1 user session (`session_id`).
- **Source**: Aggregated from `fct_events` grouped by `session_id`.

#### Attributes & Column Definitions:

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `session_sk` | `BIGINT` | No | PK | Minted surrogate key for the derived session. |
| `session_id` | `VARCHAR(36)` | No | Natural Key / Unique | Session UUID (matches `fct_events.session_id`). |
| `session_start_date_sk` | `INT` | No | FK → `dim_date.date_sk` | Calendar date session started. |
| `user_sk` | `BIGINT` | No | FK → `dim_users.user_sk` | User associated with session. |
| `session_duration_seconds` | `INT` | No | Measure | Total session duration (`MAX(event_ts) - MIN(event_ts)` in seconds). |
| `screens_viewed_count` | `INT` | No | Measure | Distinct screens visited within session. |
| `errors_count` | `INT` | No | Measure | Total error events encountered in session. |
| `is_cold_start` | `SMALLINT` | No | Measure | 1 if session started with application launch; 0 otherwise. |

---

## 3. Dimension Tables Specification

### 3.1 `dim_users` — User Dimension (SCD Type 2)

- **Description**: User profile dimension tracking platform roles and statuses with full history via SCD Type 2.
- **Grain**: 1 row per user state change version.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `user_sk` | `BIGINT` | No | PK | Surrogate key for user state snapshot. |
| `user_id` | `BIGINT` | No | Natural Key | Operational user identifier from production `usuarios`. |
| `university_sk` | `BIGINT` | No | FK → `dim_universities.university_sk` | Enrolled university. |
| `course_sk` | `BIGINT` | Yes | FK → `dim_courses.course_sk` | Enrolled primary course. |
| `role` | `VARCHAR(32)` | No | Attribute | User role (`Aluno`, `Coordenador`, `Admin`). |
| `registration_date` | `DATE` | No | Attribute | Account creation date in GradMent. |
| `status` | `VARCHAR(32)` | No | Attribute | Account status (`ativo`, `inativo`, `pendente`). |
| `valid_from` | `TIMESTAMP WITH TIME ZONE` | No | SCD2 Attribute | Snapshot start validity timestamp. |
| `valid_to` | `TIMESTAMP WITH TIME ZONE` | Yes | SCD2 Attribute | Snapshot end validity timestamp (`NULL` if current). |
| `is_current` | `BOOLEAN` | No | SCD2 Attribute | `TRUE` if currently active snapshot version. |

---

### 3.2 `dim_professors` — Professor Dimension

- **Description**: Faculty dimension supporting fuzzy matching and cleaning of professor name variations from operational listings.
- **Scope Note**: `department` and `university_key` are intentionally omitted for Phase 3 due to GradMent's current single-university operational scope.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `professor_sk` | `BIGINT` | No | PK | Surrogate key for professor entity. |
| `docente_name_clean` | `VARCHAR(255)` | No | Attribute | Normalized clean professor name. |
| `original_docente_string` | `VARCHAR(255)` | No | Attribute | Original raw name string from operational DB. |
| `raw_name_variations_json` | `JSONB` / `JSON` | No | Attribute | Array of name aliases and variations for resolution matching. |

---

### 3.3 `dim_courses` — Course & Discipline Dimension

- **Description**: Academic discipline and course curriculum metadata.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `course_sk` | `BIGINT` | No | PK | Surrogate key for course/discipline. |
| `discipline_id` | `BIGINT` | No | Natural Key | Operational ID from `curriculo_disciplinas`. |
| `codigo_disciplina` | `VARCHAR(32)` | No | Attribute | Course code (e.g. `MAT101`, `FIS202`). |
| `nome_disciplina` | `VARCHAR(255)` | No | Attribute | Official discipline name. |
| `creditos` | `INT` | No | Attribute | Academic credit hours value. |
| `ch_total` | `INT` | No | Attribute | Total workload hours. |

---

### 3.4 `dim_universities` — Institution Dimension

- **Description**: University metadata for multi-tenant analytical slicing.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `university_sk` | `BIGINT` | No | PK | Surrogate key for university entity. |
| `university_id` | `BIGINT` | No | Natural Key | Operational university identifier. |
| `name` | `VARCHAR(255)` | No | Attribute | Full university name. |
| `acronym` | `VARCHAR(32)` | No | Attribute | Short institution acronym (e.g. `UFV`, `UFMG`). |
| `state` | `VARCHAR(2)` | No | Attribute | Federative state code (e.g. `MG`). |

---

### 3.5 `dim_academic_periods` — Academic Term Dimension

- **Description**: Semester and academic term calendar mapping.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `period_sk` | `BIGINT` | No | PK | Surrogate key for academic term. |
| `academic_period` | `VARCHAR(16)` | No | Attribute | Term label (e.g. `2026.1`, `2026.2`). |
| `year` | `INT` | No | Attribute | Calendar year. |
| `semester` | `INT` | No | Attribute | Term number (`1` or `2`). |

---

### 3.6 `dim_date` — Date Dimension (Singular)

- **Description**: Pre-populated calendar date dimension for time-series analysis and cohort reporting.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `date_sk` | `INT` | No | PK | Integer key formatted `YYYYMMDD`. |
| `full_date` | `DATE` | No | Natural Key | Date value (`YYYY-MM-DD`). |
| `year` | `INT` | No | Attribute | Calendar year. |
| `quarter` | `INT` | No | Attribute | Quarter number (1 to 4). |
| `month` | `INT` | No | Attribute | Month number (1 to 12). |
| `month_name` | `VARCHAR(16)` | No | Attribute | Full month name (e.g. `Janeiro`). |
| `week_of_year` | `INT` | No | Attribute | ISO week number. |
| `day_of_week` | `INT` | No | Attribute | Day of week (1 = Monday, 7 = Sunday). |
| `is_weekend` | `BOOLEAN` | No | Attribute | `TRUE` if Saturday or Sunday. |
| `is_academic_term` | `BOOLEAN` | No | Attribute | `TRUE` if falls within standard academic term dates. |

---

### 3.7 `dim_screens` — Screen & Route Dimension

- **Description**: UI screen metadata for screen view and navigation funnel analytics.

| Column Name | Data Type | Nullable | Key Type | Description |
|---|---|---|---|---|
| `screen_sk` | `BIGINT` | No | PK | Surrogate key for application screen. |
| `screen_name` | `VARCHAR(64)` | No | Natural Key | Canonical screen identifier (e.g. `disciplinas_search`). |
| `feature_key` | `VARCHAR(64)` | No | Attribute | High-level feature group (e.g. `search`, `planning`). |
| `route_path` | `VARCHAR(255)` | No | Attribute | Application URL / URI route pattern. |

---

## 4. Reconciliations & Decisions Log

1. **Resolution of Circular Foreign Key**: `fct_events` records `session_id` as a degenerate dimension. `fct_sessions` aggregates events downstream by `session_id` and mints `session_sk`.
2. **Category Scope**: 12 categories confirmed (`Auth`, `Navigation`, `Search`, `Ratings`, `Downloads`, `Uploads`, `Planning`, `Favorites`, `Notifications`, `Errors`, `System`, `Admin`). `feature_flag_evaluated` is categorized under `System`.
3. **Singular Naming**: Dimension table for dates is named `dim_date`.
4. **Scope Boundaries**: `dim_professors` excludes `department` and `university_key` during Phase 3 due to single-university operations.
5. **No `dim_devices`**: Device parameters (`platform`, `app_version`) are stored directly as degenerate dimensions on `fct_events`.
