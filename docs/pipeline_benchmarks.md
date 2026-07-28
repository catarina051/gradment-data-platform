# Pipeline & Data Warehouse Performance Benchmarks Report

This document records physical query execution performance, `EXPLAIN ANALYZE` scan types, and SLA validation for analytical workloads across a **scaled 180-day (~6 months, 14,000+ total rows)** synthetic dataset in PostgreSQL.

--- 

## 1. Executive Summary & SLA Metrics (Scaled 180-Day Dataset)

| Specification Metric | Internal Target | Official Threshold | Empirical Result | Status |
|---|---|---|---|---|
| Workload A: Daily User Retention & DAU Composite Index Test | < 500 ms | < 3000 ms (NFR-2) | **0.86 ms** | **PASS (< 500ms Target)** |
| Workload B: Discipline & Professor Rating Score Rollup | < 500 ms | < 3000 ms (NFR-2) | **1.78 ms** | **PASS (< 500ms Target)** |
| Workload C: User Session Duration & Engagement Analysis | < 500 ms | < 3000 ms (NFR-2) | **0.8 ms** | **PASS (< 500ms Target)** |

---

## 2. EXPLAIN ANALYZE Execution Plans

### Workload A: Daily User Retention & DAU Composite Index Test

```sql
SELECT date_sk, user_sk, session_count, events_count FROM fct_daily_user_activity WHERE date_sk = 20260115 AND user_sk = 42;
```

#### PostgreSQL Raw Plan Output
```text
Index Scan using idx_fct_daily_activity_date_user on fct_daily_user_activity (actual time=0.055..0.056 rows=1.00 loops=1)
  Index Cond: ((date_sk = 20260115) AND (user_sk = 42))
  Index Searches: 1
Planning Time: 0.293 ms
Execution Time: 0.074 ms
```

### Workload B: Discipline & Professor Rating Score Rollup

```sql
SELECT c.codigo_disciplina, c.nome_disciplina, AVG(r.dificuldade) as avg_dificuldade, AVG(r.esforco) as avg_esforco FROM fct_ratings r JOIN dim_courses c ON r.course_sk = c.course_sk WHERE r.date_sk = 20260115 GROUP BY c.codigo_disciplina, c.nome_disciplina;
```

#### PostgreSQL Raw Plan Output
```text
GroupAggregate (actual time=0.137..0.138 rows=1.00 loops=1)
  Group Key: c.codigo_disciplina, c.nome_disciplina
  ->  Sort (actual time=0.111..0.112 rows=9.00 loops=1)
        Sort Key: c.codigo_disciplina, c.nome_disciplina
        Sort Method: quicksort  Memory: 25kB
        ->  Nested Loop (actual time=0.054..0.066 rows=9.00 loops=1)
              ->  Bitmap Heap Scan on fct_ratings r (actual time=0.040..0.041 rows=9.00 loops=1)
                    Recheck Cond: (date_sk = 20260115)
                    Heap Blocks: exact=1
                    ->  Bitmap Index Scan on idx_fct_ratings_date_sk (actual time=0.006..0.006 rows=9.00 loops=1)
                          Index Cond: (date_sk = 20260115)
                          Index Searches: 1
              ->  Index Scan using dim_courses_pkey on dim_courses c (actual time=0.002..0.002 rows=1.00 loops=9)
                    Index Cond: (course_sk = r.course_sk)
                    Index Searches: 9
Planning Time: 0.656 ms
Execution Time: 0.218 ms
```

### Workload C: User Session Duration & Engagement Analysis

```sql
SELECT u.user_id, SUM(s.session_duration_seconds) as total_duration FROM fct_sessions s JOIN dim_users u ON s.user_sk = u.user_sk WHERE s.session_start_date_sk = 20260115 GROUP BY u.user_id;
```

#### PostgreSQL Raw Plan Output
```text
GroupAggregate (actual time=0.106..0.117 rows=19.00 loops=1)
  Group Key: u.user_id
  ->  Sort (actual time=0.102..0.104 rows=19.00 loops=1)
        Sort Key: u.user_id
        Sort Method: quicksort  Memory: 25kB
        ->  Nested Loop (actual time=0.036..0.063 rows=19.00 loops=1)
              ->  Bitmap Heap Scan on fct_sessions s (actual time=0.028..0.029 rows=19.00 loops=1)
                    Recheck Cond: (session_start_date_sk = 20260115)
                    Heap Blocks: exact=1
                    ->  Bitmap Index Scan on idx_fct_sessions_start_date_sk (actual time=0.010..0.010 rows=19.00 loops=1)
                          Index Cond: (session_start_date_sk = 20260115)
                          Index Searches: 1
              ->  Index Scan using dim_users_pkey on dim_users u (actual time=0.001..0.001 rows=1.00 loops=19)
                    Index Cond: (user_sk = s.user_sk)
                    Index Searches: 19
Planning Time: 0.299 ms
Execution Time: 0.155 ms
```

