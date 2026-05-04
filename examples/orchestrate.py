#!/usr/bin/env python3
"""Run the full Architect → Coder → Reviewer pipeline via the Anthropic API.

The script re-runs the Coder if the Reviewer returns CHANGES_REQUESTED,
up to MAX_ITERATIONS times.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python orchestrate.py "Build a user authentication module in Python"
    echo "requirements text" | python orchestrate.py

Output: JSON with keys architect, coder, reviewer, iterations.

To also write implementation files to disk, pipe coder output through
apply_output.py (see scripts/):
    python orchestrate.py "..." | python -c "
    import json, sys, subprocess
    result = json.load(sys.stdin)
    subprocess.run(
        ['python', 'scripts/apply_output.py', '-'],
        input=json.dumps(result['coder']),
        text=True,
    )
    "
"""
import json
import sys
from pathlib import Path
import anthropic

BASE = Path(__file__).parent.parent
MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 3


def _load_role(name: str) -> str:
    return (BASE / f"{name}.md").read_text()


def _call(client: anthropic.Anthropic, system: str, user: str) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return json.loads(msg.content[0].text)


def run(requirements: str) -> dict:
    client = anthropic.Anthropic()

    print("[architect] designing...", file=sys.stderr)
    design = _call(
        client,
        _load_role("architect"),
        (
            "Automated session. Skip quality/constraint questions and the"
            " skip-architect question. Produce the design document JSON directly.\n\n"
            f"Requirements:\n{requirements}"
        ),
    )

    coder_out = None
    reviewer_out = None
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"[coder] iteration {iteration}...", file=sys.stderr)
        coder_prompt = f"Confirmed design document:\n{json.dumps(design)}"
        if reviewer_out:
            coder_prompt += f"\n\nReviewer feedback to address:\n{json.dumps(reviewer_out)}"
        coder_out = _call(client, _load_role("coder"), coder_prompt)

        print(f"[reviewer] reviewing iteration {iteration}...", file=sys.stderr)
        reviewer_out = _call(
            client,
            _load_role("reviewer"),
            f"Design document:\n{json.dumps(design)}\n\nImplementation:\n{json.dumps(coder_out)}",
        )

        if reviewer_out.get("verdict") != "CHANGES_REQUESTED":
            break

    return {
        "architect": design,
        "coder": coder_out,
        "reviewer": reviewer_out,
        "iterations": iteration,
    }


if __name__ == "__main__":
    reqs = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    if not reqs:
        print("error: no requirements provided", file=sys.stderr)
        sys.exit(1)
    result = run(reqs)
    print(json.dumps(result, indent=2))
