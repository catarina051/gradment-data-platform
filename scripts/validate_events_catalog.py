#!/usr/bin/env python3
"""
GradMent Data Platform — Events Catalog Validation Script
Validates events_catalog.yml against contract rules, payload data types, and envelope JSON schema.
Built using standard library Python to ensure zero external dependency failures.
"""

import sys
import re
import json
from pathlib import Path

ALLOWED_PRIORITIES = {"Critical", "High", "Medium", "Low"}
ALLOWED_CATEGORIES = {
    "Authentication & Registration",
    "Navigation",
    "Search",
    "Ratings",
    "Downloads",
    "Uploads",
    "Planning",
    "Favorites",
    "Notifications",
    "Errors",
    "System",
    "Admin"
}
ALLOWED_TYPES = {"integer", "string", "boolean", "number", "array", "object"}

def parse_events_yml(yml_content: str) -> list:
    """Simple standard-library YAML parser for events_catalog.yml format."""
    events = []
    current_event = None

    for line in yml_content.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        if line_str.startswith("- event_name:"):
            if current_event:
                events.append(current_event)
            event_name = line_str.split(":", 1)[1].strip()
            current_event = {
                "event_name": event_name,
                "payload": {}
            }
        elif current_event:
            if ":" in line_str:
                key, val = [part.strip() for part in line_str.split(":", 1)]
                if key in ["category", "priority", "description", "trigger"]:
                    current_event[key] = val
                elif key == "schema_version":
                    try:
                        current_event[key] = int(val)
                    except ValueError:
                        current_event[key] = val
                elif "type:" in val:
                    # Payload field attribute
                    type_match = re.search(r"type:\s*([a-z]+)", val)
                    if type_match:
                        field_type = type_match.group(1)
                        current_event["payload"][key] = {"type": field_type}

    if current_event:
        events.append(current_event)

    return events

def validate_catalog(catalog_path: Path, envelope_path: Path) -> bool:
    print(f"Validating Event Catalog: {catalog_path}")
    print(f"Validating Envelope Schema: {envelope_path}")

    if not catalog_path.exists():
        print(f"Error: Catalog file not found at {catalog_path}", file=sys.stderr)
        return False

    if not envelope_path.exists():
        print(f"Error: Envelope schema file not found at {envelope_path}", file=sys.stderr)
        return False

    # 1. Validate Envelope JSON Schema
    try:
        envelope_content = envelope_path.read_text(encoding="utf-8")
        json.loads(envelope_content)
        print("  - Envelope JSON Schema syntax: OK")
    except Exception as e:
        print(f"Error parsing envelope JSON schema: {e}", file=sys.stderr)
        return False

    # 2. Parse and Validate Catalog YAML
    try:
        catalog_content = catalog_path.read_text(encoding="utf-8")
        events = parse_events_yml(catalog_content)
    except Exception as e:
        print(f"Error parsing events_catalog.yml: {e}", file=sys.stderr)
        return False

    print(f"Found {len(events)} event definitions in catalog.")

    errors = []
    seen_names = set()

    for idx, ev in enumerate(events, 1):
        name = ev.get("event_name")
        if not name:
            errors.append(f"Event #{idx}: missing 'event_name'.")
            continue

        if name in seen_names:
            errors.append(f"Event '{name}': duplicate event_name found.")
        seen_names.add(name)

        category = ev.get("category")
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"Event '{name}': invalid category '{category}'. Must be one of {ALLOWED_CATEGORIES}")

        priority = ev.get("priority")
        if priority not in ALLOWED_PRIORITIES:
            errors.append(f"Event '{name}': invalid priority '{priority}'. Must be one of {ALLOWED_PRIORITIES}")

        schema_ver = ev.get("schema_version")
        if not isinstance(schema_ver, int) or schema_ver < 1:
            errors.append(f"Event '{name}': invalid schema_version '{schema_ver}'. Must be an integer >= 1.")

        payload = ev.get("payload", {})
        if not payload and priority in {"Critical", "High"}:
            errors.append(f"Event '{name}': Critical/High priority event must define payload fields.")
        for field, field_meta in payload.items():
            ftype = field_meta.get("type")
            if ftype not in ALLOWED_TYPES:
                errors.append(f"Event '{name}' field '{field}': invalid type '{ftype}'. Allowed: {ALLOWED_TYPES}")

    if errors:
        print("\n[FAIL] Event Catalog Validation FAILED with errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print("\n[SUCCESS] Event Catalog Validation PASSED successfully!")
    print(f"   Total Events Validated: {len(seen_names)}")
    return True

def main():
    repo_root = Path(__file__).resolve().parents[1]
    catalog_path = repo_root / "events_catalog.yml"
    envelope_path = repo_root / "schemas" / "event_envelope.schema.json"

    success = validate_catalog(catalog_path, envelope_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
