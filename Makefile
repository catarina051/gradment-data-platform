# GradMent Data Platform — Production Developer CLI Makefile
.PHONY: help up seed run-pipeline test health down reset

help:
	@echo "======================================================================"
	@echo "GradMent Data Platform — Developer CLI Wrapper Commands"
	@echo "======================================================================"
	@echo "  make up           : Start containerized Docker Compose deployment stack"
	@echo "  make seed         : Generate & load 180-day synthetic warehouse dataset"
	@echo "  make run-pipeline : Execute Airflow ETL extractors & dbt mart views"
	@echo "  make test         : Run end-to-end multi-phase validation test suite"
	@echo "  make health       : Execute system health probe & freshness SLA check"
	@echo "  make down         : Stop running Docker Compose containers"
	@echo "  make reset        : Complete teardown & purge of volumes and databases"
	@echo "======================================================================"

up:
	docker compose up -d --build

seed:
	python scripts/generate_dashboards.py

run-pipeline:
	python scripts/validate_phase4_pipeline.py

test:
	python scripts/validate_events_catalog.py
	python scripts/validate_star_schema.py
	python scripts/test_postgres_execution_and_pruning.py
	python scripts/validate_phase4_pipeline.py
	python scripts/validate_phase5_quality.py
	python scripts/validate_phase6_warehouse.py
	python scripts/check_metrics_drift.py
	python scripts/validate_phase7_metrics.py
	python scripts/validate_phase8_dashboards.py
	python scripts/validate_phase9_deployment.py

health:
	python scripts/health_check.py

down:
	docker compose down

reset:
	docker compose down -v --remove-orphans
