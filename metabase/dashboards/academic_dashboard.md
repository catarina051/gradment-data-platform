# Academic & Content Dashboard Catalog Specification

**Objective:** Discipline rating distributions, professor evaluation scores, material downloads, uploads, and search conversion for Academic Coordinators.
**Audience:** Academic Coordinators / Department Leads
**KPIs:** `ratings`, `downloads`, `uploads`, `searches`, `search_success_rate`, `empty_search_rate`, `professors_ranked`, `courses_ranked`, `university_growth`, `course_growth`
**Drill-down:** Click on a course code to view individual professor rating breakdowns; click on empty search rate to view missing query themes.
**Filters:** Date Range, University (`dim_universities`), Course Code, Academic Period (`2026.1`)
**Refresh:** Daily
**Permissions:** Group: Academic Leads, Product, Executives

---

## Executable Dashboard SQL Queries

### Card 1: Academic Evaluations & Rating Distributions
```sql
SELECT
    metric_date,
    total_ratings,
    avg_dificuldade,
    avg_esforco,
    professors_ranked,
    courses_ranked
FROM mrt_content
ORDER BY metric_date DESC;
```

### Card 2: Content Creation & Search Conversion Performance
```sql
SELECT
    metric_date,
    downloads,
    uploads,
    searches,
    search_success_rate,
    empty_search_rate
FROM mrt_content
ORDER BY metric_date DESC;
```
