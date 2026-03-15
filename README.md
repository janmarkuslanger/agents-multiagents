# agents-multiagent

Multiagent configuration for Claude Code and API-based workflows.
Implements an Architect → Coder → Reviewer pipeline with structured JSON outputs.

## Structure

```
agents-multiagent/
  AGENTS.md              # Orchestration rules — link this to your project root
  architect.md           # Architect role & output schema
  coder.md               # Coder role & output schema
  reviewer.md            # Reviewer role & output schema
  validate.py            # Validates JSON outputs against schemas
  schemas/
    architect-output.json
    coder-output.json
    reviewer-output.json
```

---

## Setup

### Add as Git submodule

```bash
git submodule add git@github.com:janmarkuslanger/agents-multiagent.git agents
```

Claude Code will automatically pick up `agents/AGENTS.md`.

On a fresh clone of a project that uses this submodule:

```bash
git clone --recurse-submodules git@github.com:USERNAME/my-project.git
```

Or if you already cloned without submodules:

```bash
git submodule update --init --recursive
```

Update to the latest version:

```bash
git submodule update --remote agents
git add agents && git commit -m "chore: update agents"
```

---

## Workflow

```
1. ARCHITECT  →  reads requirements, produces JSON design document
2. CODER      →  reads design document, produces JSON with files + tests
3. REVIEWER   →  reads design + implementation, produces JSON verdict
```

Roles run sequentially. The Coder does not start without a design document.
If the Reviewer returns `CHANGES_REQUESTED`, the Coder fixes critical issues
and the Reviewer re-reviews.

The Architect step may be skipped for changes scoped to a single function or
file that do not touch module boundaries.

---

## Usage with Claude Code

```bash
git submodule add git@github.com:janmarkuslanger/agents-multiagent.git agents
```

Then just use Claude Code normally — it reads `agents/AGENTS.md` automatically
and applies the Architect → Coder → Reviewer flow.

---

## Usage with the API

```python
from pathlib import Path
from agents.validate import parse_agent_response, validate_output

def call_claude(system: str, user: str) -> str:
    # your Anthropic API call here
    ...

architect_prompt = Path("agents/architect.md").read_text()
coder_prompt     = Path("agents/coder.md").read_text()
reviewer_prompt  = Path("agents/reviewer.md").read_text()

requirements = "Your feature description here."

# Step 1: Architect
arch_raw     = call_claude(system=architect_prompt, user=requirements)
arch_output  = parse_agent_response(arch_raw)
errors       = validate_output("architect", arch_output)
if errors:
    raise ValueError(f"Architect output invalid: {errors}")

# Step 2: Coder
coder_raw    = call_claude(
    system=coder_prompt,
    user=f"Design document:\n{arch_raw}\n\nImplement this."
)
coder_output = parse_agent_response(coder_raw)
errors       = validate_output("coder", coder_output)
if errors:
    raise ValueError(f"Coder output invalid: {errors}")

# Step 3: Reviewer
reviewer_raw    = call_claude(
    system=reviewer_prompt,
    user=f"Design:\n{arch_raw}\n\nImplementation:\n{coder_raw}\n\nReview this."
)
reviewer_output = parse_agent_response(reviewer_raw)
errors          = validate_output("reviewer", reviewer_output)
if errors:
    raise ValueError(f"Reviewer output invalid: {errors}")

if reviewer_output["verdict"] == "CHANGES_REQUESTED":
    print("Changes required:", reviewer_output["critical_issues"])
else:
    print("Approved:", reviewer_output["verdict"])
```

---

## Validating outputs manually

```bash
pip install jsonschema

python agents/validate.py architect output.json
python agents/validate.py coder output.json
python agents/validate.py reviewer output.json
```

---

## Extensions

For project-specific rules, create a `.md` file and append it to the relevant
role prompt:

```python
base  = Path("agents/architect.md").read_text()
extra = Path("my-extension.md").read_text()
system = base + "\n\n---\n\n" + extra
```

Keep extensions in your project repo — not here. Only rules that apply to
every project belong in this repo.
