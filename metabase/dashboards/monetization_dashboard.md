# Monetization & Business Validation Dashboard Catalog Specification

**Objective:** Business model validation, power-user concentration, high-value feature adoption, institutional concentration, and willingness-to-engage proxies for Investors and Business Analysts.
**Audience:** Investors / Business Analysts / Founders
**KPIs:** `power_user_concentration`, `high_value_feature_usage`, `institutional_concentration`, `willingness_to_engage_proxy`
**Drill-down:** Click on top decile users to view detailed engagement frequency; click on university concentration to view multi-tenant growth.
**Filters:** Date Range, University (`dim_universities`), Feature Domain
**Refresh:** Monthly
**Permissions:** Group: Executives, Investors, Business Analysts

---

## Executable Dashboard SQL Queries

### Card 1: Power-User Concentration & Engagement Proxies
```sql
SELECT
    total_engaged_users,
    top_decile_sessions,
    total_sessions,
    power_user_concentration_rate,
    high_value_feature_usage_count,
    institutional_concentration_rate,
    willingness_to_engage_proxy
FROM mrt_monetization_readiness;
```
