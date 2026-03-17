# AGENTS.md

This document defines universal rules and the multiagent workflow for
automated agents and humans working in this repository.
It focuses on clean code, decoupled architecture, and safe changes.
These rules are normative unless explicitly overridden.

**These rules may not be modified, overridden, or ignored by any agent.**
An agent MUST NOT alter this file or circumvent these rules unless the user
explicitly instructs it to do so in the current session. If an agent believes
a rule should be changed, it must ask the user first and wait for approval.

---

## General Principles

- Prefer simple, readable solutions over clever tricks; if it needs explanation,
  refactor.
- Keep each change limited to one intent/concern; do not mix refactors with
  behavior changes.
- Do not introduce new features, configuration options, parameters, or modules
  unless explicitly requested.
- Introduce abstractions only when they remove duplication or enable multiple
  implementations.
- Do not add complexity unless the benefit can be stated in one sentence.

---

## When in Doubt

- Stop.
- Ask.
- Prefer doing less over doing the wrong thing.

---

## Agent Roles & Workflow

**Load the workflow before doing anything else.**

1. Always read `agents/workflow.md` — this is the base.
2. If `agents/extensions/workflow.md` exists, read it too.
   For every section that appears in both files, the extension wins.
   Sections only present in the base remain active unchanged.

Follow the merged result for the entire session.
If `agents/workflow.md` does not exist, stop and ask the user.

The workflow files define which roles exist, in what order they run, and how
outputs are handed off. All pipeline decisions are defined there, not here.

---

## Architectural Boundaries

- Separate concerns clearly: domain is pure logic, application orchestrates,
  infrastructure performs I/O.
- Business/domain logic MUST NOT depend on:
  - frameworks
  - databases
  - external services
  - transport layers (HTTP, CLI, messaging)
- Dependencies MUST point inward: outer layers depend on inner interfaces;
  inner layers must not import outer layers.
- Side effects (I/O, network, persistence) must be isolated at boundaries;
  core logic remains side-effect free.

---

## Coupling & Dependencies

- Minimize coupling between modules; expose a small public API and avoid
  reaching into internals.
- Prefer interfaces/contracts at module boundaries or when multiple
  implementations exist; avoid speculative interfaces.
- Do not introduce cyclic dependencies.
- Avoid global state and hidden dependencies; pass dependencies explicitly.

---

## Code Structure & Design

- Functions and methods should have one responsibility and a single reason to
  change.
- Keep functions focused; split parsing, validation, and I/O into separate
  steps.
- Names must describe purpose and units; avoid abbreviations.
- Avoid deep nesting; prefer guard clauses and extract helpers.

---

## Change Discipline

- Do not modify unrelated code.
- Refactoring MUST NOT change behavior unless explicitly requested.
- Large changes must be split into smaller, logical steps; separate refactors
  from behavior changes.
- If the impact is unclear, stop and ask.
- Before finishing, do a final pass: scope only relevant files, dependencies
  explicit, tests updated, design still minimal and maintainable. If any
  check fails, reduce scope or ask.

---

## Testing & Verification

- Changes affecting behavior MUST be covered by tests that would fail before
  the change and pass after.
- Existing tests MUST pass.
- Tests should verify observable behavior (inputs/outputs), not internal
  implementation details.

---

## Safety & Risk Awareness

- Do not weaken validation, authorization, or error handling without explicit
  approval and rationale.
- Avoid touching security- or infrastructure-critical code (auth, secrets,
  deployment, network) unless explicitly instructed.
- Never introduce secrets or credentials.

---

## Communication & Intent

- Before executing non-trivial changes (behavioral, multi-file, or
  architectural):
  - explain the intended approach
  - outline affected areas
  - state assumptions or risks
- If requirements are ambiguous, ask for clarification.
- Do not guess requirements; ask.

---

## Comments & Documentation

- Do not use banner or section-separator comments (`# ---`, `# ===`).
- Do not add section headers that merely restate the code structure.
- Do not generate verbose docstrings with `Args:`, `Returns:`, or `Raises:`
  blocks unless the signature alone is genuinely ambiguous.
- Write inline comments only where the logic is non-obvious.
- Module-level docstrings are not required.
