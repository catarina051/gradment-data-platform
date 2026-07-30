#!/usr/bin/env python3
"""
alerts.py
---------
Monitoring and Failure Notification Engine for GradMent Data Platform.
Handles pipeline failure triggers, data quality breaches, and SLA threshold violations.
"""

import sys
import os
import json
from datetime import datetime

def send_alert(alert_type, message, details=None):
    alert_payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'platform': 'GradMent Data Platform',
        'alert_type': alert_type,
        'message': message,
        'details': details or {}
    }
    
    # Log alert payload
    print(f"\n[ALERT TRIGGERED - {alert_type.upper()}] {message}")
    if details:
        print(f"  Details: {json.dumps(details)}")
    
    return alert_payload

def trigger_sla_breach_alert(metric_name, actual_val, expected_sla):
    return send_alert(
        'SLA_BREACH',
        f"SLA violation detected for metric '{metric_name}'",
        {'actual_value': actual_val, 'expected_sla': expected_sla}
    )

def trigger_pipeline_failure_alert(dag_id, run_id, error_msg):
    return send_alert(
        'PIPELINE_FAILURE',
        f"Airflow DAG '{dag_id}' run '{run_id}' failed",
        {'error_message': error_msg}
    )

if __name__ == '__main__':
    send_alert('TEST_HEALTH_ALERT', 'System alert mechanism initialized successfully.')
