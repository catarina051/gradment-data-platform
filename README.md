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
- [ ] **Phase 6: Data Warehouse**
- [ ] **Phase 7: Metrics Catalog**
- [ ] **Phase 8: Dashboards**
- [ ] **Phase 9: Deployment**
- [ ] **Phase 10: Portfolio Packaging**

---

## 📂 Repository Structure

```
gradment-data-platform/
├── .github/workflows/         # CI/CD workflows for automated pipeline & quality validation
│   ├── phase4_ci.yml
│   └── phase5_ci.yml
├── docs/                      # Architectural design, star schema spec, ERD, discovery docs
│   ├── star_schema.md
│   ├── analytical_erd.md
│   ├── product_discovery.md
│   ├── schema_inventory.md
│   ├── backend_instrumentation.md
│   └── frontend_telemetry.md
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
├── dbt_project/               # dbt transformation models (staging, core marts, snapshots, quality tests)
│   ├── models/staging/_staging__models.yml
│   ├── models/marts/core/_core__models.yml
│   └── tests/singular/
│       ├── assert_session_duration_non_negative.sql
│       ├── assert_rating_scores_valid.sql
│       ├── assert_event_ts_not_in_future.sql
│       └── assert_fct_events_no_duplicates.sql
├── scripts/                   # Synthetic seed generator, schema & pipeline validation scripts
│   ├── synthetic/generate_seeds.py
│   ├── validate_events_catalog.py
│   ├── validate_star_schema.py
│   ├── test_postgres_execution_and_pruning.py
│   ├── validate_phase4_pipeline.py
│   ├── check_schema_drift.py
│   └── validate_phase5_quality.py
├── events_catalog.yml         # Phase 1 39-event catalog specification contract
├── schemas/                   # JSON Schema envelope validators
├── docker-compose.yml         # Containerized Airflow + PostgreSQL deployment stack
├── .gitignore
└── README.md
```
