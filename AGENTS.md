# AI / Agent Operating Contract — Gielinor Wayfinder

**STOP. READ THIS FILE BEFORE CHANGING ANY PROJECT FILE.**

This repository is deliberately governed by Git, architecture documentation, data-source rules, and PASS release records. Any AI agent, coding assistant, or automated contributor working here MUST treat those artifacts as the project's source of truth

## Mandatory first actions

Before editing anything:

1. Read this file completely.
2. Read `docs/development/AI_CHANGE_PROTOCOL.md`.
3. Run `git status --short`.
4. Run `git log --oneline -5` and inspect the current `HEAD`.
5. Read `docs/architecture/ARCHITECTURE.md`, `docs/architecture/RUNTIME.md`, and the relevant feature/data documentation for the requested change.
6. Check the current PASS/release record in `docs/releases/` and the relevant ADRs in `docs/decisions/`.
7. Do not assume an older conversation, prompt, ZIP, or generated report is authoritative when the repository disagrees.

## Mandatory change actions

For **every change**, every time:

- Keep code modular, standardized, human-readable, and consistent with surrounding code.
- Make the smallest coherent change that satisfies the task.
- Preserve the offline-first architecture unless the user explicitly changes that requirement.
- Preserve source precedence: **2009Scape first, OSRS Wiki second, unknown when unresolved**.
- Never reintroduce Ragger or other retired/untrusted production data.
- Update every affected permanent document, feature contract, data contract, ADR, test, and PASS/release record.
- If a decision changes architecture, create or update an ADR rather than hiding the decision in code comments.
- Run the relevant targeted tests and the complete applicable regression suite.
- Inspect `git diff`, `git diff --check`, and the changed-file list.
- Commit the validated change to Git with a descriptive PASS-oriented commit message.
- Do not leave the repository with unexplained uncommitted changes unless the user explicitly asks for a work-in-progress state.

## Mandatory completion evidence

An agent must be able to state:

- what changed;
- which documentation changed and why;
- which tests were run and their results;
- what Git commit records the change;
- whether release metadata changed;
- whether a fresh release archive was validated when a release artifact was produced.

If any required evidence is missing, the work is **not complete**.

## Important Git rule

`.git` is the authoritative history/checkpoint system. Do not delete, replace, reset, or reinitialize it merely to make a task easier. If history appears wrong, inspect it and explain the discrepancy before changing repository history.

Use normal Git commands to inspect `.git`; do not edit Git's internal object database manually.
