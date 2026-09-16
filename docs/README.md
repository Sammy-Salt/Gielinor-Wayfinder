# Documentation

Documentation is part of the implementation, not an afterthought. Future contributors and AI agents are expected to read the relevant documentation before changing code and update it when contracts change.

## Structure

- `architecture/` — application structure, runtime loading, PWA, service worker, and character data flow.
- `data/` — source precedence, identity, provenance, schemas, relationships, and save audits.
- `features/` — feature contracts and behavior.
- `development/` — engineering workflow, AI change protocol, Git, testing, and release process.
- `decisions/` — accepted and superseded architectural decisions (historical ADRs remain traceable).
- `releases/` — PASS-by-PASS release history.
- `history/` — consolidated external-review findings.

## Rule

Permanent project knowledge belongs in its appropriate document. Temporary analysis should be consolidated into permanent documentation or removed; it must not become a competing source of truth.

Start with `../AGENTS.md` and `development/AI_CHANGE_PROTOCOL.md` when working as an AI agent.
