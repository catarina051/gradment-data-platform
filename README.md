# GradMent Data Platform

> **Product Analytics & Data Engineering Portfolio Project**

Welcome to the **GradMent Data Platform** repository — an end-to-end, production-grade Data & Analytics Engineering platform built for **GradMent** (an academic planning and evaluation system for university students).

---

## 🏛️ Architecture Overview & Two-Lane Design

This platform operates on a **Two-Lane Principle**:

```
                    ┌─────────────────────────────┐
                    │   GradMent Production (priv) │
                    │   CodeIgniter 4 + MySQL       │
                    └───────────────┬──────────────┘
                                    │  read-only user, additive events table
                                    ▼
                    ┌─────────────────────────────┐
                    │        REAL LANE (private)    │
                    │  extraction → anonymization   │
                    │  → validation → transform      │
                    │  → private Data Warehouse      │
                    │  → private dashboards (team)   │
                    └─────────────────────────────┘

                    ┌─────────────────────────────┐
                    │      SYNTHETIC LANE (public)  │
                    │  synthetic data generator      │
                    │  (same shape as real schema)   │
                    │  → same transform code         │
                    │  → public Data Warehouse       │
                    │  → public dashboards (demo)    │
                    └─────────────────────────────┘
```

- **Public Repository (Synthetic Lane):** 100% open-source code, dbt models, Apache Airflow DAGs, data quality tests, and realistic synthetic data generators.
- **Private Execution (Real Lane):** Runs identical pipeline code configured via local environment variables (`.env`) against anonymized production MySQL data. **No real data is ever committed to this repository.**

---

## 🛠️ Technology Stack

- **Extraction & Orchestration:** Python, SQLAlchemy, Apache Airflow (Docker)
- **Staging & Data Warehouse:** PostgreSQL (Dimensional Star Schema)
- **Transformation & Data Modeling:** dbt-core (Medallion Architecture: Staging → Intermediate → Marts)
- **Data Quality & Governance:** dbt tests, Schema Validation, Salted SHA-256 Anonymization
- **Business Intelligence & Metrics:** Metabase & dbt Semantic Layer
- **CI/CD & Code Quality:** GitHub Actions, Ruff, SQLFluff

---

## 📋 Implementation Roadmap

- [x] **Phase -1: Product Discovery** ([docs/product_discovery.md](docs/product_discovery.md))
- [x] **Phase 0: Database Discovery** ([docs/schema_inventory.md](docs/schema_inventory.md) & [docs/erd.md](docs/erd.md))
- [x] **Phase 1: Event Collection Architecture** ([events_catalog.yml](events_catalog.yml) & [schemas/event_envelope.schema.json](schemas/event_envelope.schema.json))
- [x] **Phase 2: Backend Instrumentation** ([docs/backend_instrumentation.md](docs/backend_instrumentation.md))
- [x] **Phase 2.5: Frontend Telemetry Integration** ([docs/frontend_telemetry.md](docs/frontend_telemetry.md))
- [x] **Phase 3: Analytical Database Design** ([docs/star_schema.md](docs/star_schema.md), [warehouse/schema.sql](warehouse/schema.sql), [docs/analytical_erd.md](docs/analytical_erd.md))
- [x] **Phase 4: ETL/ELT Pipeline** ([extract/](extract/), [dags/](dags/), [.github/workflows/phase4_ci.yml](.github/workflows/phase4_ci.yml))
- [x] **Phase 5: Data Quality** ([dbt_project/models/](dbt_project/models/), [dbt_project/tests/singular/](dbt_project/tests/singular/), [scripts/check_schema_drift.py](scripts/check_schema_drift.py), [.github/workflows/phase5_ci.yml](.github/workflows/phase5_ci.yml))
- [x] **Phase 6: Data Warehouse** ([docs/data-catalog/](docs/data-catalog/), [docs/lineage.md](docs/lineage.md), [docs/pipeline_benchmarks.md](docs/pipeline_benchmarks.md), [.github/workflows/phase6_ci.yml](.github/workflows/phase6_ci.yml))
- [x] **Phase 7: Metrics Catalog** ([dbt_project/models/marts/metrics/](dbt_project/models/marts/metrics/), [docs/metrics_catalog.md](docs/metrics_catalog.md), [scripts/check_metrics_drift.py](scripts/check_metrics_drift.py), [.github/workflows/phase7_ci.yml](.github/workflows/phase7_ci.yml))
- [x] **Phase 8: Dashboards** ([metabase/dashboards/](metabase/dashboards/), [showcase/index.html](showcase/index.html), [docs/dashboard_screenshots/](docs/dashboard_screenshots/), [.github/workflows/phase8_ci.yml](.github/workflows/phase8_ci.yml))
- [ ] **Phase 9: Deployment**
- [ ] **Phase 10: Portfolio Packaging**

---

## 📂 Repository Structure

```
gradment-data-platform/
├── .github/workflows/         # CI/CD workflows for automated pipeline, quality, performance, metric & dashboard validation
│   ├── phase4_ci.yml
│   ├── phase5_ci.yml
│   ├── phase6_ci.yml
│   ├── phase7_ci.yml
│   └── phase8_ci.yml
├── docs/                      # Architectural design, star schema spec, ERD, data catalog, lineage, metrics & screenshots
│   ├── star_schema.md
│   ├── analytical_erd.md
│   ├── lineage.md
│   ├── lineage.png
│   ├── metrics_catalog.md     # Specification catalog for all 56 Section 19 metrics across 9 categories
│   ├── pipeline_benchmarks.md
│   ├── data-catalog/          # Individual markdown catalog for all 11 warehouse models
│   ├── dashboard_screenshots/ # Build-rendered visual screenshot artifacts for all 6 role-based dashboards
│   ├── product_discovery.md
│   ├── schema_inventory.md
│   ├── backend_instrumentation.md
│   └── frontend_telemetry.md
├── metabase/                  # Role-based dashboard catalog specifications & JSON export
│   ├── dashboards/            # 6 catalog specs following Section 27 template
│   │   ├── executive_dashboard.md
│   │   ├── product_dashboard.md
│   │   ├── academic_dashboard.md
│   │   ├── engineering_dashboard.md
│   │   ├── data_dashboard.md
│   │   └── monetization_dashboard.md
│   └── export_dashboards.json
├── showcase/                  # Standalone interactive public web dashboard showcase app
│   ├── index.html
│   └── data_snapshot.json     # Embedded Data Snapshot updated at build time
├── extract/                   # Python extractor modules, watermark state, dynamic partition manager
│   ├── extract_events.py
│   ├── extract_reference_tables.py
│   ├── watermark.py
│   ├── partition_manager.py
│   └── audit.py
├── dags/                      # Airflow DAG orchestrations (Synthetic, Real, Quality)
│   ├── extract_transform_synthetic.py
│   ├── extract_transform_real.py
│   └── quality_dag.py
├── warehouse/                 # ANSI SQL DDL statements and database schema definitions
│   ├── schema.sql
│   └── pipeline_audit.sql
├── dbt_project/               # dbt transformation models (staging, core marts, snapshots, metric marts)
│   ├── dbt_project.yml        # Layer materializations & delete+insert incremental rules
│   ├── models/staging/_staging__models.yml
│   ├── models/marts/core/_core__models.yml
│   ├── models/marts/metrics/ # 9 dedicated SQL mart models matching Section 19 categories 1:1
│   └── tests/singular/
├── scripts/                   # Synthetic seed generator, schema, performance, metric & dashboard validation scripts
│   ├── synthetic/generate_seeds.py
│   ├── validate_events_catalog.py
│   ├── validate_star_schema.py
│   ├── test_postgres_execution_and_pruning.py
│   ├── validate_phase4_pipeline.py
│   ├── check_schema_drift.py
│   ├── validate_phase5_quality.py
│   ├── verify_phase6_dw_performance.py
│   ├── validate_phase6_warehouse.py
│   ├── check_metrics_drift.py
│   ├── validate_phase7_metrics.py
│   ├── generate_dashboards.py
│   ├── generate_dashboard_screenshots.py
│   └── validate_phase8_dashboards.py
├── events_catalog.yml         # Phase 1 39-event catalog specification contract
├── schemas/                   # JSON Schema envelope validators
├── docker-compose.yml         # Containerized Airflow + PostgreSQL deployment stack
├── .gitignore
└── README.md
```
