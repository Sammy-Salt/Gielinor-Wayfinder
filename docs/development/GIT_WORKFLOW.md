# Git Workflow

Git is the project's authoritative checkpoint system. The repository contains a committed baseline and must remain understandable from Git history without relying on chat history.

## Before every change

```text
git status --short
git log --oneline -5
git show --stat --oneline HEAD
```

Read `AGENTS.md` and `docs/development/AI_CHANGE_PROTOCOL.md`, then inspect relevant architecture/data/feature docs and ADRs.

## During a PASS

1. Start from a known-good checkpoint.
2. Record the intended scope.
3. Make one coherent change.
4. Update all affected docs/tests/ADRs/release records.
5. Run targeted tests.
6. Run the full applicable regression suite.
7. Run `git diff --check`.
8. Review `git diff` and `git status --short` for unrelated/generated files.
9. Validate release metadata and fresh extraction when producing a release.
10. Commit the validated state.

## Commit format

Use:

```text
PASS31.xx: concise description of the change
```

The commit body should explain the reason and validation when the change is architectural or release-level.

## Clean-tree rule

Completed work should end with a clean working tree. A dirty tree is allowed only when the user explicitly requests a work-in-progress state.

## History safety

Never delete or reinitialize `.git` to solve a development problem. Preserve existing commits and investigate discrepancies first.
