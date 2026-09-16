# Release Process

## Required gate

A PASS release requires:

- known-good Git baseline;
- modular, readable, standardized implementation;
- relevant architecture/data/feature documentation updated;
- ADR updated or added for architectural decisions;
- PASS release note updated;
- applicable regression tests passing;
- JavaScript syntax validation;
- JSON validation;
- source-precedence and provenance checks;
- no Ragger production data or references;
- map-boundary integrity;
- release/catalog/service-worker metadata consistency;
- clean Git diff and validated commit;
- fresh extraction and revalidation;
- Firefox/Android smoke testing when runtime behavior is involved;
- minimum 96% confidence before delivering a replacement ZIP.

## Archive roles

The PWA archive contains the deployable `site/` artifact. The SOURCE archive contains the complete development project, including Git history, documentation, tests, pipelines, scripts, and the PWA source.

A SOURCE archive for this project intentionally contains `.git/` because Git is part of the requested development checkpoint system. The `.git` directory must not be manually edited.
