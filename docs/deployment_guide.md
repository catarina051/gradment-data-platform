# GradMent Data Platform — Production Deployment Runbook & Operational Guide

This runbook outlines the deployment architecture, Docker Compose orchestration, environment configuration, CLI commands, backup/restore procedures, and health monitoring for the **GradMent Data Platform**.

---

## 🚀 Quickstart: 1-Command Setup (< 15-Minute SLA)

```bash
# 1. Clone repository
git clone https://github.com/gradment/gradment-data-platform.git
cd gradment-data-platform

# 2. Spin up containerized infrastructure stack
make up

# 3. Seed warehouse with 180-day realistic dataset & build mart views
make seed

# 4. Execute end-to-end multi-phase validation suite across all 9 phases
make test
```

All **6 role-based dashboards** (`Executive`, `Product`, `Academic`, `Engineering`, `Data`, `Monetization`) will be populated and ready in under 15 minutes.

---

## 🔒 Isolamento de Dados e Decisão de Privacidade (Lane Sintética vs. Lane Real)

> [!IMPORTANT]
> **Decisão Deliberada de Design e Privacidade:**  
> O repositório público do **GradMent Data Platform** opera **exclusivamente na Lane Sintética** por decisão deliberada de governança e privacidade de dados (e **não por qualquer limitação técnica**).

- **Lane Sintética (Repositório Público no GitHub):**  
  Gera e processa datasets sintéticos realistas e telemetria comportamental de 180 dias com validação estrita de schema. Isso garante a execução *end-to-end* completa de todos os 39 eventos do catálogo, modelos dbt, particionamento mensal no PostgreSQL, testes de qualidade de dados e preenchimento dos 6 dashboards por papel, sem expor nenhum dado real de alunos ou de produção.

- **Lane Real de Produção (Operações Privadas):**  
  A arquitetura do código possui suporte nativo completo para extração operacional real (`--source real`, conexão com réplica MySQL `analytics_ro`, isolamento de privilégios por coluna e anonimização SHA-256 com salt). No entanto, **instruções de ativação e credenciais da Lane Real são intencionalmente NÃO documentadas no README público nem em docs commitados neste repositório**. As instruções de ativação da Lane Real existem exclusivamente em um guia privado separado da equipe, mantido fora do GitHub.

**Motivo:** Qualquer pessoa que clonar este repositório público pode executar, popular, construir e testar a plataforma de dados inteira com 1 único comando (`make seed && make test`), sem necessitar de credenciais de produção ou acesso à VPN privada do GradMent.

---

## 🛠️ Developer CLI Wrapper Reference (`Makefile`)

| Command | Action | SLA / Description |
|---|---|---|
| `make help` | Display CLI targets | Quick reference of available Makefile targets |
| `make up` | Start Docker stack | Spins up PostgreSQL DW (`5432`) and Metabase (`3000`) |
| `make seed` | Seed dataset | Populates 180-day synthetic dataset & builds 9 mart views |
| `make run-pipeline` | Run ETL pipeline | Triggers Python extractors & Airflow DAGs |
| `make test` | Run test suite | Executes 9-phase verification suite (Phase 1 through 9) |
| `make health` | Check system health | Runs `scripts/health_check.py` SLA & freshness probe |
| `make down` | Stop containers | Gracefully stops containerized stack |
| `make reset` | Purge & reset | Wipes database volumes and resets container state |

---

## 🔒 Security & Secrets Management

Per Section 16 (Security Strategy):
- All database credentials are managed via environment variables (`PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASS`, `PG_DB`).
- Secrets scanning is automatically enforced on every push/PR via **[Gitleaks](file:///.github/workflows/gitleaks.yml)**.
- Sensitive production connection strings must be stored in secure vault/GitHub Secrets, never committed to git.

---

## 📊 Populated Dashboards Access

Once deployed, access the **6 role-based dashboards**:
1. **Public Showcase App**: Open `showcase/index.html` directly in any web browser.
2. **Metabase BI UI**: Open `http://localhost:3000` (Import `metabase/export_dashboards.json`).
3. **Dashboard Catalog Specifications**: Refer to [metabase/dashboards/](file:///metabase/dashboards/).
