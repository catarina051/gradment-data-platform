#!/usr/bin/env python3
"""
check_metrics_drift.py
-----------------------
Automated Metric Name Drift Checker for Phase 7.

Parses Section 19 metric tables from `c:/xampp/htdocs/gradment/IMPLEMENTATION_PLAN.md`,
extracts every defined metric name across all 9 categories (19.1 - 19.9),
and compares them against `dbt_project/models/marts/metrics/metrics_catalog.yml`
and `docs/metrics_catalog.md`, asserting 100% metric coverage with zero missing metric names.
"""

import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_PLAN_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), 'IMPLEMENTATION_PLAN.md')
YML_CATALOG_PATH = os.path.join(PROJECT_ROOT, 'dbt_project', 'models', 'marts', 'metrics', 'metrics_catalog.yml')
DOCS_CATALOG_PATH = os.path.join(PROJECT_ROOT, 'docs', 'metrics_catalog.md')

def parse_master_plan_metrics():
    if not os.path.exists(MASTER_PLAN_PATH):
        raise FileNotFoundError(f"Master plan not found at {MASTER_PLAN_PATH}")

    with open(MASTER_PLAN_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Section 19 block (between Section 19 header and Section 20 header)
    sec19_match = re.search(r'### 19\.1 Acquisition.*?(?=## 20\. Event Catalog)', content, re.DOTALL)
    if not sec19_match:
        raise ValueError("Could not locate Section 19 metric tables in IMPLEMENTATION_PLAN.md")

    sec19_text = sec19_match.group(0)

    categories = {}
    current_cat = None

    for line in sec19_text.splitlines():
        line_str = line.strip()
        cat_match = re.match(r'^### (19\.\d+ \w+.*)', line_str)
        if cat_match:
            current_cat = cat_match.group(1)
            categories[current_cat] = []
            continue

        if line_str.startswith('|') and not line_str.startswith('| Metric') and not line_str.startswith('|---'):
            parts = [p.strip() for p in line_str.split('|')[1:-1]]
            if parts and parts[0] and parts[0] != 'Metric':
                metric_name = parts[0]
                if current_cat:
                    categories[current_cat].append(metric_name)

    return categories

def slugify(name):
    # Convert metric name like "Total Users" or "D1 / D7 / D14 / D30 Retention" to normalized snake_case key
    clean = name.lower()
    clean = re.sub(r'[^a-z0-9]+', '_', clean).strip('_')
    return clean

def main():
    print("======================================================================")
    print("GradMent Data Platform — Metric Name Drift Checker (Section 19 Parser)")
    print("======================================================================")

    cat_metrics = parse_master_plan_metrics()
    total_parsed = sum(len(v) for v in cat_metrics.values())

    print(f"\n[PARSER] Extracted {total_parsed} metrics across {len(cat_metrics)} Section 19 categories from IMPLEMENTATION_PLAN.md:\n")
    all_master_metrics = []
    for cat, metrics in cat_metrics.items():
        print(f"  Category {cat} ({len(metrics)} metrics):")
        for m in metrics:
            print(f"    - {m} (slug: {slugify(m)})")
            all_master_metrics.append(m)

    if not os.path.exists(YML_CATALOG_PATH):
        print(f"\n[FAIL] Catalog YAML missing at {YML_CATALOG_PATH}")
        sys.exit(1)

    with open(YML_CATALOG_PATH, 'r', encoding='utf-8') as f:
        yml_text = f.read()

    # Extract all name: 'slug' or name: slug entries
    yml_metric_names = re.findall(r"name:\s*['\"]?([a-z0-9_]+)['\"]?", yml_text)

    with open(DOCS_CATALOG_PATH, 'r', encoding='utf-8') as f:
        docs_text = f.read().lower()

    missing_in_yml = []
    missing_in_docs = []

    for m in all_master_metrics:
        slug = slugify(m)
        if slug not in yml_metric_names:
            missing_in_yml.append(f"{m} (expected slug '{slug}')")
        if m.lower() not in docs_text and slug not in docs_text:
            missing_in_docs.append(m)

    print("\n----------------------------------------------------------------------")
    if missing_in_yml:
        print(f"[FAIL] Missing in metrics_catalog.yml ({len(missing_in_yml)}):")
        for m in missing_in_yml:
            print(f"  - {m}")

    if missing_in_docs:
        print(f"[FAIL] Missing in docs/metrics_catalog.md ({len(missing_in_docs)}):")
        for m in missing_in_docs:
            print(f"  - {m}")

    if not missing_in_yml and not missing_in_docs:
        print(f"[SUCCESS] ZERO METRIC DRIFT DETECTED!")
        print(f"All {total_parsed} Section 19 metrics parsed from IMPLEMENTATION_PLAN.md match 100% with metrics_catalog.yml and docs/metrics_catalog.md.")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
