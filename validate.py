"""
Validates agent JSON outputs against their schemas.

Usage:
    python agents/validate.py architect output.json
    python agents/validate.py coder output.json
    python agents/validate.py reviewer output.json

Or programmatically:
    from agents.validate import validate_output
    errors = validate_output("architect", data)
    if errors:
        raise ValueError(errors)
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    raise ImportError("pip install jsonschema")

SCHEMAS_DIR = Path(__file__).parent / "schemas"

ROLE_SCHEMAS = {
    "architect": SCHEMAS_DIR / "architect-output.json",
    "coder": SCHEMAS_DIR / "coder-output.json",
    "reviewer": SCHEMAS_DIR / "reviewer-output.json",
}


def validate_output(role: str, data: dict) -> list[str]:
    """
    Validates data against the schema for the given role.
    Returns a list of error messages, empty if valid.
    """
    if role not in ROLE_SCHEMAS:
        return [f"Unknown role '{role}'. Valid roles: {list(ROLE_SCHEMAS)}"]

    schema_path = ROLE_SCHEMAS[role]
    schema = json.loads(schema_path.read_text())

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    return [f"{'.'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in errors]


def parse_agent_response(raw: str) -> dict:
    """
    Parses a raw agent response into a dict.
    Strips markdown fences if the agent included them despite instructions.
    """
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return json.loads(text)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate.py <role> <output.json>")
        sys.exit(1)

    role = sys.argv[1]
    output_path = Path(sys.argv[2])

    data = json.loads(output_path.read_text())
    errors = validate_output(role, data)

    if errors:
        print(f"Validation failed for role '{role}':")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"✓ Valid {role} output.")
