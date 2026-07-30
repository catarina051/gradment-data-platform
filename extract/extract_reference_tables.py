#!/usr/bin/env python3
"""
extract_reference_tables.py
---------------------------
Operational Reference Data Extractor for GradMent Data Platform (Phase 4).

Extracts operational database entity snapshots (usuarios, curriculo_disciplinas, ofertas_disciplinas)
into PostgreSQL staging tables, supporting both synthetic seeds and real lane extraction with `--full-refresh`.
"""

import sys
import os
import argparse
import psycopg2
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

MYSQL_HOST = os.getenv('MYSQL_HOST', '172.20.0.20')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'analytics_ro')
MYSQL_PASS = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DATABASE', 'gradment')

def ensure_operational_staging(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario BIGINT PRIMARY KEY,
                id_universidade BIGINT NOT NULL,
                id_curso BIGINT,
                perfil VARCHAR(32) NOT NULL,
                data_cadastro DATE NOT NULL,
                status VARCHAR(32) NOT NULL DEFAULT 'ativo'
            );
            CREATE TABLE IF NOT EXISTS curriculo_disciplinas (
                id_disciplina BIGINT PRIMARY KEY,
                codigo_disciplina VARCHAR(32) NOT NULL,
                nome_disciplina VARCHAR(255) NOT NULL,
                creditos INT NOT NULL DEFAULT 4,
                ch_total INT NOT NULL DEFAULT 60
            );
        """)
    conn.commit()

def run_extraction(source='synthetic', full_refresh=False, limit=None):
    print(f"\n======================================================================")
    print(f"Starting Operational Data Extraction | Source: {source.upper()} | Full Refresh: {full_refresh} | Limit: {limit}")
    print(f"======================================================================")

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    ensure_operational_staging(conn)

    users_data = []
    disciplines_data = []

    if source == 'synthetic':
        users_data = [
            (1, 1, 101, 'Aluno', '2026-01-01', 'ativo'),
            (2, 1, 101, 'Coordenador', '2025-06-15', 'ativo'),
            (3, 1, 102, 'Aluno', '2026-01-10', 'ativo')
        ]
        disciplines_data = [
            (101, 'MAT101', 'Cálculo I', 4, 60),
            (102, 'FIS101', 'Física Geral I', 4, 60),
            (103, 'INF110', 'Programação I', 4, 60)
        ]
        if limit:
            users_data = users_data[:limit]
            disciplines_data = disciplines_data[:limit]
    else:
        print(f"[EXTRACT] Real Lane mode: Connecting to MySQL ({MYSQL_HOST}:{MYSQL_PORT}) as '{MYSQL_USER}'...")
        import pymysql
        my_conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with my_conn.cursor() as my_cur:
                # Query users joining with usuario_academicos using ALLOWED NON-SENSITIVE COLUMNS ONLY
                # Excludes nome, email, senha, telefone, matricula per Anonymization policy
                q_users = """
                    SELECT u.id as id_usuario,
                           COALESCE(ua.faculdade_id, 1) as id_universidade,
                           ua.curso_id as id_curso,
                           'Aluno' as perfil,
                           DATE(u.created_at) as data_cadastro,
                           u.status
                    FROM usuarios u
                    LEFT JOIN usuario_academicos ua ON u.id = ua.usuario_id
                """
                if limit:
                    q_users += f" LIMIT {int(limit)}"
                my_cur.execute(q_users)
                for r in my_cur.fetchall():
                    users_data.append((
                        r['id_usuario'],
                        r['id_universidade'],
                        r['id_curso'],
                        r['perfil'],
                        str(r['data_cadastro']) if r['data_cadastro'] else '2026-01-01',
                        r['status'] or 'ativo'
                    ))

                # Query curriculo_disciplinas using allowed non-sensitive columns
                q_disc = "SELECT id, codigo, nome, 4 as creditos, COALESCE(carga_horaria, 60) as ch_total FROM curriculo_disciplinas"
                if limit:
                    q_disc += f" LIMIT {int(limit)}"
                my_cur.execute(q_disc)
                for r in my_cur.fetchall():
                    disciplines_data.append((
                        r['id'],
                        r['codigo'] or f"DISC{r['id']}",
                        r['nome'] or f"Disciplina {r['id']}",
                        r['creditos'],
                        r['ch_total']
                    ))
        finally:
            my_conn.close()

    with conn.cursor() as cur:
        for u in users_data:
            cur.execute("""
                INSERT INTO usuarios (id_usuario, id_universidade, id_curso, perfil, data_cadastro, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_usuario) DO UPDATE SET perfil = EXCLUDED.perfil, status = EXCLUDED.status;
            """, u)
            
        for d in disciplines_data:
            cur.execute("""
                INSERT INTO curriculo_disciplinas (id_disciplina, codigo_disciplina, nome_disciplina, creditos, ch_total)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id_disciplina) DO NOTHING;
            """, d)

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Operational reference data extracted ({len(users_data)} users, {len(disciplines_data)} disciplines) and staged successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GradMent Operational Data Extractor")
    parser.add_argument('--source', choices=['synthetic', 'real'], default='synthetic')
    parser.add_argument('--full-refresh', action='store_true')
    parser.add_argument('--limit', type=int, default=None, help="Limit rows extracted for controlled runs")
    args = parser.parse_args()
    run_extraction(source=args.source, full_refresh=args.full_refresh, limit=args.limit)

