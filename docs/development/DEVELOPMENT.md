# Development Workflow

Gielinor Wayfinder is maintained as a modular, documented, offline-first software project.

## Repository boundaries

- `site/` — deployable PWA.
- `site/js/core/` — runtime/core infrastructure.
- `site/js/services/` — reusable domain services.
- `site/js/components/` — reusable UI/runtime components.
- `site/js/pages/` — page-specific behavior.
- `data-pipeline/` — reproducible data generation.
- `tests/` — regression and integrity tests.
- `scripts/` — repeatable development/release validation helpers.
- `docs/` — permanent project knowledge.
- `audit/` — generated/protected validation artifacts.

## Engineering standards

Code should be modular, standardized, readable by humans, and formatted consistently with neighboring modules. Prefer existing services/contracts over parallel implementations.

Changes must preserve offline behavior, source provenance, and canonical ownership boundaries.

## Change lifecycle

Read → plan → implement → document → test → diff-review → commit → package → fresh-extract → revalidate.

See `AGENTS.md` and `docs/development/AI_CHANGE_PROTOCOL.md` for mandatory AI-agent behavior.
