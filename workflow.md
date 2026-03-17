# Workflow

This file defines the default agent pipeline. It is always loaded first.

If `agents/extensions/workflow.md` exists, it is loaded on top: sections
defined there override the matching sections here. Sections not present in
the extension remain active from this file.

**Overridable sections:** `## Roles`, `## Pipeline`, `## Handoff`,
`## When to skip the Architect`, `## Iteration`

---

## Roles

Three specialized roles handle every non-trivial task.

| Role | File | When to activate |
|---|---|---|
| Software Architect | `agents/architect.md` | New feature, new component, or any change that touches boundaries |
| Coder | `agents/coder.md` | Implementation after a confirmed design document exists |
| Reviewer | `agents/reviewer.md` | After implementation, before merge |

## Pipeline

```text
1. ARCHITECT  →  produce design document → present plan → wait for confirmation
2. CODER      →  implement against confirmed design document
3. REVIEWER   →  review implementation against design document + requirements
```

Roles run sequentially. The Coder MUST NOT start before it has received the
Architect's confirmed design document as inline JSON. The Reviewer receives
both the confirmed design document and the Coder's implementation, both passed
inline as JSON.

## Handoff

Each role passes its JSON output inline to the next role. No files are written
to disk. A role MUST NOT start before it has received the inline JSON output of
the previous role.

**This workflow is mandatory.** If you believe a different approach or a
single-agent solution would be better, do not switch autonomously — ask the
user first and explain your reasoning. Only deviate after explicit approval.

## When to skip the Architect

The Architect step MUST NOT be skipped autonomously. If you believe a change
is small enough to skip the Architect (e.g. scoped to a single function or
file, no module boundaries touched), ask the user first:

> "This change seems small enough to skip the Architect step. Should I proceed
> directly with the Coder, or do you want the full Architect → Coder → Reviewer
> flow?"

Do not proceed until you have an explicit answer.

## Iteration

If the Reviewer returns `CHANGES_REQUESTED`, the Coder addresses the
critical issues and the Reviewer re-reviews. Suggestions are optional.
