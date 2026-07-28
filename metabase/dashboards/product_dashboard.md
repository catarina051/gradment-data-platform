# Product & Feature Dashboard Catalog Specification

**Objective:** Detailed feature adoption, funnel conversion, screen abandonment, bounce rates, and retention cohorts for Product Managers.
**Audience:** Product Managers / UX Designers
**KPIs:** `funnel_conversion`, `screen_feature_abandonment`, `most_least_used_features`, `navigation_flow`, `bounce_rate`, `feature_adoption`, `power_users`, `dormant_users`, `sessions_per_user`, `session_duration`, `d1_d7_d14_d30_retention`, `cohort_retention_table`, `rolling_retention`
**Drill-down:** Click on a feature to view drop-off rates by screen; click on cohort retention cell to inspect specific registration day behavior.
**Filters:** Date Range, Feature Domain, Platform (`web`, `mobile`), App Version
**Refresh:** Hourly
**Permissions:** Group: Product, Engineering, Executives

---

## Executable Dashboard SQL Queries

### Card 1: Feature Adoption & Ranked Feature Usage
```sql
SELECT
    feature_key,
    unique_users_count,
    total_events_count,
    rank_most_used,
    rank_least_used
FROM mrt_product
ORDER BY rank_most_used ASC;
```

### Card 2: Session Duration & Bounce Rate Trends
```sql
SELECT
    activity_date,
    avg_session_duration_seconds,
    sessions_per_user,
    bounce_rate,
    feature_adoption_rate,
    dormant_users_count,
    power_users_count
FROM mrt_engagement
ORDER BY activity_date DESC;
```

### Card 3: Cohort Retention Matrix (D1 / D7 / D14 / D30)
```sql
SELECT
    cohort_date,
    cohort_size,
    d1_active_users,
    d7_active_users,
    d14_active_users,
    d30_active_users,
    d1_retention_rate,
    d7_retention_rate,
    d30_retention_rate
FROM mrt_retention
ORDER BY cohort_date DESC;
```
