# Contributing

Gielinor Wayfinder is maintained as a documented, Git-checkpointed offline-first PWA project.

## Before editing

Read:

1. `AGENTS.md`
2. `docs/development/AI_CHANGE_PROTOCOL.md`
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/development/GIT_WORKFLOW.md`
5. the relevant feature/data documentation and ADRs

Then inspect the Git working tree and recent history.

## During editing

- Keep modules small and readable.
- Reuse established services and contracts instead of adding parallel data paths.
- Keep HTML shell structure consistent across pages.
- Keep source provenance explicit.
- Treat unknown as unknown; do not invent missing game data.
- Update tests with behavior changes.
- Update permanent documentation whenever behavior, contracts, architecture, source policy, or workflow changes.

## Before completion

Run the applicable validation, inspect the full diff, verify release metadata, and commit the validated state. Release archives are built only from a validated Git checkpoint and are fresh-extracted and revalidated before delivery.
