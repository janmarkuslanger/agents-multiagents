#!/usr/bin/env python3
"""Validate a role output JSON against its schema.

Usage:
    python validate_handoff.py <role> <output.json>
    python validate_handoff.py <role> -      # reads from stdin

Roles: architect, coder, reviewer, tester
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("missing dependency: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"
KNOWN_ROLES = {"architect", "coder", "reviewer", "tester"}


def validate(role: str, raw: str) -> None:
    if role not in KNOWN_ROLES:
        raise ValueError(f"unknown role '{role}'. valid: {', '.join(sorted(KNOWN_ROLES))}")
    schema_file = SCHEMAS_DIR / f"{role}-output.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"schema not found: {schema_file}")
    schema = json.loads(schema_file.read_text())
    instance = json.loads(raw)
    jsonschema.validate(instance, schema)
    print(f"✓ {role} output is valid")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    role_name = sys.argv[1]
    path_arg = sys.argv[2]
    raw_data = sys.stdin.read() if path_arg == "-" else Path(path_arg).read_text()
    try:
        validate(role_name, raw_data)
    except json.JSONDecodeError as e:
        print(f"✗ invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except jsonschema.ValidationError as e:
        print(f"✗ schema violation: {e.message}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, FileNotFoundError) as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)
