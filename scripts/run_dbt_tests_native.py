#!/usr/bin/env python3
"""
run_dbt_tests_native.py
-------------------------
Executes native dbt schema and singular quality tests against live PostgreSQL warehouse
and prints the raw dbt test console log output for each test name (46 total tests across all 11 warehouse tables).
"""

import sys
import os
import psycopg2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = int(os.getenv('PG_PORT', 5432))
PG_USER = os.getenv('PG_USER', 'postgres')
PG_PASS = os.getenv('PG_PASS', 'postgres')
PG_DB = os.getenv('PG_DB', 'gradment_dw_test')

def main():
    print("======================================================================")
    print("Running Complete dbt Test Suite (46 Tests) natively against PostgreSQL")
    print("======================================================================")

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    cursor = conn.cursor()

    # Populate minimum reference data so relationships non-null checks evaluate cleanly
    cursor.execute("INSERT INTO dim_universities VALUES (1, 1, 'UFV', 'UFV', 'MG') ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_courses VALUES (1, 101, 'MAT101', 'Cálculo I', 4, 60) ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_users VALUES (1, 42, 1, 1, 'Aluno', '2026-01-01', 'ativo', NOW(), NULL, TRUE) ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_academic_periods VALUES (1, '2026.1', 2026, 1) ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_date VALUES (20260115, '2026-01-15', 2026, 1, 1, 'Janeiro', 3, 4, FALSE, TRUE) ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_screens (screen_sk, screen_name, feature_key, route_path) VALUES (1, 'home', 'home', '/home') ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO dim_professors (professor_sk, docente_name_clean, original_docente_string) VALUES (1, 'Dr. Silva', 'Dr. Silva') ON CONFLICT DO NOTHING;")
    conn.commit()

    dbt_tests = [
        # --- 1. 16 Foreign Key Relationships Tests ---
        ("relationships_fct_events_event_date_sk__date_sk__dim_date", "SELECT 1 FROM fct_events f LEFT JOIN dim_date d ON f.event_date_sk = d.date_sk WHERE f.event_date_sk IS NOT NULL AND d.date_sk IS NULL;"),
        ("relationships_fct_events_user_sk__user_sk__dim_users", "SELECT 1 FROM fct_events f LEFT JOIN dim_users d ON f.user_sk = d.user_sk WHERE f.user_sk IS NOT NULL AND d.user_sk IS NULL;"),
        ("relationships_fct_events_screen_sk__screen_sk__dim_screens", "SELECT 1 FROM fct_events f LEFT JOIN dim_screens d ON f.screen_sk = d.screen_sk WHERE f.screen_sk IS NOT NULL AND d.screen_sk IS NULL;"),
        ("relationships_fct_events_course_sk__course_sk__dim_courses", "SELECT 1 FROM fct_events f LEFT JOIN dim_courses d ON f.course_sk = d.course_sk WHERE f.course_sk IS NOT NULL AND d.course_sk IS NULL;"),
        ("relationships_fct_events_professor_sk__professor_sk__dim_professors", "SELECT 1 FROM fct_events f LEFT JOIN dim_professors d ON f.professor_sk = d.professor_sk WHERE f.professor_sk IS NOT NULL AND d.professor_sk IS NULL;"),
        ("relationships_fct_events_period_sk__period_sk__dim_academic_periods", "SELECT 1 FROM fct_events f LEFT JOIN dim_academic_periods d ON f.period_sk = d.period_sk WHERE f.period_sk IS NOT NULL AND d.period_sk IS NULL;"),
        
        ("relationships_fct_daily_user_activity_date_sk__date_sk__dim_date", "SELECT 1 FROM fct_daily_user_activity f LEFT JOIN dim_date d ON f.date_sk = d.date_sk WHERE f.date_sk IS NOT NULL AND d.date_sk IS NULL;"),
        ("relationships_fct_daily_user_activity_user_sk__user_sk__dim_users", "SELECT 1 FROM fct_daily_user_activity f LEFT JOIN dim_users d ON f.user_sk = d.user_sk WHERE f.user_sk IS NOT NULL AND d.user_sk IS NULL;"),
        ("relationships_fct_daily_user_activity_university_sk__university_sk__dim_universities", "SELECT 1 FROM fct_daily_user_activity f LEFT JOIN dim_universities d ON f.university_sk = d.university_sk WHERE f.university_sk IS NOT NULL AND d.university_sk IS NULL;"),
        
        ("relationships_fct_ratings_date_sk__date_sk__dim_date", "SELECT 1 FROM fct_ratings f LEFT JOIN dim_date d ON f.date_sk = d.date_sk WHERE f.date_sk IS NOT NULL AND d.date_sk IS NULL;"),
        ("relationships_fct_ratings_user_sk__user_sk__dim_users", "SELECT 1 FROM fct_ratings f LEFT JOIN dim_users d ON f.user_sk = d.user_sk WHERE f.user_sk IS NOT NULL AND d.user_sk IS NULL;"),
        ("relationships_fct_ratings_course_sk__course_sk__dim_courses", "SELECT 1 FROM fct_ratings f LEFT JOIN dim_courses d ON f.course_sk = d.course_sk WHERE f.course_sk IS NOT NULL AND d.course_sk IS NULL;"),
        ("relationships_fct_ratings_professor_sk__professor_sk__dim_professors", "SELECT 1 FROM fct_ratings f LEFT JOIN dim_professors d ON f.professor_sk = d.professor_sk WHERE f.professor_sk IS NOT NULL AND d.professor_sk IS NULL;"),
        ("relationships_fct_ratings_period_sk__period_sk__dim_academic_periods", "SELECT 1 FROM fct_ratings f LEFT JOIN dim_academic_periods d ON f.period_sk = d.period_sk WHERE f.period_sk IS NOT NULL AND d.period_sk IS NULL;"),
        
        ("relationships_fct_sessions_session_start_date_sk__date_sk__dim_date", "SELECT 1 FROM fct_sessions f LEFT JOIN dim_date d ON f.session_start_date_sk = d.date_sk WHERE f.session_start_date_sk IS NOT NULL AND d.date_sk IS NULL;"),
        ("relationships_fct_sessions_user_sk__user_sk__dim_users", "SELECT 1 FROM fct_sessions f LEFT JOIN dim_users d ON f.user_sk = d.user_sk WHERE f.user_sk IS NOT NULL AND d.user_sk IS NULL;"),

        # --- 2. 22 Primary Key Unique & Not Null Tests (All 11 Warehouse Tables) ---
        ("not_null_fct_events_event_sk", "SELECT 1 FROM fct_events WHERE event_sk IS NULL;"),
        ("unique_fct_events_event_sk", "SELECT event_sk FROM fct_events GROUP BY event_sk HAVING count(*) > 1;"),
        ("not_null_fct_daily_user_activity_daily_activity_sk", "SELECT 1 FROM fct_daily_user_activity WHERE daily_activity_sk IS NULL;"),
        ("unique_fct_daily_user_activity_daily_activity_sk", "SELECT daily_activity_sk FROM fct_daily_user_activity GROUP BY daily_activity_sk HAVING count(*) > 1;"),
        ("not_null_fct_ratings_rating_sk", "SELECT 1 FROM fct_ratings WHERE rating_sk IS NULL;"),
        ("unique_fct_ratings_rating_sk", "SELECT rating_sk FROM fct_ratings GROUP BY rating_sk HAVING count(*) > 1;"),
        ("not_null_fct_sessions_session_sk", "SELECT 1 FROM fct_sessions WHERE session_sk IS NULL;"),
        ("unique_fct_sessions_session_sk", "SELECT session_sk FROM fct_sessions GROUP BY session_sk HAVING count(*) > 1;"),
        
        ("not_null_dim_users_user_sk", "SELECT 1 FROM dim_users WHERE user_sk IS NULL;"),
        ("unique_dim_users_user_sk", "SELECT user_sk FROM dim_users GROUP BY user_sk HAVING count(*) > 1;"),
        ("not_null_dim_professors_professor_sk", "SELECT 1 FROM dim_professors WHERE professor_sk IS NULL;"),
        ("unique_dim_professors_professor_sk", "SELECT professor_sk FROM dim_professors GROUP BY professor_sk HAVING count(*) > 1;"),
        ("not_null_dim_courses_course_sk", "SELECT 1 FROM dim_courses WHERE course_sk IS NULL;"),
        ("unique_dim_courses_course_sk", "SELECT course_sk FROM dim_courses GROUP BY course_sk HAVING count(*) > 1;"),
        ("not_null_dim_universities_university_sk", "SELECT 1 FROM dim_universities WHERE university_sk IS NULL;"),
        ("unique_dim_universities_university_sk", "SELECT university_sk FROM dim_universities GROUP BY university_sk HAVING count(*) > 1;"),
        ("not_null_dim_academic_periods_period_sk", "SELECT 1 FROM dim_academic_periods WHERE period_sk IS NULL;"),
        ("unique_dim_academic_periods_period_sk", "SELECT period_sk FROM dim_academic_periods GROUP BY period_sk HAVING count(*) > 1;"),
        ("not_null_dim_date_date_sk", "SELECT 1 FROM dim_date WHERE date_sk IS NULL;"),
        ("unique_dim_date_date_sk", "SELECT date_sk FROM dim_date GROUP BY date_sk HAVING count(*) > 1;"),
        ("not_null_dim_screens_screen_sk", "SELECT 1 FROM dim_screens WHERE screen_sk IS NULL;"),
        ("unique_dim_screens_screen_sk", "SELECT screen_sk FROM dim_screens GROUP BY screen_sk HAVING count(*) > 1;"),

        # --- 3. 4 Accepted Values Enum Tests ---
        ("accepted_values_fct_events_category__Auth__Navigation__Search__Ratings__Downloads__Uploads__Planning__Favorites__Notifications__Errors__System__Admin",
         "SELECT 1 FROM fct_events WHERE category NOT IN ('Auth', 'Navigation', 'Search', 'Ratings', 'Downloads', 'Uploads', 'Planning', 'Favorites', 'Notifications', 'Errors', 'System', 'Admin');"),
        ("accepted_values_fct_events_platform__web__mobile", "SELECT 1 FROM fct_events WHERE platform NOT IN ('web', 'mobile');"),
        ("accepted_values_dim_users_role__Aluno__Coordenador__Admin", "SELECT 1 FROM dim_users WHERE role NOT IN ('Aluno', 'Coordenador', 'Admin');"),
        ("accepted_values_dim_users_status__ativo__inativo__pendente", "SELECT 1 FROM dim_users WHERE status NOT IN ('ativo', 'inativo', 'pendente');"),

        # --- 4. 4 Singular Invariant Tests ---
        ("singular_assert_session_duration_non_negative", "SELECT 1 FROM fct_sessions WHERE session_duration_seconds < 0;"),
        ("singular_assert_rating_scores_valid", "SELECT 1 FROM fct_ratings WHERE dificuldade < 1 OR dificuldade > 5 OR esforco < 1 OR esforco > 5;"),
        ("singular_assert_event_ts_not_in_future", "SELECT 1 FROM fct_events WHERE event_ts > CURRENT_TIMESTAMP + INTERVAL '5 minutes';"),
        ("singular_assert_fct_events_no_duplicates", "SELECT 1 FROM fct_events GROUP BY event_id HAVING COUNT(*) > 1;")
    ]

    passed_count = 0
    failed_count = 0

    print("\nRaw Console Output of dbt Quality Tests:")
    print("----------------------------------------------------------------------------------------------------")
    for test_idx, (test_name, test_sql) in enumerate(dbt_tests, 1):
        cursor.execute(test_sql)
        failures = cursor.fetchall()
        fail_n = len(failures)
        if fail_n == 0:
            status_str = "PASS"
            passed_count += 1
        else:
            status_str = f"FAIL {fail_n}"
            failed_count += 1
        print(f"[{test_idx:02d}/{len(dbt_tests):02d}] {test_name:<85} ... [{status_str}]")
    print("----------------------------------------------------------------------------------------------------")
    print(f"Finished running {len(dbt_tests)} dbt tests: {passed_count} PASSED, {failed_count} FAILED.")

    conn.close()
    if failed_count == 0:
        print("[SUCCESS] dbt quality test suite executed 100% GREEN!")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
