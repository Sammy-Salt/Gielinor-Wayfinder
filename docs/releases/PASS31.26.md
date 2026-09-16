# PASS31.26 — Git and AI Governance Foundation

## Purpose

Establish a durable Git repository and repository-discoverable operating contract so future human and AI contributors can understand, preserve, validate, and checkpoint the project without relying on chat history.

## Scope

PASS31.26 is a development/governance pass. It does not intentionally change PWA feature behavior.

### Repository governance

- Added a real committed `.git` repository.
- Added root `AGENTS.md` as the mandatory AI/contributor entry point.
- Added `CLAUDE.md`, `.github/copilot-instructions.md`, and `CONTRIBUTING.md` as discoverable adapter instructions.
- Added `docs/development/AI_CHANGE_PROTOCOL.md` as the detailed change contract.
- Added tracked `.githooks/pre-commit` and `scripts/setup-git-hooks.sh`.
- Added `scripts/verify_project.py` as a repeatable repository integrity gate.

### Documentation

- Added `docs/development/PROJECT_ANALYSIS.md` with the current architecture, data paths, ownership boundaries, risk map, and invariants.
- Expanded Git, development, testing, release, architecture, and documentation-governance guidance.
- Corrected ADR-0005 status to describe the current canonical shell decision.

### Repository hygiene

- Removed generated Python cache/test cache artifacts from the source tree and added Git-tracked checks that keep such generated files out of releases.
- Expanded `.gitignore` for common generated/local files.
- Synchronized stale PASS31.24 release manifests to the PASS31.26 governance baseline.

## Validation

The PASS31.26 release gate requires:

- project integrity script;
- JavaScript syntax checks;
- JSON validation;
- static-shell invariants;
- zero Ragger production references;
- release/build metadata consistency;
- Git repository presence and clean checkpoint;
- applicable historical PASS regression tests;
- fresh source-archive extraction and revalidation.
