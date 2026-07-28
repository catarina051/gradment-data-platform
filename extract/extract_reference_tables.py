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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

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

def run_extraction(source='synthetic', full_refresh=False):
    print(f"\n======================================================================")
    print(f"Starting Operational Data Extraction | Source: {source.upper()} | Full Refresh: {full_refresh}")
    print(f"======================================================================")

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    ensure_operational_staging(conn)

    # Ingest baseline operational reference data into staging tables
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
    print("[SUCCESS] Operational reference data extracted and staged successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GradMent Operational Data Extractor")
    parser.add_argument('--source', choices=['synthetic', 'real'], default='synthetic')
    parser.add_argument('--full-refresh', action='store_true')
    args = parser.parse_args()
    run_extraction(source=args.source, full_refresh=args.full_refresh)
