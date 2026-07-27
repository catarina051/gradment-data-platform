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
- [ ] **Phase 2.5: Frontend Telemetry Integration**
- [ ] **Phase 3: Analytical Database Design**
- [ ] **Phase 4: ETL/ELT Pipeline**
- [ ] **Phase 5: Data Quality**
- [ ] **Phase 6: Data Warehouse**
- [ ] **Phase 7: Metrics Catalog**
- [ ] **Phase 8: Dashboards**
- [ ] **Phase 9: Deployment**
- [ ] **Phase 10: Portfolio Packaging**

---

## 📂 Repository Structure

```
gradment-data-platform/
├── docs/                      # Architectural design, product discovery, schemas, and ADRs
│   └── product_discovery.md
├── scripts/                   # Data discovery, extraction, and utility scripts
├── dbt/                       # dbt project (models, seeds, tests, docs)
├── airflow/                   # Airflow DAGs and plugins
├── tests/                     # Unit, integration, and data validation tests
├── .gitignore
└── README.md
```
