#!/usr/bin/env python3
"""
inspect_showcase.py
-------------------
Prints concrete empirical proof of showcase/data_snapshot.json content
and showcase/index.html JavaScript fetch/parse logic.
"""

import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_PATH = os.path.join(PROJECT_ROOT, 'showcase', 'data_snapshot.json')
HTML_PATH = os.path.join(PROJECT_ROOT, 'showcase', 'index.html')

def main():
    print("======================================================================")
    print("GradMent Data Platform — Showcase Empirical Proof Inspection")
    print("======================================================================")

    # 1. Inspect data_snapshot.json snippet
    print(f"\n1. RAW JSON SNIPPET FROM {SNAPSHOT_PATH}:")
    with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cat in ['engagement', 'product', 'retention', 'quality']:
        rows = data.get(cat, [])
        first_row = rows[0] if rows else {}
        print(f"  Category '{cat}' (first row): {first_row}")

    # 2. Inspect index.html JS fetch snippet
    print(f"\n2. JAVASCRIPT FETCH/DOM PARSING SNIPPET FROM {HTML_PATH}:")
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    js_start = html.find("<script>")
    js_end = html.find("</script>")
    if js_start != -1 and js_end != -1:
        print(html[js_start:js_end+9])

if __name__ == '__main__':
    main()
