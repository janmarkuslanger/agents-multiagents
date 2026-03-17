# agents-multiagent

Multiagent configuration for Claude Code and API-based workflows.
Implements an Architect → Coder → Reviewer pipeline with structured JSON outputs.

## Structure

```
agents-multiagent/
  AGENTS.md              # Orchestration rules — linked to your project root via submodule
  architect.md           # Architect role definition
  coder.md               # Coder role definition
  reviewer.md            # Reviewer role definition
  schemas/
    architect-output.json
    coder-output.json
    reviewer-output.json
  extensions/
    role-template.md           # Template for creating new workflow roles
    platform-engineer.md       # Example: Platform Engineer role
    platform-engineer-output.json
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

The base workflow runs three roles sequentially:

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

## Extending the Workflow with Custom Roles

You can insert additional roles into the pipeline without modifying any core
file in this submodule. The mechanism relies on two things:

1. **A role file** — a markdown file describing what the role does and what
   it outputs
2. **A project-level `AGENTS.md`** at your project root — Claude Code reads
   this alongside `agents/AGENTS.md` and uses it to override or extend the
   workflow

Core files (`agents/AGENTS.md`, `agents/architect.md`, etc.) stay untouched.

---

### Two types of extensions

| Type | What it does | Example |
|---|---|---|
| **Role extension** | Appends extra rules to an existing role | Add TypeScript-specific rules to the Coder |
| **Workflow extension** | Adds a new role to the pipeline | Insert a Platform Engineer between Coder and Reviewer |

This section covers **workflow extensions** (new roles). For role extensions
(appending rules), see the [Role Extensions](#role-extensions-appending-rules-to-existing-roles)
section below.

---

### Adding a new workflow role: step by step

#### 1. Create the role file

Copy `agents/extensions/role-template.md` to your project and fill it in:

```bash
cp agents/extensions/role-template.md platform-engineer.md
```

The role file defines:
- What the role is responsible for
- What inputs it expects (which upstream role outputs it reads)
- When it can skip itself (output `{ "skipped": true, "reason": "..." }`)
- What JSON it outputs

#### 2. Create the output schema

Create a JSON Schema file that describes the role's output. This is what the
next role in the chain validates against.

Refer to `agents/extensions/platform-engineer-output.json` as a concrete
example. Schemas for skippable roles use a `oneOf` with a skip variant and a
full-output variant.

#### 3. Register the role in your project's AGENTS.md

Create (or extend) a root-level `AGENTS.md` in your project. Claude Code reads
this file alongside the submodule's `agents/AGENTS.md`.

Declare:
- Where in the pipeline the new role sits
- What inputs it receives
- How its output is handed to the next role

```markdown
# AGENTS.md  ←  this is your project's root-level file, not the submodule's

## Extended workflow

This project extends the base Architect → Coder → Reviewer workflow with a
Platform Engineer role after the Coder.

| Role | File | When to activate |
|---|---|---|
| Software Architect | `agents/architect.md` | New feature or boundary change |
| Coder | `agents/coder.md` | After confirmed design document |
| Platform Engineer | `platform-engineer.md` | After Coder, always — self-skips if no infra impact |
| Reviewer | `agents/reviewer.md` | After Platform Engineer |

### Handoff

After the Coder produces its JSON, pass it inline to the Platform Engineer.
The Platform Engineer reads both the Architect's design document and the
Coder's implementation.

If the Platform Engineer outputs `{ "skipped": true }`, pass that directly
to the Reviewer as-is.

The Reviewer receives:
- The Architect's confirmed design document (inline JSON)
- The Coder's implementation (inline JSON)
- The Platform Engineer's output or skip marker (inline JSON)
```

#### 4. (API usage only) Append the role prompt programmatically

When calling the Claude API directly, concatenate the role file at runtime:

```python
base     = Path("agents/coder.md").read_text()
# no change needed — platform-engineer.md is its own system prompt

platform = Path("platform-engineer.md").read_text()
schema   = Path("platform-engineer-output.json").read_text()

# Pass platform + schema as the system prompt for the Platform Engineer turn
system = platform + "\n\n---\n\nOutput schema:\n```json\n" + schema + "\n```"
```

---

### Worked example: Platform Engineer

The `agents/extensions/` folder contains a complete, ready-to-use Platform
Engineer role.

**Files:**
- `agents/extensions/platform-engineer.md` — role definition
- `agents/extensions/platform-engineer-output.json` — output schema

**What it does:**

The Platform Engineer runs after the Coder. It translates the implementation
into everything needed to run it in production: infrastructure-as-code,
deployment config, observability (metrics, alerts), and a rollout plan with
rollback steps.

It self-skips (`{ "skipped": true }`) when the change has no infrastructure
impact, so it is always activated and never pre-judged.

**To use it in your project:**

```bash
# Copy the role file into your project
cp agents/extensions/platform-engineer.md .
cp agents/extensions/platform-engineer-output.json .
```

Then add the extended workflow declaration to your root `AGENTS.md` as shown
in step 3 above.

**Adjusted workflow with Platform Engineer:**

```
1. ARCHITECT          →  design document (JSON)
2. CODER              →  implementation (JSON)
3. PLATFORM ENGINEER  →  infra + deployment + observability (JSON), or { "skipped": true }
4. REVIEWER           →  verdict (JSON), using all three upstream outputs
```

---

### Design rules for custom roles

Keep your role files consistent with the base roles:

- **One responsibility**: the role has one clear concern and does not bleed
  into adjacent roles
- **Self-skipping**: if the role does not apply, it outputs
  `{ "skipped": true, "reason": "..." }` rather than producing empty output
- **No disk writes**: all output is inline JSON, passed to the next role
- **Minimal input**: the role declares exactly which upstream outputs it needs
- **Schema-first**: define the output schema before writing the role instructions

---

## Role Extensions: appending rules to existing roles

A role extension appends extra instructions to an existing base role without
replacing it. Use this for project- or domain-specific rules (framework
conventions, naming rules, stack constraints).

**Via API:**

```python
base  = Path("agents/architect.md").read_text()
extra = Path("my-architect-extension.md").read_text()
system = base + "\n\n---\n\n" + extra
```

**Reference in your project's `AGENTS.md`:**

```markdown
## Role extensions

- Architect: see `agents-extensions/architect-typescript.md`
- Coder: see `agents-extensions/coder-django.md`
```

Only include rules that are genuinely specific to your project. Rules that
apply to all projects belong in the base role files — open a PR instead.
