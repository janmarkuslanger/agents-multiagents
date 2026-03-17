# agents-multiagent

Multiagent configuration for Claude Code and API-based workflows.
Implements an Architect → Coder → Reviewer pipeline with structured JSON outputs.

## Structure

```
agents-multiagent/
  AGENTS.md                       # Orchestration rules — link this to your project root
  architect.md                    # Architect role & output schema
  coder.md                        # Coder role & output schema
  platform-engineer.md            # Platform Engineer role & output schema (optional step)
  reviewer.md                     # Reviewer role & output schema
  schemas/
    architect-output.json
    coder-output.json
    platform-engineer-output.json
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
1. ARCHITECT          →  reads requirements, produces JSON design document
2. CODER              →  reads design document, produces JSON with files + tests
3. PLATFORM ENGINEER  →  reads design + implementation, produces JSON with infra/deployment/observability
                          (outputs { "skipped": true } if no infra impact)
4. REVIEWER           →  reads design + implementation + platform output, produces JSON verdict
```

Roles run sequentially. The Coder does not start without a design document.
The Platform Engineer always runs after the Coder and decides itself whether
infra work is needed. If the Reviewer returns `CHANGES_REQUESTED`, the Coder
fixes critical issues and the Reviewer re-reviews.

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


## Extensions

An extension is a markdown file appended to a base role prompt for project- or
domain-specific rules. Keep extensions in your project repo — not here.

**Append via API:**

```python
base  = Path("agents/architect.md").read_text()
extra = Path("my-extension.md").read_text()
system = base + "\n\n---\n\n" + extra
```

**Reference in `AGENTS.md`:**

```markdown
## Project-specific rules
See `agents/extensions/my-extension.md`.
```

**Creating an extension:** create a `.md` file named after the domain or
project. Only include rules that are genuinely specific to that context — rules
that apply to all projects belong in the base role files instead.
