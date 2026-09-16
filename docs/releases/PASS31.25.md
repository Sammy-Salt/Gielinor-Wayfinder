# PASS31.25 — Shell Bootstrap Parity

## Purpose
Eliminate the remaining Character/Crafting disappearance by making the application-tools markup static and identical across the shell, matching the working Items detail-page architecture.

## Root-cause direction
PASS31.24 isolated application tools from `#site-nav`, but the tools themselves were still created dynamically. PASS31.25 removes that runtime DOM-creation dependency. Every shell page now ships the same static navigation and static application-tools markup; JavaScript enhances and binds existing elements only.

## Changes
- Static `#app-tools` markup is present under `#app-tools-host` on every shell page.
- `app-enhancer.js` no longer creates the application-tools DOM.
- Search behavior binds to existing controls.
- Player import/export and install behavior bind to existing controls.
- Item detail uses the same static shell structure as normal pages.
- `item.js` cache/version reference standardized.
- Loader/build version advanced to 39.
- Service-worker namespace advanced to PASS31.25.
- Regression coverage verifies one navigation, one tools host, one tools component, and persistent Character/Crafting links.
- Documentation and compatibility tests updated for the new release baseline.

## Validation
- 21 shell pages audited.
- JavaScript syntax checks passed.
- PASS31.18–PASS31.24 compatibility suites passed after updating their current-release compatibility baseline.
- PASS31.25 shell/static-tools regression passed.
- JSON validation passed.
- Ragger production scan remains clean.

## Manual validation required
Firefox/Android PWA behavior must still be smoke-tested because the available automated browser environment cannot reliably exercise the local PWA origin.
