# Engineering & Observability Dashboard Catalog Specification

**Objective:** API/Frontend error rates, response time percentiles (P50/P90), failed upload/login attempts, and validation error counts for CTO and Engineering team.
**Audience:** CTO / System Architects / Backend Engineers
**KPIs:** `api_error_rate`, `frontend_error_rate`, `upload_failures`, `login_failures`, `validation_errors`, `response_time_p50_p90`
**Drill-down:** Click on an error peak to view specific endpoint error payload codes; click on validation errors to inspect form names.
**Filters:** Date Range, Environment (`production`, `staging`), Platform (`web`, `mobile`)
**Refresh:** Hourly
**Permissions:** Group: Engineering, System Admins

---

## Executable Dashboard SQL Queries

### Card 1: System Error Rates & System Failure Counts
```sql
SELECT
    error_date,
    api_errors,
    frontend_errors,
    upload_failures,
    login_failures,
    validation_errors,
    total_events,
    api_error_rate,
    frontend_error_rate
FROM mrt_quality
ORDER BY error_date DESC;
```

### Card 2: Response Time Percentiles (P50 & P90)
```sql
SELECT
    error_date,
    response_time_p50_ms,
    response_time_p90_ms
FROM mrt_quality
ORDER BY error_date DESC;
```
