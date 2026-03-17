# Workflow (with Platform Engineer)

This file is an example of a workflow override. To activate it, copy it to
`agents/extensions/workflow.md` in your project repository:

```bash
cp agents/extensions/workflow-platform-engineer.example.md agents/extensions/workflow.md
```

**This file is not active on its own.** Only `agents/extensions/workflow.md`
is loaded by `AGENTS.md`.

---

## Roles

| Role | File | When to activate |
|---|---|---|
| Software Architect | `agents/architect.md` | New feature, new component, or any change that touches boundaries |
| Coder | `agents/coder.md` | Implementation after a confirmed design document exists |
| Platform Engineer | `agents/extensions/platform-engineer.md` | After Coder — always activated, self-skips if no infra impact |
| Reviewer | `agents/reviewer.md` | After Platform Engineer |

## Pipeline

```
1. ARCHITECT          →  design document (JSON) → wait for confirmation
2. CODER              →  implementation (JSON)
3. PLATFORM ENGINEER  →  infra + deployment + observability (JSON), or { "skipped": true }
4. REVIEWER           →  verdict (JSON)
```

Roles run sequentially. Each role MUST NOT start before it has received the
inline JSON output of the previous role.

## Handoff

- Coder receives: Architect's confirmed design document
- Platform Engineer receives: Architect's design document + Coder's implementation
- Reviewer receives: Architect's design document + Coder's implementation +
  Platform Engineer's output (full output or `{ "skipped": true, "reason": "..." }`)

No files are written to disk. All handoffs are inline JSON.

**This workflow is mandatory.** Do not deviate without explicit user approval.

## When to skip the Architect

The Architect step MUST NOT be skipped autonomously. If you believe a change
is small enough to skip it, ask the user first:

> "This change seems small enough to skip the Architect step. Should I proceed
> directly with the Coder, or do you want the full Architect → Coder →
> Platform Engineer → Reviewer flow?"

Do not proceed until you have an explicit answer.

## When the Platform Engineer skips itself

The Platform Engineer always runs. It decides itself whether infra work is
needed. If it outputs `{ "skipped": true, "reason": "..." }`, pass that
marker directly to the Reviewer — do not omit it.

## Iteration

If the Reviewer returns `CHANGES_REQUESTED`, the Coder addresses the critical
issues. If the Reviewer flags infra issues, the Platform Engineer also re-runs.
Then the Reviewer re-reviews.
