-- =============================================================================
-- GradMent Data Platform — Star Schema DDL Specification
-- Section 5.2 & Phase 3 Analytical Database Design
-- Supported Dialect: ANSI SQL / PostgreSQL Compatible
-- =============================================================================

-- Clean existing structures if initializing schema
DROP TABLE IF EXISTS fct_events CASCADE;
DROP TABLE IF EXISTS fct_daily_user_activity CASCADE;
DROP TABLE IF EXISTS fct_ratings CASCADE;
DROP TABLE IF EXISTS fct_sessions CASCADE;
DROP TABLE IF EXISTS dim_users CASCADE;
DROP TABLE IF EXISTS dim_professors CASCADE;
DROP TABLE IF EXISTS dim_courses CASCADE;
DROP TABLE IF EXISTS dim_universities CASCADE;
DROP TABLE IF EXISTS dim_academic_periods CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_screens CASCADE;

-- =============================================================================
-- 1. DIMENSION TABLES
-- =============================================================================

-- 1.1 dim_universities (Institution Metadata)
CREATE TABLE dim_universities (
    university_sk BIGINT PRIMARY KEY,
    university_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    acronym VARCHAR(32) NOT NULL,
    state VARCHAR(2) NOT NULL
);

COMMENT ON TABLE dim_universities IS 'University metadata for multi-tenant analytical slicing.';
COMMENT ON COLUMN dim_universities.university_sk IS 'Surrogate key for university entity.';
COMMENT ON COLUMN dim_universities.university_id IS 'Operational university identifier.';

-- 1.2 dim_courses (Discipline & Curriculum Metadata)
CREATE TABLE dim_courses (
    course_sk BIGINT PRIMARY KEY,
    discipline_id BIGINT NOT NULL UNIQUE,
    codigo_disciplina VARCHAR(32) NOT NULL,
    nome_disciplina VARCHAR(255) NOT NULL,
    creditos INT NOT NULL DEFAULT 0,
    ch_total INT NOT NULL DEFAULT 0
);

COMMENT ON TABLE dim_courses IS 'Academic discipline and course curriculum metadata.';
COMMENT ON COLUMN dim_courses.course_sk IS 'Surrogate key for course/discipline.';

-- 1.3 dim_users (User Profiles — SCD Type 2)
CREATE TABLE dim_users (
    user_sk BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    university_sk BIGINT NOT NULL REFERENCES dim_universities(university_sk),
    course_sk BIGINT REFERENCES dim_courses(course_sk),
    role VARCHAR(32) NOT NULL,
    registration_date DATE NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ativo',
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_to TIMESTAMP WITH TIME ZONE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_dim_users_user_id ON dim_users(user_id);
CREATE INDEX idx_dim_users_university_sk ON dim_users(university_sk);
CREATE INDEX idx_dim_users_course_sk ON dim_users(course_sk);
CREATE INDEX idx_dim_users_lookup ON dim_users(user_id, is_current);

COMMENT ON TABLE dim_users IS 'User dimension tracking role and status history via SCD Type 2.';
COMMENT ON COLUMN dim_users.user_sk IS 'Surrogate key for user state snapshot version.';

-- 1.4 dim_professors (Faculty Dimension)
CREATE TABLE dim_professors (
    professor_sk BIGINT PRIMARY KEY,
    docente_name_clean VARCHAR(255) NOT NULL,
    original_docente_string VARCHAR(255) NOT NULL,
    raw_name_variations_json JSONB NOT NULL DEFAULT '[]'::jsonb
);

COMMENT ON TABLE dim_professors IS 'Faculty dimension supporting fuzzy name resolution. Department/university_key intentionally deferred.';

-- 1.5 dim_academic_periods (Academic Term Dimension)
CREATE TABLE dim_academic_periods (
    period_sk BIGINT PRIMARY KEY,
    academic_period VARCHAR(16) NOT NULL UNIQUE,
    year INT NOT NULL,
    semester INT NOT NULL
);

COMMENT ON TABLE dim_academic_periods IS 'Semester and academic term calendar mapping.';

-- 1.6 dim_date (Singular Date Dimension)
CREATE TABLE dim_date (
    date_sk INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(16) NOT NULL,
    week_of_year INT NOT NULL,
    day_of_week INT NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    is_academic_term BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_dim_date_full_date ON dim_date(full_date);

COMMENT ON TABLE dim_date IS 'Pre-populated calendar date dimension (YYYYMMDD).';

-- 1.7 dim_screens (UI Screen & Navigation Dimension)
CREATE TABLE dim_screens (
    screen_sk BIGINT PRIMARY KEY,
    screen_name VARCHAR(64) NOT NULL UNIQUE,
    feature_key VARCHAR(64) NOT NULL,
    route_path VARCHAR(255) NOT NULL
);

COMMENT ON TABLE dim_screens IS 'UI screen metadata for navigation funnel analytics.';

-- =============================================================================
-- 2. FACT TABLES
-- =============================================================================

-- 2.1 fct_events (Atomic Event Fact Table)
-- Note: session_id is stored as a DEGENERATE DIMENSION (raw UUID, no FK to fct_sessions)
-- to avoid circular loading dependencies during session derivation.
CREATE TABLE fct_events (
    event_sk BIGINT NOT NULL,
    event_id VARCHAR(36) NOT NULL,
    event_date_sk INT NOT NULL REFERENCES dim_date(date_sk),
    user_sk BIGINT NOT NULL REFERENCES dim_users(user_sk),
    screen_sk BIGINT REFERENCES dim_screens(screen_sk),
    course_sk BIGINT REFERENCES dim_courses(course_sk),
    professor_sk BIGINT REFERENCES dim_professors(professor_sk),
    period_sk BIGINT REFERENCES dim_academic_periods(period_sk),
    session_id VARCHAR(36) NOT NULL,
    platform VARCHAR(32) NOT NULL,
    app_version VARCHAR(32) NOT NULL,
    event_name VARCHAR(64) NOT NULL,
    category VARCHAR(32) NOT NULL,
    priority VARCHAR(16) NOT NULL,
    schema_version VARCHAR(16) NOT NULL,
    event_ts TIMESTAMP WITH TIME ZONE NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (event_sk, event_ts),
    CONSTRAINT uq_fct_events_id_ts UNIQUE (event_id, event_ts)
) PARTITION BY RANGE (event_ts);

-- Declarative Monthly Partitions
CREATE TABLE fct_events_y2026m01 PARTITION OF fct_events
    FOR VALUES FROM ('2026-01-01 00:00:00+00') TO ('2026-02-01 00:00:00+00');

CREATE TABLE fct_events_y2026m02 PARTITION OF fct_events
    FOR VALUES FROM ('2026-02-01 00:00:00+00') TO ('2026-03-01 00:00:00+00');

CREATE TABLE fct_events_y2026m03 PARTITION OF fct_events
    FOR VALUES FROM ('2026-03-01 00:00:00+00') TO ('2026-04-01 00:00:00+00');

CREATE TABLE fct_events_default PARTITION OF fct_events DEFAULT;

CREATE INDEX idx_fct_events_event_date_sk ON fct_events(event_date_sk);
CREATE INDEX idx_fct_events_user_sk ON fct_events(user_sk);
CREATE INDEX idx_fct_events_screen_sk ON fct_events(screen_sk);
CREATE INDEX idx_fct_events_course_sk ON fct_events(course_sk);
CREATE INDEX idx_fct_events_professor_sk ON fct_events(professor_sk);
CREATE INDEX idx_fct_events_period_sk ON fct_events(period_sk);
CREATE INDEX idx_fct_events_session_id ON fct_events(session_id);
CREATE INDEX idx_fct_events_event_ts ON fct_events(event_ts);
CREATE INDEX idx_fct_events_name_category ON fct_events(category, event_name);

COMMENT ON TABLE fct_events IS 'Central atomic event fact table (grain = 1 row per event). Covers all 39 catalog events.';
COMMENT ON COLUMN fct_events.session_id IS 'Degenerate dimension for session ID. Plain column without FK constraint to prevent circular dependency with fct_sessions.';
COMMENT ON COLUMN fct_events.platform IS 'Degenerate dimension for client platform (web/mobile).';
COMMENT ON COLUMN fct_events.app_version IS 'Degenerate dimension for client application release version.';

-- 2.2 fct_daily_user_activity (Daily Retention & Engagement Rollup)
CREATE TABLE fct_daily_user_activity (
    daily_activity_sk BIGINT PRIMARY KEY,
    date_sk INT NOT NULL REFERENCES dim_date(date_sk),
    user_sk BIGINT NOT NULL REFERENCES dim_users(user_sk),
    university_sk BIGINT NOT NULL REFERENCES dim_universities(university_sk),
    is_active_day SMALLINT NOT NULL DEFAULT 1,
    session_count INT NOT NULL DEFAULT 0,
    events_count INT NOT NULL DEFAULT 0,
    ratings_submitted_count INT NOT NULL DEFAULT 0,
    downloads_count INT NOT NULL DEFAULT 0,
    uploads_count INT NOT NULL DEFAULT 0,
    has_completed_core_action SMALLINT NOT NULL DEFAULT 0,
    CONSTRAINT uq_daily_user_activity UNIQUE (date_sk, user_sk)
);

CREATE INDEX idx_fct_daily_user_activity_date_sk ON fct_daily_user_activity(date_sk);
CREATE INDEX idx_fct_daily_user_activity_user_sk ON fct_daily_user_activity(user_sk);
CREATE INDEX idx_fct_daily_user_activity_university_sk ON fct_daily_user_activity(university_sk);

COMMENT ON TABLE fct_daily_user_activity IS 'Daily engagement rollup per user. Drives WAU/MAU and North Star metric.';

-- 2.3 fct_ratings (Academic Evaluation Specialized Fact Table)
CREATE TABLE fct_ratings (
    rating_sk BIGINT PRIMARY KEY,
    rating_id VARCHAR(36) NOT NULL UNIQUE,
    date_sk INT NOT NULL REFERENCES dim_date(date_sk),
    user_sk BIGINT NOT NULL REFERENCES dim_users(user_sk),
    course_sk BIGINT NOT NULL REFERENCES dim_courses(course_sk),
    professor_sk BIGINT REFERENCES dim_professors(professor_sk),
    period_sk BIGINT NOT NULL REFERENCES dim_academic_periods(period_sk),
    dificuldade SMALLINT NOT NULL,
    esforco SMALLINT NOT NULL,
    passou SMALLINT NOT NULL DEFAULT 1,
    rating_ts TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_fct_ratings_date_sk ON fct_ratings(date_sk);
CREATE INDEX idx_fct_ratings_user_sk ON fct_ratings(user_sk);
CREATE INDEX idx_fct_ratings_course_sk ON fct_ratings(course_sk);
CREATE INDEX idx_fct_ratings_professor_sk ON fct_ratings(professor_sk);
CREATE INDEX idx_fct_ratings_period_sk ON fct_ratings(period_sk);

COMMENT ON TABLE fct_ratings IS 'Specialized domain fact for academic course and professor evaluations.';

-- 2.4 fct_sessions (Derived User Sessions Rollup)
CREATE TABLE fct_sessions (
    session_sk BIGINT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL UNIQUE,
    session_start_date_sk INT NOT NULL REFERENCES dim_date(date_sk),
    user_sk BIGINT NOT NULL REFERENCES dim_users(user_sk),
    session_duration_seconds INT NOT NULL DEFAULT 0,
    screens_viewed_count INT NOT NULL DEFAULT 0,
    errors_count INT NOT NULL DEFAULT 0,
    is_cold_start SMALLINT NOT NULL DEFAULT 0
);

CREATE INDEX idx_fct_sessions_start_date_sk ON fct_sessions(session_start_date_sk);
CREATE INDEX idx_fct_sessions_user_sk ON fct_sessions(user_sk);
CREATE INDEX idx_fct_sessions_session_id ON fct_sessions(session_id);

COMMENT ON TABLE fct_sessions IS 'Session rollup derived from fct_events via 30-minute inactivity threshold.';
