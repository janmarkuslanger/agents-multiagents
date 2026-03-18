## Roles

| Role | File | When to activate |
|---|---|---|
| Software Architect | `agents/architect.md` | New feature, new component, or any change that touches boundaries |
| Platform Engineer | `platform-engineer.md` | After Architect — self-skips if no infrastructure impact |
| Coder | `agents/coder.md` | After Platform Engineer — receives both Architect and Platform Engineer output |
| Reviewer | `agents/reviewer.md` | After Coder |

## Pipeline

```text
1. ARCHITECT          →  design document (JSON) → wait for confirmation
2. PLATFORM ENGINEER  →  infra plan (JSON), or { "skipped": true, "reason": "..." }
3. CODER              →  implementation (JSON)
4. REVIEWER           →  verdict (JSON)
```

## Handoff

- Platform Engineer receives: Architect's confirmed design document (inline JSON)
- Coder receives: Architect's confirmed design document + Platform Engineer output (both inline JSON)
- Reviewer receives: Architect's confirmed design document + Platform Engineer output + Coder's implementation (all inline JSON)

All handoffs are inline JSON. No files are written to disk.
A role MUST NOT start before it has received all required upstream outputs.
