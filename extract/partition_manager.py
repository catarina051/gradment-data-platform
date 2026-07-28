#!/usr/bin/env python3
"""
partition_manager.py
---------------------
Dynamic PostgreSQL Range Partition Manager for GradMent Data Platform (Phase 4).

Pre-creates monthly range partitions on `fct_events` (e.g., `fct_events_y2026m04`) for target
timestamps before data loading occurs. Prevents default partition fallback and maintains EXPLAIN partition pruning performance.
"""

import sys
import os
import re
from datetime import datetime, timezone
import psycopg2

def ensure_monthly_partition(conn, target_dt: datetime):
    """
    Guarantees that a declarative child partition for target_dt's year and month exists on fct_events.
    """
    year = target_dt.year
    month = target_dt.month
    
    partition_name = f"fct_events_y{year}m{month:02d}"
    
    start_str = f"{year}-{month:02d}-01 00:00:00+00"
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
        
    end_str = f"{next_year}-{next_month:02d}-01 00:00:00+00"
    
    with conn.cursor() as cur:
        # Check if table already exists in pg_tables
        cur.execute("SELECT 1 FROM pg_tables WHERE tablename = %s;", (partition_name,))
        if cur.fetchone():
            return partition_name, False # Already existed
            
        # Create partition
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF fct_events
            FOR VALUES FROM ('{start_str}') TO ('{end_str}');
        """
        cur.execute(create_sql)
        
        # Create index on event_ts for the child partition
        idx_sql = f"CREATE INDEX IF NOT EXISTS {partition_name}_event_ts_idx ON {partition_name}(event_ts);"
        cur.execute(idx_sql)
        
    conn.commit()
    print(f"[PARTITION MANAGER] Dynamically created PostgreSQL partition '{partition_name}' for range {start_str} to {end_str}.")
    return partition_name, True

def ensure_partitions_for_timestamps(conn, timestamps):
    created_count = 0
    checked_partitions = set()
    for ts in timestamps:
        if isinstance(ts, str):
            # Parse ISO string
            ts_clean = ts.replace('Z', '+00:00')
            dt = datetime.fromisoformat(ts_clean)
        else:
            dt = ts
            
        key = (dt.year, dt.month)
        if key not in checked_partitions:
            p_name, newly_created = ensure_monthly_partition(conn, dt)
            checked_partitions.add(key)
            if newly_created:
                created_count += 1
    return created_count
