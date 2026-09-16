# Claude Repository Instructions

Before making any change, read `AGENTS.md` and `docs/development/AI_CHANGE_PROTOCOL.md`, then inspect Git with `git status --short` and `git log --oneline -5`.

The repository's architecture and documentation are authoritative. Follow the 2009Scape → OSRS Wiki → unknown source policy, keep the PWA offline-first, never reintroduce Ragger, update affected documentation/tests/ADRs/PASS records, validate the result, inspect the diff, and commit every completed change.

Do not leave undocumented or uncommitted completed work unless the user explicitly requests a work-in-progress state.
