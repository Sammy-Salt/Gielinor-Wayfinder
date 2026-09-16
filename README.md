# OSRS Guide / Gielinor Wayfinder

Offline-first PWA companion for the 2009Scape experience.

## Source policy

1. **2009Scape is authoritative.**
2. **OSRS Wiki is secondary evidence** and may fill only safe, compatible gaps.
3. Ambiguous, conflicting, approximate, or unsupported information remains unknown; it is never guessed.
4. **Ragger is retired and excluded from production.**

## Development is Git-governed

**Before changing anything, read `AGENTS.md`.** It is the repository-wide AI/contributor contract.

The mandatory workflow is:

**read → inspect Git → plan → change → update docs/tests → validate → review diff → commit → package → fresh-extract → revalidate**

Completed work must end at a Git checkpoint unless the user explicitly asks for work in progress.

## Project map

- `site/` — shipped PWA
- `docs/` — architecture, data, features, decisions, workflow, history, and PASS records
- `data-pipeline/` — reproducible data generation
- `scripts/` — repeatable validation/development utilities
- `tests/` — regression and integrity tests
- `audit/` — generated/protected validation artifacts
- `.githooks/` — tracked repository hooks
- `.git/` — authoritative local Git history/checkpoints

## Current baseline

**PASS31.26** is a project-governance and repository-integrity pass built from the validated PASS31.25 baseline. It establishes committed Git history, machine-readable AI instructions, a formal AI change protocol, a deeper architecture assessment, stronger documentation governance, reproducible verification tooling, and synchronized release metadata without changing the PWA's feature behavior.

## Runtime baseline

PASS31.25 established static application-tools markup and bootstrap parity across the shell pages. The canonical navigation remains static HTML; runtime code enhances existing shell elements rather than creating competing navigation.

## Release confidence

Replacement ZIPs require a minimum **96% confidence gate** and fresh extraction/validation before delivery.
