# Data Team Dashboard Catalog Specification

**Objective:** Data Engineering pipeline execution health, runtime durations, stage breakdowns, event volume, data freshness, duplicate/missing events, and warehouse growth for Data Engineers.
**Audience:** Data Engineering Lead / Analytics Engineers
**KPIs:** `pipeline_runtime`, `pipeline_success_rate`, `etl_duration_by_stage`, `event_volume`, `data_freshness`, `duplicate_events`, `missing_late_events`, `warehouse_growth`
**Drill-down:** Click on a DAG run to view detailed Airflow task durations; click on event volume to view ingestion rates per partition.
**Filters:** Date Range, DAG ID (`extract_transform_synthetic`, `extract_transform_real`), Run Status (`SUCCESS`, `FAILED`)
**Refresh:** Real-Time / Hourly
**Permissions:** Group: Data Engineers, System Admins

---

## Executable Dashboard SQL Queries

### Card 1: Pipeline Execution Health & Success Rates
```sql
SELECT
    run_date,
    total_runs,
    successful_runs,
    pipeline_success_rate,
    avg_pipeline_runtime_seconds,
    total_rows_extracted,
    total_rows_loaded
FROM mrt_data_engineering
ORDER BY run_date DESC;
```

### Card 2: Warehouse Ingestion & Row Volume Growth
```sql
SELECT
    run_date,
    total_rows_extracted AS event_volume,
    total_rows_loaded AS warehouse_growth
FROM mrt_data_engineering
ORDER BY run_date DESC;
```
