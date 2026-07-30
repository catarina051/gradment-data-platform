# Auditoria Técnica — Plano de Correção

> Gerado a partir de uma revisão brutal do repositório (nível "Staff Data Engineer / Tech Lead avaliando candidato a estágio").
> Objetivo: corrigir item por item. Marque `[x]` conforme for resolvendo. Quando terminar tudo (ou um bloco 🔴/🟠), peça uma nova auditoria completa para comparar com esta.

Nota geral na auditoria original: **5.5/10**. Veredito: *"Contrataria apenas para estágio"* — não por falta de conhecimento teórico (o candidato demonstrou vocabulário correto de star schema, SCD2, medallion, CI/CD), mas porque várias partes do projeto **parecem funcionar mas não funcionam**, e isso não seria pego numa checagem rápida a menos que alguém realmente rodasse o pipeline (o que o CI atual não faz).

---

## 🔴 Críticas (bloqueiam qualquer alegação de "production-grade")

- [x] **`dbt` nunca é instalado nem executado em lugar nenhum do projeto.**
  CI (`.github/workflows/ci_cd_matrix.yml`) só instala `psycopg2-binary pyyaml jsonschema matplotlib`. Nenhuma etapa roda `dbt run`, `dbt build` ou `dbt test`. Toda a "Medallion Architecture" anunciada no README nunca é validada de fato.
  **Ação:** adicionar `dbt-core` + `dbt-postgres` ao CI e um step real de `dbt run && dbt test`.

- [x] **`stg_operational_tables.sql` referencia uma fonte (`source('operational_db', 'usuarios')`) que não existe em nenhum `sources.yml`.**
  Arquivo: `dbt_project/models/staging/stg_operational_tables.sql`.
  Isso faz `dbt compile` falhar com "source not found". Ninguém rodou esse modelo com sucesso, ou o arquivo está órfão.
  **Ação:** criar o `sources.yml` declarando `operational_db.usuarios` e `operational_db.curriculo_disciplinas`, OU remover o modelo se não for mais usado.

- [x] **Os nomes de coluna em `stg_operational_tables.sql` não batem com o schema real.**
  Usa `id_usuario`, `id_universidade`, `perfil`, `data_cadastro` — mas o schema real (documentado em `scripts/create_analytics_ro_user.sql`) usa `usuarios.id`, `usuario_academicos.faculdade_id`/`curso_id`, `status_academico`, etc.
  **Ação:** reescrever o staging model com os nomes reais de coluna/tabela, batendo com o grant script.

- [x] **`dim_universities.sql` e `dim_courses.sql` são hardcoded com uma única linha fake**, em vez de extrair da fonte real:
  ```sql
  select 1 as university_id, 'Universidade Federal de Viçosa' as name, 'UFV' as acronym, 'MG' as state
  ```
  Isso contradiz o próprio comentário do DDL (`'University metadata for multi-tenant analytical slicing'`).
  **Ação:** ligar essas dimensões à staging real (depois de corrigir os dois itens acima).

- [x] **A task `log_audit` da DAG (`dags/extract_transform_synthetic.py`, linhas ~58-61) é um `BashOperator` que só imprime uma frase**, fingindo logar em `fct_pipeline_runs`, mas não loga nada de verdade. O log real (`extract/audit.py`) é chamado separadamente, sem relação com essa task.
  **Ação:** ou fazer a task chamar `extract/audit.py` de verdade, ou removê-la da DAG.

- [x] **Chave substituta (`event_sk`, `user_sk`, `university_sk`, `course_sk`) gerada via `abs(hashtext(x))::bigint`.**
  `hashtext` do Postgres é 32 bits — colisão >50% de probabilidade a partir de ~77 mil linhas (paradoxo do aniversário). Isso é uma bomba-relógio de chave primária/join incorreto em escala.
  **Ação:** trocar por `dbt_utils.generate_surrogate_key(...)` (md5, 128 bits) ou sequence real.

- [x] **`fct_events.course_sk` e `fct_events.period_sk` são sempre `NULL`** (`dbt_project/models/marts/core/fct_events.sql`, linhas 25 e 27). Nenhuma métrica de evento por curso/período é possível hoje.
  **Ação:** popular de verdade ou documentar explicitamente a limitação no README/data catalog (não deixar implícito).

- [x] **"Screenshots" de dashboard não são screenshots.**
  `docs/dashboard_screenshots/*.png` são gerados por `scripts/generate_dashboard_screenshots.py` via `matplotlib` — uma simulação visual, não uma prova de que o Metabase real rodou com dados reais. Nenhum stakeholder olhou de fato para esses dashboards funcionando.
  **Ação:** subir o Metabase real (`docker-compose.yml` já tem o serviço), montar os 6 dashboards de verdade a partir dos specs em `metabase/dashboards/*.md`, e tirar screenshots reais (ou gravar um GIF).

---

## 🟠 Importantes

- [x] **`check_fk_relationships_coverage()` (`scripts/validate_phase5_quality.py`) não roda `dbt test` — conta blocos `relationships:` via regex e compara com número mágico hardcoded (`expected_total_fks = 16`).** Se você adicionar um teste novo (melhoria legítima), o "quality gate" falha.
  **Ação:** trocar por uma chamada real a `dbt test --select ...` e checar o exit code/resultado do `run_results.json`.

- [x] **`check_singular_invariant_tests()` duplica manualmente, como string Python, o SQL que já existe em `dbt_project/tests/singular/*.sql`.** Editar o teste real (`.sql`) não afeta essa validação — ela testa uma cópia congelada.
  **Ação:** ler e executar os arquivos `.sql` de `tests/singular/` diretamente, em vez de reescrevê-los em Python.

- [x] **`check_schema_drift.py` faz parsing de YAML com regex** (`re.findall(r'-\s+event_name:...')`) apesar de `pyyaml` estar instalado no CI e nunca ser usado.
  **Ação:** usar `yaml.safe_load()` de verdade.

- [x] **Bug de modelagem em `mrt_engagement.sql` (linhas ~61-62):** `feature_adoption_rate` e `dormant_users_count` usam `COUNT(*) FROM dim_users` **sem filtrar `is_current = true`** — como `dim_users` é SCD2, usuários com múltiplas versões históricas são contados mais de uma vez, inflando o denominador. `fct_events.sql` lembrou do filtro; aqui não.
  **Ação:** aplicar `WHERE is_current = true` (ou um CTE `dim_users_current`) em todo lugar que referencia `dim_users` para contagem de usuários únicos.

- [x] **Divergência de nomes de variável de ambiente**: `.env.example` usa `POSTGRES_HOST/POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB`, mas o código (`extract/extract_events.py`, linhas 34-38) lê `PG_HOST/PG_USER/PG_PASS/PG_DB`. Seguindo o próprio `.env.example`, a conexão cai silenciosamente nos defaults hardcoded.
  **Ação:** unificar os nomes entre `.env.example` e o código.

- [x] **Nenhum `requirements.txt` / `pyproject.toml` no repositório.** As dependências só existem hardcoded dentro do YAML do CI.
  **Ação:** criar `requirements.txt` (ou `pyproject.toml`) com todas as libs usadas (`psycopg2-binary`, `pymysql`, `python-dotenv`, `pyyaml`, `jsonschema`, `matplotlib`, `dbt-core`, `dbt-postgres`), e fazer o CI instalar a partir dele.

- [x] **Inserts linha a linha em loop** (`extract/extract_events.py`, dentro de `run_extraction()`) em vez de `execute_values`/`COPY`. Funciona com dataset sintético pequeno; não escala.
  **Ação:** trocar por inserção em lote.

---

## 🟡 Melhorias

- [x] Adicionar **type hints** em todo o código Python (`extract/`, `scripts/`, `dags/`, `monitoring/`).
- [x] Trocar **`print()` por `logging`** com níveis configuráveis (especialmente nos módulos que rodam dentro do Airflow).
- [x] Adicionar **testes unitários reais** (pytest, com fixtures/mocks) para `extract/watermark.py` e `extract/partition_manager.py` — hoje só existem scripts de validação ponta-a-ponta (`validate_phaseN.py`), sem cobertura unitária isolada.
- [x] Remover CTE órfã `stg_disciplinas` em `stg_operational_tables.sql` (definida mas nunca usada no `SELECT` final).
- [x] Otimizar o cálculo de WAU/MAU em `mrt_engagement.sql` (linhas 12-28) — hoje usa subquery correlacionada por linha (O(n²)-ish); considerar `array_agg` incremental ou pré-agregação.
- [x] Criar mais partições mensais fixas no DDL inicial (`warehouse/schema.sql` só tem `y2026m01` a `y2026m03` + `default`), ou garantir que `partition_manager.py` seja sempre chamado antes de qualquer carga.
- [x] Reduzir boilerplate duplicado de conexão Postgres (`PG_HOST = os.getenv(...)` repetido em quase todo script de `scripts/`) — extrair para um módulo `db.py` compartilhado.

---

## 🟢 Opcional

- [x] Adicionar `LICENSE` ao repositório (README diz "100% open-source" mas não há licença declarada).
- [x] Reduzir o tamanho dos commits futuros — hoje são 28 commits para todo o volume do projeto, cada um um "mega-commit" de fase inteira (`feat(phase-5): complete Data Quality suite with 46 dbt tests...`). Isso não mostra iteração real; prefira commits menores e mais frequentes daqui pra frente.
- [x] Gravar um GIF real do pipeline rodando (Airflow UI + Metabase real) para o README, complementando/substituindo as imagens fabricadas.
- [x] Automatizar a criação dos 6 dashboards no Metabase via API (`metabase/export_dashboards.json` já existe como esqueleto) em vez de manter só os specs em Markdown.


---

## Como usar este arquivo

1. Ataque primeiro os 🔴 — eles são o motivo da nota mais baixa e o que mais rapidamente derruba a credibilidade do projeto numa entrevista técnica.
2. Depois os 🟠, que são bugs/gaps reais mas não "mentiras estruturais".
3. 🟡 e 🟢 melhoram polimento e maturidade, mas não são bloqueantes.
4. Quando terminar um bloco (ou tudo), peça a reavaliação completa novamente — vou reler o código do zero e comparar com esta lista, sem levar em conta o que foi "prometido", só o que de fato está implementado.
