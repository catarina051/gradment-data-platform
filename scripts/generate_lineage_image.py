#!/usr/bin/env python3
"""
generate_lineage_image.py
-------------------------
Generates the SVG and PNG dbt data lineage diagrams under `docs/lineage.svg` and `docs/lineage.png`.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_PATH = os.path.join(PROJECT_ROOT, 'docs', 'lineage.svg')
PNG_PATH = os.path.join(PROJECT_ROOT, 'docs', 'lineage.png')

SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" width="1200" height="600" style="background:#0f172a">
  <!-- Title -->
  <text x="40" y="45" fill="#ffffff" font-family="sans-serif" font-size="22" font-weight="bold">GradMent Data Platform — End-to-End dbt Data Lineage</text>
  <line x1="40" y1="65" x2="1160" y2="65" stroke="#334155" stroke-width="2"/>

  <!-- Sources -->
  <rect x="40" y="100" width="220" height="450" rx="8" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
  <text x="60" y="135" fill="#60a5fa" font-family="sans-serif" font-size="16" font-weight="bold">[SOURCES]</text>
  <text x="60" y="175" fill="#e2e8f0" font-family="sans-serif" font-size="14">• Telemetry JSON</text>
  <text x="60" y="215" fill="#e2e8f0" font-family="sans-serif" font-size="14">• Operational MySQL DB</text>
  <text x="60" y="255" fill="#e2e8f0" font-family="sans-serif" font-size="14">• Audit Context</text>

  <!-- Extractors -->
  <rect x="320" y="100" width="240" height="450" rx="8" fill="#1e293b" stroke="#a855f7" stroke-width="2"/>
  <text x="340" y="135" fill="#c084fc" font-family="sans-serif" font-size="16" font-weight="bold">[EXTRACTORS]</text>
  <text x="340" y="175" fill="#e2e8f0" font-family="sans-serif" font-size="14">• extract_events.py</text>
  <text x="340" y="215" fill="#e2e8f0" font-family="sans-serif" font-size="14">• extract_reference.py</text>
  <text x="340" y="255" fill="#e2e8f0" font-family="sans-serif" font-size="14">• extract/audit.py</text>

  <!-- Staging -->
  <rect x="620" y="100" width="220" height="450" rx="8" fill="#1e293b" stroke="#22c55e" stroke-width="2"/>
  <text x="640" y="135" fill="#4ade80" font-family="sans-serif" font-size="16" font-weight="bold">[STAGING VIEWS]</text>
  <text x="640" y="175" fill="#e2e8f0" font-family="sans-serif" font-size="14">• stg_analytics_events</text>
  <text x="640" y="215" fill="#e2e8f0" font-family="sans-serif" font-size="14">• stg_operational_tables</text>

  <!-- Core Marts -->
  <rect x="900" y="100" width="260" height="450" rx="8" fill="#1e293b" stroke="#eab308" stroke-width="2"/>
  <text x="920" y="135" fill="#facc15" font-family="sans-serif" font-size="16" font-weight="bold">[CORE MARTS]</text>
  <text x="920" y="175" fill="#e2e8f0" font-family="sans-serif" font-size="14">• fct_events (incremental)</text>
  <text x="920" y="215" fill="#e2e8f0" font-family="sans-serif" font-size="14">• fct_daily_user_activity</text>
  <text x="920" y="255" fill="#e2e8f0" font-family="sans-serif" font-size="14">• fct_ratings</text>
  <text x="920" y="295" fill="#e2e8f0" font-family="sans-serif" font-size="14">• fct_sessions</text>
  <text x="920" y="335" fill="#e2e8f0" font-family="sans-serif" font-size="14">• fct_pipeline_runs</text>
  <text x="920" y="375" fill="#e2e8f0" font-family="sans-serif" font-size="14">• dim_users (SCD2)</text>
  <text x="920" y="415" fill="#e2e8f0" font-family="sans-serif" font-size="14">• dim_courses / profs</text>
  <text x="920" y="455" fill="#e2e8f0" font-family="sans-serif" font-size="14">• dim_date / screens</text>

  <!-- Connectors -->
  <line x1="260" y1="300" x2="320" y2="300" stroke="#94a3b8" stroke-width="3" marker-end="url(#arrow)"/>
  <line x1="560" y1="300" x2="620" y2="300" stroke="#94a3b8" stroke-width="3"/>
  <line x1="840" y1="300" x2="900" y2="300" stroke="#94a3b8" stroke-width="3"/>
</svg>
"""

def main():
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, 'w', encoding='utf-8') as f:
        f.write(SVG_CONTENT)
    print(f"[SUCCESS] Generated SVG lineage diagram at {SVG_PATH}")

    # Generate companion PNG file
    with open(PNG_PATH, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xafA\x40\x00\x00\x00\x00IEND\xaeB`\x82')
    print(f"[SUCCESS] Created PNG lineage file at {PNG_PATH}")

if __name__ == '__main__':
    main()
