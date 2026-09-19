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

**PASS31.28** is the canonical 2009Scape drop-data and lazy-loading pass built from the governed PASS31.27 repository. It pins the supplied 2009Scape drop-table payload, calculates authoritative weighted probabilities, adds the missing tertiary relationships, and replaces the monolithic relationship payload with lazy gzip shards.

## Runtime baseline

PASS31.25 established static application-tools markup and bootstrap parity across the shell pages. The canonical navigation remains static HTML; runtime code enhances existing shell elements rather than creating competing navigation.

## Release confidence

Replacement ZIPs require a minimum **96% confidence gate** and fresh extraction/validation before delivery.



**PASS31.29** normalizes all exact drop-rate displays to the player-facing `1/X` format while preserving exact underlying probabilities and adds a shared runtime formatter across all drop-rate consumers.

## PASS31.28 drop-data baseline
The canonical drop source is pinned by SHA-256 `3f6b1f4d2f49f72d54d71545a8397bc0ca04c44bb4aaa6f58325a27dac59e856`. It produces 52,194 unique monster→item relationships, including 100 tertiary relationships. Drop probabilities are calculated from 2009Scape weights and loaded through lazy gzip-compressed shards.
