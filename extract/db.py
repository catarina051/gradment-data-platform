"""
Shared Database Connection Module for GradMent Data Platform
Handles environment variable fallbacks (POSTGRES_* and PG_*) and provides unified PostgreSQL connection helper.
"""

import os
import psycopg2

def get_pg_config() -> dict:
    return {
        'host': os.getenv('POSTGRES_HOST') or os.getenv('PG_HOST') or 'localhost',
        'port': int(os.getenv('POSTGRES_PORT') or os.getenv('PG_PORT') or 5432),
        'user': os.getenv('POSTGRES_USER') or os.getenv('PG_USER') or 'postgres',
        'password': os.getenv('POSTGRES_PASSWORD') or os.getenv('PG_PASS') or 'postgres',
        'dbname': os.getenv('POSTGRES_DB') or os.getenv('PG_DB') or 'gradment_dw_test'
    }

def get_db_connection():
    cfg = get_pg_config()
    return psycopg2.connect(**cfg)
