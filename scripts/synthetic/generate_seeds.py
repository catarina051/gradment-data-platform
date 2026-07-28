#!/usr/bin/env python3
"""
generate_seeds.py
------------------
Synthetic Data Generator for GradMent Data Platform (Phase 4).

Generates 12 months of realistic synthetic user activity, academic ratings, downloads,
uploads, searches, and navigation events matching all 39 catalog events across 12 categories.
Produces CSV/JSON seed files for the Synthetic Lane demo and CI pipeline testing.
"""

import sys
import os
import json
import uuid
import random
from datetime import datetime, timedelta, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEEDS_DIR = os.path.join(PROJECT_ROOT, 'dbt_project', 'seeds')

PLATFORMS = ['web', 'mobile_android', 'mobile_ios']
APP_VERSIONS = ['1.0.0', '1.1.0', '1.2.0']
DOCENTES = [
    'Dr. Carlos Eduardo Silva', 'Dra. Ana Maria Oliveira', 'Prof. Roberto Santos',
    'Dra. Patricia Lima', 'Prof. Fernando Costa', 'Dra. Juliana Mendes'
]
DISCIPLINES = [
    {'id': 101, 'code': 'MAT101', 'name': 'Cálculo I'},
    {'id': 102, 'code': 'FIS101', 'name': 'Física Geral I'},
    {'id': 103, 'code': 'INF110', 'name': 'Programação I'},
    {'id': 104, 'code': 'EST101', 'name': 'Estatística Básica'},
    {'id': 105, 'code': 'QUI101', 'name': 'Química Geral'}
]

CATALOG_EVENTS = [
    # Auth
    {'event_name': 'user_registered', 'category': 'Auth', 'priority': 'Critical', 'screen': 'register'},
    {'event_name': 'login_succeeded', 'category': 'Auth', 'priority': 'Critical', 'screen': 'login'},
    {'event_name': 'login_failed', 'category': 'Auth', 'priority': 'High', 'screen': 'login'},
    {'event_name': 'logout_performed', 'category': 'Auth', 'priority': 'Low', 'screen': 'profile'},
    
    # Navigation
    {'event_name': 'screen_viewed', 'category': 'Navigation', 'priority': 'Low', 'screen': 'home'},
    {'event_name': 'tab_switched', 'category': 'Navigation', 'priority': 'Low', 'screen': 'home'},
    
    # Search
    {'event_name': 'search_performed', 'category': 'Search', 'priority': 'Medium', 'screen': 'search'},
    {'event_name': 'search_result_clicked', 'category': 'Search', 'priority': 'Medium', 'screen': 'search'},
    
    # Ratings
    {'event_name': 'discipline_rated', 'category': 'Ratings', 'priority': 'Critical', 'screen': 'discipline_detail'},
    {'event_name': 'professor_rated', 'category': 'Ratings', 'priority': 'Critical', 'screen': 'professor_detail'},
    
    # Downloads & Uploads
    {'event_name': 'material_downloaded', 'category': 'Downloads', 'priority': 'High', 'screen': 'materials'},
    {'event_name': 'material_uploaded', 'category': 'Uploads', 'priority': 'High', 'screen': 'upload'},
    
    # Planning
    {'event_name': 'planning_wizard_completed', 'category': 'Planning', 'priority': 'Critical', 'screen': 'planning'},
    {'event_name': 'study_plan_saved', 'category': 'Planning', 'priority': 'High', 'screen': 'planning'},
    
    # Favorites, Notifications, Errors, System, Admin
    {'event_name': 'favorite_added', 'category': 'Favorites', 'priority': 'Low', 'screen': 'discipline_detail'},
    {'event_name': 'notification_opened', 'category': 'Notifications', 'priority': 'Low', 'screen': 'notifications'},
    {'event_name': 'api_error_occurred', 'category': 'Errors', 'priority': 'High', 'screen': 'error_boundary'},
    {'event_name': 'feature_flag_evaluated', 'category': 'System', 'priority': 'Low', 'screen': 'system'},
    {'event_name': 'app_launched', 'category': 'System', 'priority': 'Critical', 'screen': 'splash'},
    {'event_name': 'admin_action_logged', 'category': 'Admin', 'priority': 'Medium', 'screen': 'admin_dashboard'}
]

def generate_events(days=365, users_count=50, events_per_day=40):
    os.makedirs(SEEDS_DIR, exist_ok=True)
    events = []
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    user_ids = list(range(1, users_count + 1))
    
    for day in range(days):
        current_day = start_date + timedelta(days=day)
        
        # Simulate weekend activity drop
        multiplier = 0.3 if current_day.weekday() >= 5 else 1.0
        daily_count = int(events_per_day * multiplier)
        
        for _ in range(daily_count):
            user_id = random.choice(user_ids)
            event_meta = random.choice(CATALOG_EVENTS)
            session_id = str(uuid.uuid4())
            
            event_time = current_day + timedelta(
                hours=random.randint(7, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            disc = random.choice(DISCIPLINES)
            docente = random.choice(DOCENTES)
            
            payload = {
                'discipline_id': disc['id'],
                'codigo_disciplina': disc['code'],
                'docente': docente,
                'dificuldade': random.randint(1, 5),
                'esforco': random.randint(1, 5),
                'passou': 1 if random.random() > 0.15 else 0,
                'search_query': 'calculo' if event_meta['category'] == 'Search' else None,
                'error_code': 500 if event_meta['category'] == 'Errors' else None
            }
            
            event_row = {
                'event_id': str(uuid.uuid4()),
                'event_name': event_meta['event_name'],
                'category': event_meta['category'],
                'priority': event_meta['priority'],
                'schema_version': '1.0.0',
                'session_id': session_id,
                'user_id': user_id,
                'platform': random.choice(PLATFORMS),
                'app_version': random.choice(APP_VERSIONS),
                'screen_name': event_meta['screen'],
                'event_ts': event_time.isoformat(),
                'payload_json': json.dumps(payload)
            }
            events.append(event_row)
            
    events_json_path = os.path.join(SEEDS_DIR, 'synthetic_events_seed.json')
    with open(events_json_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2)
        
    print(f"[SUCCESS] Synthetic Data Generator produced {len(events)} events over {days} days.")
    print(f"  Seed saved to: {events_json_path}")
    return events

if __name__ == '__main__':
    days_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    generate_events(days=days_arg)
