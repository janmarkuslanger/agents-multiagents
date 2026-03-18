# Template: Architect → Platform Engineer → Coder → Reviewer

This template extends the default `agents-multiagent` pipeline by inserting a
**Platform Engineer** between the Architect and the Coder.

Use this when your project deploys to real infrastructure and you need infra
concerns (databases, queues, secrets, IaC, CI/CD) evaluated before any code
is written.

---

## Pipeline

```
1. ARCHITECT          →  design document (confirmed by user)
2. PLATFORM ENGINEER  →  infra plan, or skips if no infra impact
3. CODER              →  implementation (aware of infra plan)
4. REVIEWER           →  verdict
```

---

## Setup

### 1. Add the submodule

```bash
git submodule add git@github.com:janmarkuslanger/agents-multiagent.git agents
```

### 2. Copy this template into your project root

```
your-project/
  agents/                               ← submodule (do not edit)
  agents-extensions/
    workflow.md                         ← pipeline overlay (from this template)
  platform-engineer.md                  ← role definition (from this template)
  schemas/
    platform-engineer-output.json       ← output schema (from this template)
```

Copy the files:

```bash
cp -r templates/with-platform-engineer/agents-extensions your-project/
cp templates/with-platform-engineer/platform-engineer.md your-project/
cp -r templates/with-platform-engineer/schemas your-project/
```

### 3. Clone with submodules (fresh clones)

```bash
git clone --recurse-submodules git@github.com:YOUR_ORG/your-project.git
# or after cloning without submodules:
git submodule update --init --recursive
```

### 4. Update the submodule

```bash
git submodule update --remote agents
git add agents && git commit -m "chore: update agents"
```

---

## How the Platform Engineer works

The Platform Engineer receives the Architect's confirmed design document and
evaluates its infrastructure impact before the Coder starts.

**It self-skips** when the design has no infrastructure consequences (e.g. a
pure in-process logic change with no new I/O boundaries). In that case it
emits `{ "skipped": true, "reason": "..." }` and the Coder proceeds immediately.

**When it runs**, it produces a structured infra plan covering:

| Field | Content |
|---|---|
| `environment_requirements` | Resources that must exist before the app runs (DB, queues, IAM roles, …) |
| `iac_changes` | Terraform / Helm / Kubernetes files to create or modify |
| `cicd_changes` | Pipeline steps to add or change |
| `secrets` | Environment variables and secrets required by new components |
| `risks` | Deployment risks with severity and rollback strategy |

The Coder receives both the Architect's design document and the Platform
Engineer's infra plan, so implementation decisions can account for the
actual environment.

---

## Customising

The `agents-extensions/workflow.md` overlay only defines what changes from the
base pipeline (`## Roles`, `## Pipeline`, `## Handoff`). Everything else
(Architect skip question, iteration rule, mandatory workflow note) is inherited
from `agents/workflow.md` automatically — do not repeat it here.

To add project-specific rules to the Platform Engineer role, append them
directly to `platform-engineer.md` (e.g. "Always use Terraform for IaC",
"Target environment is AWS ECS").
