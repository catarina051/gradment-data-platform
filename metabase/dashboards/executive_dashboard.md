# Executive Dashboard Catalog Specification

**Objective:** High-level platform health, engagement North Star, user acquisition trends, and activation funnel metrics for CEO and executive leadership.
**Audience:** Executive / CEO / Leadership Team
**KPIs:** `dau`, `wau`, `mau`, `stickiness`, `user_growth`, `total_users`, `new_users`, `returning_users`, `registration_rate`, `activation_rate`, `time_to_activation`, `first_rating`, `first_upload`, `first_session_completion`
**Drill-down:** Click on daily active users to view active university and course breakdowns; click on new users to view registration source cohort detail.
**Filters:** Date Range, University (`dim_universities`), Platform (`web`, `mobile`)
**Refresh:** Hourly (aligned with Airflow pipeline execution schedule)
**Permissions:** Group: Executives, Admins

---

## Executable Dashboard SQL Queries

### Card 1: Executive North Star & User Engagement Summary
```sql
SELECT
    activity_date,
    dau,
    wau,
    mau,
    stickiness_dau_mau
FROM mrt_engagement
ORDER BY activity_date DESC;
```

### Card 2: User Acquisition & Growth Trends
```sql
SELECT
    metric_date,
    new_users,
    returning_users,
    total_active_users,
    total_users_cumulative,
    user_growth_rate
FROM mrt_acquisition
ORDER BY metric_date DESC;
```

### Card 3: User Activation & 7-Day Funnel Performance
```sql
SELECT
    registration_date,
    total_cohort_new_users,
    activated_users_7d,
    activation_rate_7d,
    users_first_action_rating,
    users_first_action_upload
FROM mrt_activation
ORDER BY registration_date DESC;
```
