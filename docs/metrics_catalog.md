# Metrics Catalog Specification — GradMent Data Platform

This document is the human-readable Metrics Specification for the GradMent Data Platform, cross-referencing **100% of all 56 metrics across all 9 categories** from Section 19 of `IMPLEMENTATION_PLAN.md`.

---

## 1. Acquisition Metrics (19.1)
- **`total_users` (Total Users)**: All-time registered users in `dim_users` (`COUNT(DISTINCT user_sk)`).
- **`new_users` (New Users)**: Users registered within the period (`COUNT(*)` where `registration_date` in period).
- **`returning_users` (Returning Users)**: Users active in period who registered before period start (`COUNT(DISTINCT user_sk)` in `fct_daily_user_activity` where `registration_date < period_start`).
- **`user_growth` (User Growth)**: Period-over-period percentage growth (`(new_users_this_period - new_users_last_period) / NULLIF(new_users_last_period, 0)`).
- **`registration_rate` (Registration Rate)**: Share of unauthenticated sessions completing registration (`registrations / NULLIF(unauthenticated_sessions, 0)`).
- **`university_growth` (University Growth)**: New universities with active users period-over-period.
- **`course_growth` (Course Growth)**: New courses with at least 1 rating or usage event period-over-period.

---

## 2. Activation Metrics (19.2)
- **`activation_rate` (Activation Rate)**: Share of new users completing an activating action (first rating, first upload, or first completed planning session) within 7 days of registration (`activated_users_within_7d / NULLIF(new_users, 0)`).
- **`time_to_activation` (Time to Activation)**: Median time in hours between registration and first activating event (`MEDIAN(activation_ts - registration_ts)`).
- **`first_rating` (First Rating)**: Share of new users whose first activating action was a rating (`COUNT(first_action = 'rating') / NULLIF(activated_users, 0)`).
- **`first_upload` (First Upload)**: Share of new users whose first activating action was a material upload (`COUNT(first_action = 'upload') / NULLIF(activated_users, 0)`).
- **`first_session_completion` (First Session Completion)**: Share of new users completing full session without abandonment (`first_session_completed / NULLIF(new_users, 0)`).

---

## 3. Retention Metrics (19.3)
- **`d1_d7_d14_d30_retention` (D1 / D7 / D14 / D30 Retention)**: Share of registration cohort active N days after registration (`active_on_day_N / NULLIF(cohort_size, 0)`).
- **`wau` (WAU)**: Weekly Active Users active in trailing 7 days (`COUNT(DISTINCT user_sk)`).
- **`mau` (MAU)**: Monthly Active Users active in trailing 30 days (`COUNT(DISTINCT user_sk)`).
- **`cohort_retention_table` (Cohort Retention Table)**: Standard cohort-by-week retention matrix.
- **`rolling_retention` (Rolling Retention)**: Share of cohort active in any later period (`COUNT(active_in_later_period) / NULLIF(cohort_size, 0)`).

---

## 4. Engagement Metrics (19.4)
- **`dau` (DAU)**: Daily Active Users (`COUNT(DISTINCT user_sk)`).
- **`wau_mau` (WAU / MAU)**: Ratio of WAU to MAU.
- **`stickiness` (Stickiness)**: DAU to MAU ratio (`DAU / NULLIF(MAU, 0)`). Target range: [0.0, 1.0].
- **`session_duration` (Session Duration)**: Median and P90 session duration in seconds (`PERCENTILE_CONT(0.5)` and `PERCENTILE_CONT(0.9)` of `session_duration_seconds`).
- **`sessions_per_user` (Sessions per User)**: Average sessions per active user (`total_sessions / NULLIF(active_users, 0)`).
- **`feature_adoption` (Feature Adoption)**: Share of active users using a specific feature (`feature_users / NULLIF(mau, 0)`).
- **`bounce_rate` (Bounce Rate)**: Share of single-event sessions (`single_event_sessions / NULLIF(total_sessions, 0)`).
- **`power_users` (Power Users)**: Users in top decile of session frequency.
- **`dormant_users` (Dormant Users)**: Previously active users with no activity in trailing 30 days.

---

## 5. Content Metrics (19.5)
- **`ratings` (Ratings)**: Total discipline and professor ratings submitted (`COUNT(*)` in `fct_ratings`).
- **`downloads` (Downloads)**: Total material and past-exam downloads (`COUNT(*)` where `event_name = 'material_downloaded'`).
- **`uploads` (Uploads)**: Total materials uploaded (`COUNT(*)` where `event_name = 'material_uploaded'`).
- **`searches` (Searches)**: Total search queries executed (`COUNT(*)` where `event_name = 'search_performed'`).
- **`search_success_rate` (Search Success Rate)**: Share of searches leading to result opened/downloaded (`successful_searches / NULLIF(searches, 0)`).
- **`empty_search_rate` (Empty Search Rate)**: Share of searches returning zero results (`zero_result_searches / NULLIF(searches, 0)`).
- **`professors_ranked` (Professors Ranked)**: Distinct professors with at least one rating (`COUNT(DISTINCT professor_sk)`).
- **`courses_ranked` (Courses Ranked)**: Distinct courses with at least one rating (`COUNT(DISTINCT course_sk)`).

---

## 6. Product Metrics (19.6)
- **`funnel_conversion` (Funnel Conversion)**: Step-over-step conversion ratio across defined user funnel steps.
- **`screen_feature_abandonment` (Screen/Feature Abandonment)**: Share of multi-step flows started but not completed (`started_not_completed / NULLIF(started, 0)`).
- **`most_least_used_features` (Most / Least Used Features)**: Tabular ranking of features by unique user adoption and total event count (`rank_by_users`, `rank_by_events`).
- **`navigation_flow` (Navigation Flow)**: Tabular ranking of top screen-to-screen transition sequences (`prev_screen`, `next_screen`, `transition_count`).

---

## 7. Quality Metrics (19.7)
- **`api_error_rate` (API Error Rate)**: Share of backend requests resulting in 5xx/4xx error (`api_errors / NULLIF(total_requests, 0)`).
- **`frontend_error_rate` (Frontend Error Rate)**: Share of sessions with client-side error (`sessions_with_error / NULLIF(total_sessions, 0)`).
- **`upload_failures` (Upload Failures)**: Failed upload attempts share (`failed_uploads / NULLIF(total_uploads, 0)`).
- **`login_failures` (Login Failures)**: Failed login attempts share (`failed_logins / NULLIF(total_logins, 0)`).
- **`validation_errors` (Validation Errors)**: Form validation errors count (`COUNT(*)` where `event_name = 'validation_error_occurred'`).
- **`response_time_p50_p90` (Response Time (P50/P90))**: Median and 90th percentile response time in milliseconds.

---

## 8. Data Engineering Metrics (19.8)
- **`pipeline_runtime` (Pipeline Runtime)**: Duration of Airflow DAG execution (`duration_seconds` in `fct_pipeline_runs`).
- **`pipeline_success_rate` (Pipeline Success Rate)**: Share of DAG runs completing without failure (`successful_runs / NULLIF(total_runs, 0)`).
- **`etl_duration_by_stage` (ETL Duration by Stage)**: Extraction, transform, and quality gate task durations.
- **`event_volume` (Event Volume)**: Raw events ingested per day (`COUNT(*)` in `fct_events`).
- **`data_freshness` (Data Freshness)**: Time elapsed since most recent loaded event (`NOW() - MAX(event_ts)`).
- **`duplicate_events` (Duplicate Events)**: Events with repeated `event_id` (`COUNT(*) - COUNT(DISTINCT event_id)`).
- **`missing_late_events` (Missing/Late Events)**: Events delivered with timestamp significantly earlier than load time.
- **`warehouse_growth` (Warehouse Growth)**: Weekly row count growth of core warehouse fact tables.

---

## 9. Monetization Readiness Metrics (19.9)
- **`power_user_concentration` (Power-User Concentration)**: Share of total engagement generated by top 10% of users (`top_10pct_sessions / NULLIF(total_sessions, 0)`).
- **`high_value_feature_usage` (High-Value Feature Usage)**: Adoption rate of paywall-candidate features (e.g. past exams, advanced planning).
- **`institutional_concentration` (Institutional Concentration)**: Share of active users in top N universities (`top_n_univ_users / NULLIF(mau, 0)`).
- **`willingness_to_engage_proxy` (Willingness-to-Engage Proxy)**: Correlation proxy between session frequency and feature usage depth.
