# Phase -1 — Product Discovery & Measurement Strategy

**Document Owner:** Data Engineering / Product Analytics  
**System:** GradMent Data Platform  
**Status:** Approved for Phase -1 Checkpoint  

---

## 1. Executive Summary & Objective

Before instrumenting event tracking or building database pipelines, the **GradMent Data Platform** establishes a clear, hypothesis-driven Product Discovery framework. 

The primary goal of Phase -1 is to map concrete business and product questions to quantitative metrics **before writing code**. This ensures that every tracked event directly informs product decisions, prevents over-instrumentation ("tracking data for the sake of tracking"), and aligns technical engineering work with business objectives.

---

## 2. Product Framing Frameworks

### 2.1 North Star Metric

> **North Star Metric:** *Weekly Active Users who complete at least one core value-creating action (Rating a discipline/professor, Downloading a study material/past exam, or Saving a curriculum planning session).*

**Why this metric?**  
Simple active user counts (like raw page views or login frequency) do not prove that students are deriving utility from GradMent. The North Star metric moves **only** when students actively participate in the academic ecosystem.

---

### 2.2 AARRR (Pirate Metrics) Funnel Mapping

| Funnel Stage | Core Business Question | Mapped Platform Category | Key Metrics |
|---|---|---|---|
| **Acquisition** | Are new students finding GradMent across target universities and courses? | Acquisition | Total Users, New Users, Registration Rate, University Growth, Course Growth |
| **Activation** | Do new users experience value (first rating/download/plan) within 7 days of registration? | Activation | Activation Rate, Time to Activation, First Rating Share, First Session Completion |
| **Retention** | Do students return week-over-week and semester-over-semester? | Retention | D1/D7/D30 Retention, WAU, MAU, Cohort Retention Matrix, Stickiness (DAU/MAU) |
| **Referral (Growth)** | Is GradMent spreading organically within specific academic courses/faculties? | Growth Proxy | Course Growth, University Active User Depth |
| **Revenue / Monetization** | Where is student engagement strong enough to justify future premium features or B2B institutional partnerships? | Monetization Readiness | Power-User Concentration, High-Value Feature Usage, Institutional Concentration |

---

### 2.3 HEART Framework (Product UX Lens)

For Product and UX design iterations (specifically driving the Phase 8 Product Dashboard), metrics are categorized using Google’s HEART framework:

- **Happiness:** Content feedback signal (Rating score distribution, rating comment rate).
- **Engagement:** Depth of interaction (`sessions_per_user`, median session duration, feature adoption).
- **Adoption:** Percentage of new registrants reaching activation milestones.
- **Retention:** Cohort retention rates over 7, 14, and 30 days.
- **Task Success:** Search success rate vs empty search rate, and planning session completion vs abandonment.

---

## 3. Ranked Business & Product Questions Matrix

Every metric implemented in the Data Platform exists to answer a specific decision-oriented business question. Below is the ranked list of business questions ordered by strategic decision impact.

### Priority 1: High Decision Impact (Activation & Core Funnel Health)

#### Q1: What percentage of newly registered students experience core value within their first week?
- **Mapped Metrics:** `Activation Rate`, `Time to Activation`, `First Rating`, `First Upload`
- **Decision Impact:** If activation rate drops below 30%, product efforts must focus on onboarding simplification rather than user acquisition marketing.

#### Q2: Which feature acts as the strongest hook for first-time user activation?
- **Mapped Metrics:** `First Rating Share`, `First Upload Share`, `First Session Completion`
- **Decision Impact:** Informs landing page copy and primary CTA placement (e.g., prompting for a course rating vs. directing students to past exams).

#### Q3: Where do users abandon the multi-step curriculum planning workflow?
- **Mapped Metrics:** `Screen/Feature Abandonment`, `Funnel Conversion`, `Search Success Rate`
- **Decision Impact:** Directs engineering sprint priorities to fix UI friction points in the course planning feature.

---

### Priority 2: Medium-High Decision Impact (Retention & Engagement Depth)

#### Q4: How sticky is GradMent during peak academic periods (exam weeks vs. vacation)?
- **Mapped Metrics:** `DAU`, `WAU`, `MAU`, `Stickiness (DAU/MAU)`, `Cohort Retention Table`
- **Decision Impact:** Helps schedule re-engagement notification campaigns and infrastructure auto-scaling windows.

#### Q5: Are students searching for academic content that does not yet exist on the platform?
- **Mapped Metrics:** `Empty Search Rate`, `Search Success Rate`, `Searches`
- **Decision Impact:** Identifies content supply gaps (missing courses/professors) to target student content contribution drives.

---

### Priority 3: Strategic & Future-Proofing (Quality & Monetization Readiness)

#### Q6: Are technical errors or upload failures degrading user satisfaction?
- **Mapped Metrics:** `API Error Rate`, `Frontend Error Rate`, `Upload Failures`, `Login Failures`
- **Decision Impact:** Triggers immediate engineering bug-fix sprints when error rates exceed SLAs (>1.5%).

#### Q7: Is engagement concentrated in a small group of power users or evenly distributed across faculties?
- **Mapped Metrics:** `Power-User Concentration`, `High-Value Feature Usage`, `Institutional Concentration`
- **Decision Impact:** Validates monetization feasibility (e.g., whether to explore premium individual features vs. institutional B2B software offerings).

---

## 4. Verification & Governance Traceability

All business questions and metrics documented here map 1:1 to:
1. **Metrics Catalog:** Section 19 of `IMPLEMENTATION_PLAN.md`.
2. **Event Taxonomy:** Section 20 of `IMPLEMENTATION_PLAN.md` (`events_catalog.yml` in Phase 1).
3. **dbt Marts Layer:** `models/marts/` star schema tables in Phase 4.

---

## 5. Phase -1 Sign-off & Checklist

- [x] All core product and business questions identified and documented.
- [x] Each question mapped to concrete metrics in the Metrics Catalog.
- [x] Questions ranked by decision-making impact.
- [x] Alignment with North Star, AARRR, and HEART frameworks established.
- [x] Document placed in standalone public repo at `gradment-data-platform/docs/product_discovery.md`.
