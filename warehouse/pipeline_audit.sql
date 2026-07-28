-- =============================================================================
-- GradMent Data Platform — Pipeline Audit Log Table DDL
-- Tracks execution metadata, durations, row counts, and status for fct_pipeline_runs
-- =============================================================================

CREATE TABLE IF NOT EXISTS fct_pipeline_runs (
    run_sk BIGINT PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL UNIQUE,
    dag_id VARCHAR(64) NOT NULL,
    lane VARCHAR(32) NOT NULL DEFAULT 'synthetic',
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_seconds NUMERIC(10, 2) NOT NULL,
    rows_extracted INT NOT NULL DEFAULT 0,
    rows_loaded INT NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_fct_pipeline_runs_dag ON fct_pipeline_runs(dag_id, status);
CREATE INDEX IF NOT EXISTS idx_fct_pipeline_runs_start ON fct_pipeline_runs(start_time);

COMMENT ON TABLE fct_pipeline_runs IS 'Audit table logging pipeline execution runtimes, row counts, and status.';
