# AI Change Protocol

**Status: Mandatory project policy**

This document exists so that future AI agents can work on Gielinor Wayfinder without losing architectural decisions, source provenance, tests, Git history, or release discipline.

## 1. The repository is the source of truth

An AI must not treat a previous chat, generated ZIP, external review, or memory as more authoritative than the checked-out repository.

The authoritative layers are:

1. current source code and shipped data;
2. Git history and the current branch/HEAD;
3. current architecture/data/feature documentation;
4. accepted ADRs;
5. PASS release records;
6. consolidated external-review history.

Generated reports are evidence, not architecture.

## 2. Required startup sequence

Run this before editing:

```text
git status --short
git log --oneline -5
git show --stat --oneline HEAD
```

Then read:

```text
AGENTS.md
README.md
docs/architecture/ARCHITECTURE.md
docs/architecture/RUNTIME.md
docs/architecture/PWA.md
docs/data/DATA_ARCHITECTURE.md
docs/data/SOURCES.md
docs/data/PROVENANCE.md
docs/development/GIT_WORKFLOW.md
docs/development/TESTING.md
docs/development/RELEASE_PROCESS.md
```

Also read the relevant feature document and ADRs before touching that area.

## 3. Required planning questions

Before changing code, identify:

- What user-visible or internal contract is changing?
- Which module owns that behavior today?
- Is there already a service/data relationship that should be reused?
- Which source supplies the data, and what provenance must be preserved?
- Which pages, data files, tests, docs, manifests, and service-worker assets are affected?
- Does the change create a new architectural decision?
- Does the map-boundary protection apply?

Do not solve an ownership problem by creating a second implementation.

## 4. Required implementation rules

### Architecture

- `site/` is the shipped PWA.
- Shared runtime belongs in `site/js/core/` and shared services in `site/js/services/`.
- Page-specific behavior belongs in `site/js/pages/`.
- Shared UI components belong in `site/js/components/`.
- Data generation belongs in `data-pipeline/`.
- Validation belongs in `tests/` and reproducible helper scripts in `scripts/`.
- Permanent knowledge belongs in `docs/`.

### Data

The source policy is:

**2009Scape → OSRS Wiki → unknown**

A secondary source may fill a safe gap but must not silently override authoritative game data. Ambiguous, conflicting, approximate, or unsupported evidence stays unavailable/unknown.

Ragger is retired and must remain absent from production data, code, HTML, CSS, and manifests.

### Runtime shell

The static HTML shell owns the canonical navigation. There must be one `#site-nav` and one `#app-tools-host` on normal shell pages. Runtime JavaScript enhances existing elements; it does not create, replace, or remove the canonical navigation or application-tools shell.

### Offline/PWA

The application is offline-first. New functionality must not quietly introduce a network dependency into the shipped PWA.

## 5. Documentation matrix

Update the smallest complete set of permanent records:

| Change area | Required documentation |
|---|---|
| Architecture/runtime | `docs/architecture/*` + ADR when a decision changes |
| Data/source/schema | `docs/data/*` + affected feature doc + ADR if policy changes |
| UI feature | affected `docs/features/*.md` + architecture docs if shell/runtime changes |
| Test/validation | `docs/development/TESTING.md` |
| Git/process | `docs/development/*` |
| Release/PASS | `docs/releases/PASSxx.xx.md` |
| External review | `docs/history/EXTERNAL_REVIEWS.md` only after useful findings are consolidated |

Do not create random top-level notes when a permanent document already has an appropriate home.

## 6. Required validation

At minimum, run the relevant targeted tests. For a release-level change, run the full applicable suite, JavaScript syntax checks, JSON validation, source-policy checks, Ragger scan, map-boundary checks, manifest/build checks, and fresh-extraction validation.

When runtime behavior changes, Firefox/Android smoke testing remains part of the release confidence gate.

## 7. Required Git completion

After validation:

```text
git diff --check
git status --short
git diff --stat
git diff
```

Review every changed file. Then commit the complete validated change.

Recommended format:

```text
PASS31.xx: concise description of the coherent change
```

A commit is not a substitute for documentation. A document update is not a substitute for a commit. Both are required.

## 8. Work-in-progress rule

If the user explicitly requests a work-in-progress state, an AI may leave changes uncommitted, but it must clearly identify the uncommitted state and list the remaining validation/documentation work. Otherwise completed work must end at a clean Git checkpoint.

## 9. No history destruction

Never delete `.git`, reinitialize the repository, rewrite history, or force-reset a user's work merely to simplify a task. Inspect first. Preserve existing checkpoints.
